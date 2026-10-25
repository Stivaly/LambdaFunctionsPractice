# ES3 Big Data (TI2081) — Retail Inteligente

Proyecto integrador: **HDFS → Pig → Hive**, más dos ramas de uso sobre el mismo negocio: **HBase** (perfiles por RowKey) y **Mahout** (recomendaciones).

Este directorio contiene el guion completo del video (transiciones + narración + comandos) y sirve también como README de entrega.

## Índice de archivos

| Archivo | Uso | Tiempo en video |
|---|---|---|
| [00_guion_y_tiempos.md](00_guion_y_tiempos.md) | Estructura del video, tiempos, checklist de grabación | — |
| [00_preparacion_ambiente.md](00_preparacion_ambiente.md) | Instalación/arranque con JDK 8 en Zorin OS (antes de grabar) | — |
| [01_intro.md](01_intro.md) | Identificación y presentación del caso | ~1:00 |
| [02_hdfs.md](02_hdfs.md) | Etapa 1 — Hadoop / HDFS | ~3:00 |
| [03_pig.md](03_pig.md) | Etapa 2 — Apache Pig (ETL) | ~6:00 |
| [04_hive.md](04_hive.md) | Etapa 3 — Apache Hive (DW y consultas) | ~7:00 |
| [05_hbase.md](05_hbase.md) | Etapa 4 — Apache HBase (CRUD por RowKey) | ~5:00 |
| [06_mahout.md](06_mahout.md) | Etapa 5 — Apache Mahout (recomendaciones) | ~5:00 |
| [07_cierre.md](07_cierre.md) | Diagrama, comparación de herramientas, resultado y limitación | ~3:00 |
| [08_problemas_y_verificacion.md](08_problemas_y_verificacion.md) | Problemas encontrados/soluciones y verificaciones cruzadas | se usa dentro de las etapas |
| [09_resultados_resumidos.md](09_resultados_resumidos.md) | Archivo de resultados resumidos (entregable) | — |

## Versiones de herramientas (compatibles con JDK 8)

> Completa la columna "Instalada" con la salida real de los comandos de verificación. La columna "Recomendada" es la combinación probada habitualmente con Java 8.

| Herramienta | Recomendada (JDK 8) | Instalada | Comando para verificar |
|---|---|---|---|
| Java | OpenJDK 1.8.0_xxx | `[COMPLETAR]` | `java -version` |
| Hadoop (HDFS + YARN) | 3.3.6 (o 3.2.x / 2.10.x) | `[COMPLETAR]` | `hadoop version` |
| Apache Pig | 0.17.0 | `[COMPLETAR]` | `pig -version` |
| Apache Hive | 3.1.3 (o 2.3.9 con Hadoop 2.x) | `[COMPLETAR]` | `hive --version` |
| Apache HBase | 2.4.x / 2.5.x | `[COMPLETAR]` | `hbase version` |
| Apache Mahout | 0.13.0 (MapReduce + Taste) | `[COMPLETAR]` | `ls $MAHOUT_HOME/*.jar` |
| Sistema operativo | Zorin OS (base Ubuntu) | `[COMPLETAR]` | `cat /etc/os-release` |

**Por qué Mahout 0.13.0:** es la última versión que trae los algoritmos MapReduce (`recommenditembased`, `itemsimilarity`, `kmeans`) y la librería Taste, compilados para Java 7/8. Las versiones 14.x eliminaron esos comandos y requieren Java 11+ / Spark.

## Estructura local del proyecto

```text
~/retail_es3/
├── datos/                       # contenido del zip ES3_BigData_Datos_Retail.zip (sin modificar)
│   ├── ventas_raw.csv
│   ├── dim_clientes.csv
│   ├── dim_productos.csv
│   ├── interacciones_cliente_producto.csv
│   └── README_DATOS.txt
├── scripts/
│   ├── etl_ventas.pig           # Etapa 2 (ver 03_pig.md)
│   ├── limpieza_dimensiones.pig # Etapa 2 (ver 03_pig.md)
│   ├── retail_dw.hql            # Etapa 3 DDL (ver 04_hive.md)
│   ├── consultas.hql            # Etapa 3 consultas (ver 04_hive.md)
│   ├── hbase_perfiles.txt       # Etapa 4 (ver 05_hbase.md)
│   ├── prep_mahout.pig          # Etapa 5 (ver 06_mahout.md)
│   ├── mahout_recomendar.sh     # Etapa 5 (ver 06_mahout.md)
│   └── RecomendadorRetail.java  # Etapa 5, plan B (ver 06_mahout.md)
└── resultados/                  # salidas reales copiadas desde HDFS para la entrega
```

Cada bloque de código de los `.md` indica el nombre de archivo en el que debe guardarse.

## Rutas HDFS utilizadas

| Ruta | Contenido | Quién la escribe |
|---|---|---|
| `/retail/raw/ventas/ventas_raw.csv` | Ventas originales (180 filas) | `hdfs dfs -put` |
| `/retail/raw/clientes/dim_clientes.csv` | Dimensión clientes (30) | `hdfs dfs -put` |
| `/retail/raw/productos/dim_productos.csv` | Dimensión productos (9) | `hdfs dfs -put` |
| `/retail/raw/interacciones/interacciones_cliente_producto.csv` | Interacciones (174) | `hdfs dfs -put` |
| `/retail/clean/ventas_limpias/` | Ventas válidas y normalizadas (174) | Pig |
| `/retail/clean/ventas_descartadas/` | Ventas con monto ≤ 0 (6) — trazabilidad | Pig |
| `/retail/clean/conteos_etl/` | Conteos entrada/salida/descartadas | Pig |
| `/retail/clean/mapeo_regiones/` | Tabla región original → oficial | Pig |
| `/retail/clean/dim_clientes/`, `/retail/clean/dim_productos/` | Dimensiones sin encabezado ni `\r` | Pig |
| `/user/hive/warehouse/retail_dw.db/` | Tabla administrada `ventas_enriquecidas` (ORC) | Hive |
| `/hbase/data/default/perfiles_cliente/` | Almacenamiento físico de la tabla HBase | HBase |
| `/retail/mahout/input/` | Tripletas `usuario,item,preferencia` numéricas | Pig |
| `/retail/mahout/output/` | Recomendaciones | Mahout |

## Instrucciones reproducibles (resumen)

```bash
# 0. Servicios arriba (ver 00_preparacion_ambiente.md)
start-dfs.sh && start-yarn.sh && mapred --daemon start historyserver
start-hbase.sh

# 1. HDFS (detalle en 02_hdfs.md)
hdfs dfs -mkdir -p /retail/raw/{ventas,clientes,productos,interacciones} /retail/clean
hdfs dfs -put datos/ventas_raw.csv /retail/raw/ventas/
hdfs dfs -put datos/dim_clientes.csv /retail/raw/clientes/
hdfs dfs -put datos/dim_productos.csv /retail/raw/productos/
hdfs dfs -put datos/interacciones_cliente_producto.csv /retail/raw/interacciones/

# 2. Pig
pig -x mapreduce scripts/etl_ventas.pig
pig -x mapreduce scripts/limpieza_dimensiones.pig

# 3. Hive
hive -f scripts/retail_dw.hql
hive -f scripts/consultas.hql

# 4. HBase
hbase shell -n scripts/hbase_perfiles.txt     # o paso a paso en la shell

# 5. Mahout
pig -x mapreduce scripts/prep_mahout.pig
bash scripts/mahout_recomendar.sh
```

## Datos

Datos ficticios/sintéticos entregados por el docente. No contienen RUT, teléfonos ni emails. Los CSV **no se editan a mano**: toda limpieza ocurre en Pig.

## Declaración de recursos utilizados

- Documentación oficial de Apache Hadoop, Pig, Hive, HBase y Mahout.
- `[COMPLETAR: material docente / otros recursos autorizados]`
