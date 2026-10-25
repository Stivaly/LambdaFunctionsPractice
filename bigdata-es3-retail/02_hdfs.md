# 01:00 – 04:00 · Etapa 1 — Hadoop / HDFS

## Tarjeta de transición

```text
Etapa 1 · Hadoop / HDFS
Almacenamiento distribuido de los datos originales
/retail/raw  →  /retail/clean
```

## Paso 1 — HDFS operativo (≈30 s)

> Primero compruebo que Hadoop está operativo. Con `jps` veo los procesos de Java: el NameNode, que guarda los metadatos del sistema de archivos, el DataNode, que guarda los bloques físicos, y en YARN el ResourceManager y NodeManager, que ejecutarán los trabajos MapReduce de Pig, Hive y Mahout.

```bash
jps
hadoop version | head -1
hdfs dfsadmin -report | head -20
```

> El reporte muestra un DataNode vivo y la capacidad disponible. Trabajo en modo pseudo-distribuido, con replicación 1, porque es una sola máquina.

## Paso 2 — Crear rutas raw y clean (≈30 s)

> Creo la estructura del proyecto: `/retail/raw` para los datos originales tal como llegan, y `/retail/clean` para lo que genere Pig. Dentro de raw separo un directorio por archivo, porque Hive lee **directorios**, no archivos sueltos.

```bash
hdfs dfs -mkdir -p /retail/raw/ventas /retail/raw/clientes /retail/raw/productos /retail/raw/interacciones
hdfs dfs -mkdir -p /retail/clean
hdfs dfs -ls /retail
```

## Paso 3 — Subir los archivos provistos (≈40 s)

> Subo los cuatro CSV entregados, sin modificarlos.

```bash
cd ~/retail_es3/datos
hdfs dfs -put ventas_raw.csv                      /retail/raw/ventas/
hdfs dfs -put dim_clientes.csv                    /retail/raw/clientes/
hdfs dfs -put dim_productos.csv                   /retail/raw/productos/
hdfs dfs -put interacciones_cliente_producto.csv  /retail/raw/interacciones/
hdfs dfs -ls -R /retail
```

> En el listado se ven los permisos, el dueño, el factor de replicación, que es 1, y el tamaño de cada archivo. Los archivos son de mi usuario con permisos de lectura y escritura para mí y solo lectura para el resto, que es lo adecuado para datos originales.

## Paso 4 — Lectura parcial (≈30 s)

```bash
hdfs dfs -cat /retail/raw/ventas/ventas_raw.csv | head -8
hdfs dfs -cat /retail/raw/ventas/ventas_raw.csv | wc -l
hdfs dfs -cat /retail/raw/ventas/ventas_raw.csv | cut -d, -f5 | sort | uniq -c
```

> Leo las primeras líneas desde HDFS. El archivo tiene 181 líneas: un encabezado y 180 ventas. Al contar la columna `region_raw` aparecen **doce variantes** para solo cuatro regiones: por ejemplo "Stgo.", "SANTIAGO" y "Santiago" son la misma región. Esto es lo que Pig tiene que estandarizar.

## Paso 5 — Almacenamiento físico (≈40 s)

> HDFS es un sistema de archivos lógico: la ruta `/retail/raw/ventas/ventas_raw.csv` existe en el NameNode, pero físicamente el archivo se guarda como **bloques** en el disco local del DataNode. Lo compruebo con `fsck`.

```bash
hdfs fsck /retail/raw/ventas/ventas_raw.csv -files -blocks -locations
hdfs getconf -confKey dfs.datanode.data.dir
find ~/hadoop_data/datanode -name "blk_*" ! -name "*.meta" | head
```

> `fsck` muestra que el archivo ocupa un bloque, con su identificador `blk_...`, y la ubicación del DataNode. Ese bloque es un archivo real en el directorio configurado en `dfs.datanode.data.dir`, dentro de mi disco.

Opcional (si queda tiempo), demostrar que el bloque es el archivo:

```bash
BLK=$(hdfs fsck /retail/raw/ventas/ventas_raw.csv -files -blocks | grep -o 'blk_[0-9]*' | head -1)
head -3 $(find ~/hadoop_data/datanode -name "$BLK")
```

## Qué debe verse

| Comprobación | Valor esperado |
|---|---|
| `wc -l` ventas_raw | 181 (1 encabezado + 180 ventas) |
| Variantes de `region_raw` | 12 (CONCEPCION, Conce., Concepcion, LA SERENA, La Serena, Serena, SANTIAGO, Santiago, Stgo., VALPARAISO, Valparaiso, Valpo.) |
| Bloques por archivo | 1 (archivos de pocos KB, bloque de 128 MB) |
| Replicación | 1 |

## Checklist de rúbrica

- [x] Criterio 2 — rutas RAW y CLEAN, carga, `ls`, lectura parcial, permisos.
- [x] Criterio 8 — rol físico (bloques en DataNode) vs lógico (ruta en NameNode).
