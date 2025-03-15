

import sys
from pyspark.sql import SparkSession
import pandas as pd
import re
from datetime import datetime

#levantamos spark
spark = SparkSession.builder.appName("Process Logs Analysis").getOrCreate()

# ruta al archivo, 
#para probar, la vamos a pasar como parámetro
# dentro del contenedor de spark
log_file = sys.argv[1] #parámetro

# expresion para parsear el log
log_pattern = r'(\S+) \S+ \S+ \[([^\]]+)\] "([A-Za-z]+ [^"]+)" (\d{3}) (\d+|-) "([^"]*)" "([^"]*)"'

#funcion para parsear
def parse_log_line(line):
    try:
        match = re.match(log_pattern, line)
        if match:
            ip, timestamp, request, status, size, referer, user_agent = match.groups()
            method, url = request.split(" ", 1) if " " in request else (request, "")
            return (ip, timestamp, method, url, int(status), int(size) if size != "-" else 0, referer, user_agent)
        else:
            return None
    except Exception as e:
        print(f"Error parseando linea: {line}. Error: {e}")
        return None

# leer el log como texto
try:
    # leemos el log como texto
    df = spark.read.text(log_file)

    # parsear y filtrar lo fallido
    parsed_rdd = df.rdd.map(lambda x: parse_log_line(x[0])).filter(lambda x: x is not None)

    #convertimos a DataFrame de spark con columnas
    columns = ["ip", "timestamp", "method", "url", "status", "size", "referer", "user_agent"]
    parsed_df = spark.createDataFrame(parsed_rdd, columns)

    # guardamos elcontenido como csv
    csv_path = "/data/full_access_log.csv"
    parsed_df.write.csv(csv_path, header=True, mode="overwrite")

    # hacemos conteo de códigos
    status_count = (parsed_df.groupBy("status")
                    .agg({"status": "count"})
                    .withColumnRenamed("count(status)", "Count")
                    .orderBy("Count", ascending=False))
    # calcular el total
    total_records = parsed_df.count()

    # obtenemos el timestamp y la url más frecuente
    status_details = (parsed_df.groupBy("status")
                      .agg({"timestamp": "min", "url": "first"})
                      .withColumnRenamed("min(timestamp)", "Timestamp")
                      .withColumnRenamed("first(url)", "URL")
                    )
    # unimos conteos con detalles
    union_df = status_count.join(status_details, "status").select(
        "status", "Timestamp", "URL", "Count"
    )

    #calcular porcentaje y marcar códigos críticos
    critical_codes = [404, 500, 502, 504]
    union_df_pd = union_df.toPandas() #pasamos a pandas
    union_df_pd["Percentage"] = (union_df_pd["Count"] / total_records * 100).round(2).astype(str) + "%"
    union_df_pd["Critical"] = union_df_pd["status"].apply(lambda x: "Yes" if int(x) in critical_codes else "No")

    # guardamos el csv listo para el análisis
    status_csv_path = "/data/status_code.csv"
    union_df_pd.to_csv(status_csv_path, index=False)
except Exception as e:
    print(f"Error en el procesamiento: {e}")
    raise

finally:
    #paramos spark
    spark.stop()


