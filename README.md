**Proyecto: Procesamiento de Logs con Apache Airflow y Spark
¡Bienvenido al repositorio de mi proyecto "Procesamiento de Logs con Apache Airflow y Spark"! 
Este proyecto es una solución end-to-end para procesar y analizar archivos de logs a gran escala, utilizando tecnologías modernas de orquestación (Airflow) 
y procesamiento distribuido (Spark). 
Está diseñado para demostrar habilidades técnicas avanzadas, resolución de problemas y capacidad para trabajar con big data en un entorno de contenedores Docker. 

📋 Descripción General
Este proyecto automatiza el procesamiento de un archivo de logs (access.log, el mismo es muy pesado para adjuntarlo en el repo, por lo que tuve que adjuntar el link de descarga del mismo)
utilizando Apache Spark para análisis distribuidos y Apache Airflow para la orquestación de tareas. El flujo completo incluye:

Lectura y transformación de logs con Spark.
Generación de un informe con estadísticas (códigos de estado, errores críticos, etc.).
Envío de un email con el informe y los datos procesados. Todo esto se ejecuta en un entorno Dockerizado, lo que asegura portabilidad y escalabilidad.
🎯 Objetivo
Demostrar la integración de herramientas de big data (Spark) y orquestación (Airflow).
Automatizar el análisis de logs para identificar patrones y anomalías.
Crear un pipeline reproducible para uso en entornos reales o pruebas técnicas.

🛠 Tecnologías Utilizadas
Apache Airflow	Orquestador de workflows para automatizar tareas.
Apache Spark	Motor de procesamiento distribuido para big data.
Docker	Contenedorización para entornos consistentes.
Python	Lenguaje principal para scripts y análisis.
Pandas	Análisis de datos y visualización en reportes.
GitHub	Control de versiones y despliegue del código.
PostgreSQL	Base de datos para metadatos de Airflow (opcional).

🚀 Flujo End-to-End del Proyecto
Ingestión de Datos:
Se parte de un archivo access.log que simula logs de un servidor web.
Este archivo se monta en un volumen Docker para ser accesible por Spark.
Procesamiento con Spark:
Un script Python (process_logs_spark.py) usa Spark para leer el access.log, particionarlo, y generar un archivo status_codes.csv con estadísticas (códigos de estado, conteos, etc.).
Ejecución dentro de un contenedor Spark via docker exec -it.
Orquestación con Airflow:
Un DAG (process_logs_dag.py) define dos tareas:
run_spark_script: Ejecuta el script de Spark.
generate_and_send_report: Genera un informe y lo envía por email.
Airflow gestiona la ejecución, dependencias y reintentos.
Generación y Envío de Reportes:
La tarea generate_and_send_report lee status_codes.csv, analiza datos (códigos críticos, picos de errores), y envía un email con el informe y el archivo adjunto usando SMTP.
Despliegue:
Todo se ejecuta en un entorno Docker compuesto por servicios (Airflow, Spark, Postgres).
Se parte de dos archivos dockerfile-airflow/spark y luego un yaml, para levantar los servicios de airflow.
El proyecto se inicia con docker-compose up -d --build(creando las imágenes y levantando los contenedores).

💡 Inconvenientes Potenciales y Soluciones
Inconveniente	Causa	Solución
Archivos grandes en GitHub	Logs o resultados superan 100 MB.	Usar .gitignore para excluir data/ y limpiar el historial con git filter-branch.
Errores de email (SMTP)	Credenciales inválidas o puerto incorrecto.	Verificar .env con contraseña de aplicación de Gmail y puerto 587.
Rutas de archivos inconsistentes	Diferencias entre contenedores.	Asegurar que volúmenes Docker mapeen correctamente (ej. ./data:/opt/airflow/data).
Fallo en Spark	Configuración de Java o Spark mal definida.	Verificar JAVA_HOME y SPARK_HOME en el contenedor.
Ejecutar docker exec -it directamente desde el contenedor de airflow, asegurarse de añadir socket de docker en contenedores webserver y scheduler.

🌟 Habilidades Desarrolladas
Desarrollo: Integración de Airflow, Spark y Docker.
Resolución de problemas: Manejo de errores de tamaño de archivos, rutas y autenticación.
Automatización: Pipelines de datos end-to-end.

📬 Contacto
GitHub: Mercado-tomas
Email: tomasfmercado@gmail.com
¡Estoy abierto a oportunidades y colaboraciones!
