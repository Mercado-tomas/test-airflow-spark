##importaciones 

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import date, datetime, timedelta
import pandas as pd
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# argumentos por defecto del dag
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2025, 3, 14) #ajustar la fecha de inicio
}

# definimos el dag
with DAG(
    'process_logs_dag', #id dag
    default_args=default_args,
    description='Procesar logs con Spark y enviar informe por email.',
    schedule_interval=None, #correría diariamente -> timedelta(days=1),
    catchup=False, #evita ejecuciones retroactivas
    tags=['logs', 'spark']
) as dag:
    # tarea 1, ejecutar el script de spark
    spark_task=BashOperator(
        task_id='run_spark_script',
        # dentro del contenedor, ejectumos spark-submit
        bash_command='docker exec spark_container /opt/bitnami/spark/bin/spark-submit /data/process_logs_spark.py /data/access.log',
        dag=dag
    )

    # función para hacer el informe ymandar el email
    def generate_and_send_report():
        #ruta al csv generado por spark
        csv_path = "/opt/airflow/data/status_code.csv"
        # validamos que el archivo exista
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"El archivo, {csv_path}, no se encontró.")
        # leemos el csv
        df = pd.read_csv(csv_path)

        # análisis
        total_records = df['Count'].sum()
        critical_codes = df[df['Critical'] == 'Yes']
        top_critical = critical_codes.sort_values('Count', ascending=False).head(3)
        peak_critical_time = df[df['Critical'] == 'Yes']['Timestamp'].iloc[0]

        # generamos el reporte
        report = f"""
        **Informe de Análisis de Logs - {datetime.now().strftime('%Y-%m-%d %h:%M:%S')}**
        
        - Total de registros procesados: {total_records}
        - Códigos críticos detectados:
          {critical_codes.to_string(index=False)}
        - Top 3 códigos críticos por cantidad:
          {top_critical.to_string(index=False)}
        - Pico de errores críticos: {peak_critical_time}
        - Archivo adjunto: status_codes.csv con detalles completos.

        Este informe se generó automaticamente con Airflow.
        """

        # configuración de email desde variables de entorno.
        smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', 587))
        smtp_user = os.environ.get('SMTP_USER', 'default_user@gmail.com')
        smtp_password = os.environ.get('SMTP_PASSWORD', 'default_password')
        email_from = os.environ.get('EMAIL_FROM', 'default_user@gmail.com')
        email_to = os.environ.get('EMAIL_TO', 'default_user@gmail.com').split(',')

        # crear mensaje
        msg = MIMEMultipart()
        msg['From'] = email_from
        msg['To'] = ', '.join(email_to)
        msg['Subject'] = 'Informe de Análisis de Logs desde Airflow'
        msg.attach(MIMEText(report, 'plain'))

        # adjuntamos el csv al email
        with open(csv_path, 'rb') as f:
            attachment = MIMEApplication(f.read(), Name=os.path.basename(csv_path))
            attachment['Content-Disposition'] = f'attachment; filename={os.path.basename(csv_path)}'
            msg.attach(attachment)
        # enviamos el email
        try:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
        except Exception as e:
            raise Exception(f"Error enviando email: {e}")    

    # tarea 2, generamos el informe y enviamos el email
    report_task = PythonOperator(
        task_id = 'generate_and_send_report',
        python_callable=generate_and_send_report,
        dag=dag
        )
    
    # establecemos dependecias
    spark_task >> report_task




















