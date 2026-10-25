# Problemas, soluciones y verificaciones

El criterio 7 de la rúbrica (8 %) pide **al menos un problema y su solución** o un riesgo, más comprobaciones legibles. Los problemas 1 y 2 ocurren sí o sí con estos datos: nárralos en sus etapas.

## Problemas propios de los datos (mencionar en el video)

| # | Problema | Cómo se detecta | Solución aplicada | Etapa |
|---|---|---|---|---|
| 1 | Los CSV tienen fin de línea Windows (CRLF): cada línea termina en `\r` | `head -2 datos/ventas_raw.csv \| cat -A` muestra `^M$` | `TRIM()` en Pig antes de convertir a número; dimensiones limpiadas con Pig antes de Hive | Pig |
| 2 | 12 variantes de región para 4 regiones | `cut -d, -f5 \| sort \| uniq -c` | `CASE UPPER(region_raw)` + valor de control `SIN_REGION` | Pig |
| 3 | 6 ventas con monto negativo | `FILTER ... monto_clp <= 0` | Se excluyen pero se guardan en `ventas_descartadas` (trazabilidad) | Pig |
| 4 | Encabezado del CSV se lee como dato | Pig lee 181 registros | `FILTER venta_id != 'venta_id'` | Pig |
| 5 | 174 interacciones pero 159 pares únicos | `GROUP BY (user, item)` | Preferencia = suma de cantidades por par | Mahout |
| 6 | Mahout exige IDs numéricos | — | `C008 → 8`, `P006 → 6`, mapeo guardado en HDFS | Mahout |

Texto sugerido si quieres un bloque explícito de "problema/solución" (≈30 s, al final de Pig):

> Un problema de los datos: al revisar el archivo con `cat -A` se ve que cada línea termina con `^M`, el retorno de carro de Windows, que queda pegado al monto, la última columna. Si convierto el monto a número sin limpiarlo, Pig lo deja nulo y la venta se descartaría. La solución fue aplicar `TRIM` antes de convertir a número. No modifiqué el CSV: la corrección quedó en el script, así que es reproducible.

Para demostrarlo en vivo (opcional, ≈20 s), en `pig -x mapreduce` interactivo (grunt):

```pig
r = LOAD '/retail/raw/ventas/ventas_raw.csv' USING PigStorage(',') AS (id:chararray, f, c, p, reg, cant, monto:chararray);
s = FOREACH r GENERATE id, (long) monto AS sin_trim, (long) TRIM(monto) AS con_trim;
t = LIMIT s 3;
DUMP t;
```

Si en tu ambiente `sin_trim` sale vacío y `con_trim` con el número, ese es el problema demostrado. Si ambos salen bien (algunas versiones toleran el `\r`), narra el `TRIM` como medida preventiva, no como error encontrado.

## Problemas típicos del ambiente (JDK 8 / Zorin)

| Síntoma | Causa probable | Solución |
|---|---|---|
| `jps` no muestra `DataNode` | `clusterID` distinto tras reformatear el NameNode | `stop-dfs.sh`, borrar `~/hadoop_data/datanode/*`, `start-dfs.sh` (se pierden los datos de HDFS) |
| `Connection refused localhost:9000` | HDFS no arrancado | `start-dfs.sh`, verificar con `jps` |
| `Name node is in safe mode` | Recién arrancado | Esperar o `hdfs dfsadmin -safemode leave` |
| Pig: `ERROR 2997 ... Unable to recreate exception` o falla al leer contadores | JobHistory Server apagado | `mapred --daemon start historyserver` |
| Pig: `Output Location Validation Failed ... already exists` | Salida previa | El script usa `rmf`; o `hdfs dfs -rm -r /retail/clean/...` |
| Job MapReduce: `Could not find or load main class ...MRAppMaster` | Falta classpath en `mapred-site.xml` | Agregar `HADOOP_MAPRED_HOME` (ver `00_preparacion_ambiente.md`) |
| Hive 3.1.3: `NoSuchMethodError: com.google.common.base.Preconditions.checkArgument` | Guava de Hive (19) vs Hadoop 3 (27) | `rm $HIVE_HOME/lib/guava-19.0.jar` y `cp $HADOOP_HOME/share/hadoop/common/lib/guava-27.0-jre.jar $HIVE_HOME/lib/` |
| Hive: `Table not found` en otra sesión | Metastore Derby creado en otro directorio | Ejecutar `hive` siempre desde `~/retail_es3` |
| Hive: columnas en `NULL` | Separador o tipos distintos a la salida de Pig | Ver `hdfs dfs -cat .../part-* \| head`; separador `,` y 8 columnas |
| HBase: `ServerNotRunningYetException` / `PleaseHoldException` | HMaster arrancando | Esperar 20–30 s tras `start-hbase.sh` |
| HBase no arranca con Hadoop 3 (`StreamCapabilities`) | Chequeo de hflush | `hbase.unsafe.stream.capability.enforce=false` en `hbase-site.xml` |
| HBase: `KeeperErrorCode = ConnectionLoss` | ZooKeeper caído | `stop-hbase.sh`, revisar `hbase.zookeeper.property.dataDir`, `start-hbase.sh` |
| Mahout: `MAHOUT_LOCAL is not set; adding HADOOP_CONF_DIR` | Mensaje normal | Indica que corre sobre Hadoop (es buena evidencia) |
| Mahout falla en YARN con Hadoop 3 | Mahout 0.13 está compilado para Hadoop 2 | Plan B1 (`MAHOUT_LOCAL=true`) o B2 (API Taste), declararlo en el video |
| `Unsupported major.minor version 55.0` | Algún componente compilado para Java 11 | Usar las versiones de la tabla del README (todas para Java 8) |

## Verificaciones cruzadas (para mostrar o tener a mano)

| Verificación | Comando | Esperado |
|---|---|---|
| Entrada = salida + descartadas | `conteos_etl` | 180 = 174 + 6 |
| Pig → Hive sin pérdida | `SELECT COUNT(*) FROM ventas_limpias` | 174 |
| Solo 4 regiones | `SELECT DISTINCT region FROM ventas_limpias` | 4 filas |
| Total válido | `SELECT SUM(monto_clp) ...` | 59.910.000 |
| Suma de regiones = total | Q1 | 18.371.000 + 15.695.000 + 14.024.000 + 11.820.000 = 59.910.000 |
| Suma de categorías = total | Q2 | 36.850.000 + 17.400.000 + 5.660.000 = 59.910.000 |
| Coherencia de precios | Q3 | Notebook 50 × 690.000 = 34.500.000 |
| Región de venta = región del cliente | `SELECT COUNT(*) FROM ventas_enriquecidas e JOIN dim_clientes c ON e.cliente_id=c.cliente_id WHERE e.region <> c.region` | 0 (la normalización es consistente con la dimensión) |
| Interacciones = ventas válidas | — | Las 174 interacciones corresponden 1 a 1 a las 174 ventas válidas (cliente, producto, cantidad) |
| HBase usa clientes reales | `hdfs dfs -cat /retail/clean/dim_clientes/part-* \| grep -E "C00[1235],"` | 4 filas |
