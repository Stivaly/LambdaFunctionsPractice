# 10:00 – 17:00 · Etapa 3 — Apache Hive (Data Warehouse y consultas)

## Tarjeta de transición

**Slide 5** de `ES3_Retail_Transiciones.pptx`: mostrar 3–5 s al iniciar la etapa. El texto de la slide es este:

```text
Etapa 3 · Apache Hive
Data warehouse retail_dw sobre los datos limpios de Pig
Tablas externas + tabla administrada · JOIN · GROUP BY
```

## DDL — guardar como `scripts/retail_dw.hql`

```sql
-- retail_dw.hql · ES3 Retail Inteligente · crea el DW sobre las salidas de Pig
CREATE DATABASE IF NOT EXISTS retail_dw COMMENT 'DW Retail Inteligente - ES3 TI2081';
USE retail_dw;

-- Tablas EXTERNAS: Hive solo registra el esquema; los datos siguen en /retail/clean (escritos por Pig)
DROP TABLE IF EXISTS ventas_limpias;
CREATE EXTERNAL TABLE ventas_limpias (
  venta_id    STRING,
  fecha       DATE,
  cliente_id  STRING,
  producto_id STRING,
  region_raw  STRING,
  region      STRING,
  cantidad    INT,
  monto_clp   BIGINT
)
COMMENT 'Ventas validas y normalizadas por Pig'
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/retail/clean/ventas_limpias';

DROP TABLE IF EXISTS dim_clientes;
CREATE EXTERNAL TABLE dim_clientes (
  cliente_id      STRING,
  nombre_ficticio STRING,
  region          STRING,
  segmento        STRING
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/retail/clean/dim_clientes';

DROP TABLE IF EXISTS dim_productos;
CREATE EXTERNAL TABLE dim_productos (
  producto_id           STRING,
  producto              STRING,
  categoria             STRING,
  precio_referencia_clp INT
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/retail/clean/dim_productos';

-- Tabla ADMINISTRADA (managed) en formato columnar ORC: hecho de ventas enriquecido con las dimensiones
DROP TABLE IF EXISTS ventas_enriquecidas;
CREATE TABLE ventas_enriquecidas STORED AS ORC AS
SELECT v.venta_id, v.fecha, v.cliente_id, c.segmento, v.region,
       v.producto_id, p.producto, p.categoria, v.cantidad, v.monto_clp
FROM ventas_limpias v
JOIN dim_clientes  c ON v.cliente_id  = c.cliente_id
JOIN dim_productos p ON v.producto_id = p.producto_id;

SHOW TABLES;
```

## Consultas — guardar como `scripts/consultas.hql`

```sql
-- consultas.hql · ES3 Retail Inteligente
USE retail_dw;
SET hive.cli.print.header=true;

-- Q0. Control de trazabilidad con Pig: deben ser 174 filas
SELECT COUNT(*) AS filas, SUM(monto_clp) AS total_clp FROM ventas_limpias;

-- Q1. Total vendido por región
SELECT region,
       COUNT(*)        AS num_ventas,
       SUM(cantidad)   AS unidades,
       SUM(monto_clp)  AS total_clp,
       ROUND(100 * SUM(monto_clp) / SUM(SUM(monto_clp)) OVER (), 1) AS pct
FROM ventas_limpias
GROUP BY region
ORDER BY total_clp DESC;

-- Q2. Total por categoría (JOIN con dim_productos)
SELECT p.categoria,
       COUNT(*)          AS num_ventas,
       SUM(v.cantidad)   AS unidades,
       SUM(v.monto_clp)  AS total_clp,
       ROUND(100 * SUM(v.monto_clp) / SUM(SUM(v.monto_clp)) OVER (), 1) AS pct
FROM ventas_limpias v
JOIN dim_productos p ON v.producto_id = p.producto_id
GROUP BY p.categoria
ORDER BY total_clp DESC;

-- Q3. Top 3 productos por facturación (JOIN + agregación)
SELECT p.producto_id, p.producto, p.categoria,
       SUM(v.cantidad)  AS unidades,
       SUM(v.monto_clp) AS facturacion_clp
FROM ventas_limpias v
JOIN dim_productos p ON v.producto_id = p.producto_id
GROUP BY p.producto_id, p.producto, p.categoria
ORDER BY facturacion_clp DESC
LIMIT 3;

-- Q4 (extra). Productos del catálogo sin ninguna venta (LEFT JOIN)
SELECT p.producto_id, p.producto, p.categoria
FROM dim_productos p
LEFT JOIN ventas_limpias v ON p.producto_id = v.producto_id
WHERE v.venta_id IS NULL;

-- Q5 (extra). Ventas por segmento de cliente, desde la tabla administrada ORC
SELECT segmento, COUNT(*) AS num_ventas, SUM(monto_clp) AS total_clp
FROM ventas_enriquecidas
GROUP BY segmento
ORDER BY total_clp DESC;

-- Q6. Actividad de los clientes que se cargarán en HBase (fuente coherente para la Etapa 4)
SELECT cliente_id, COUNT(*) AS num_compras, SUM(monto_clp) AS monto_total_clp
FROM ventas_limpias
WHERE cliente_id IN ('C001','C002','C003','C005')
GROUP BY cliente_id
ORDER BY cliente_id;
```

---

> **Importante (Derby):** ejecuta siempre `hive` desde `~/retail_es3`, el directorio donde está `metastore_db`.

## Paso 1 — Crear la base y las tablas (≈1:30)

```bash
cd ~/retail_es3
cat scripts/retail_dw.hql
hive -f scripts/retail_dw.hql 2>&1 | tee resultados/hive_ddl.log
```

> Creo la base `retail_dw`. Las tres tablas de origen son **externas**: Hive solo guarda el esquema en su metastore y apunta a las carpetas que generó Pig en `/retail/clean`. Así el flujo Pig → Hive es trazable: Hive lee exactamente lo que Pig escribió, sin copiar ni recalcular nada.

> Además creo una tabla **administrada**, `ventas_enriquecidas`, en formato ORC, que une las ventas con las dimensiones de cliente y producto. Esta es la tabla de hechos del data warehouse.

## Paso 2 — Ubicación en HDFS y metadatos (≈1:30)

```bash
hive -e "USE retail_dw; DESCRIBE FORMATTED ventas_limpias;" 2>/dev/null | grep -E "col_name|venta_id|monto_clp|Location|Table Type|SerDe Library|field.delim"
hive -e "USE retail_dw; DESCRIBE FORMATTED ventas_enriquecidas;" 2>/dev/null | grep -E "Location|Table Type|InputFormat|numRows"
hdfs dfs -ls /retail/clean/ventas_limpias
hdfs dfs -ls /user/hive/warehouse/retail_dw.db/ventas_enriquecidas
```

> Aquí se ve la diferencia entre el rol **lógico** y el **físico** del data warehouse. Lo lógico es el esquema: columnas, tipos y tipo de tabla, guardados en el metastore de Hive. Lo físico son los archivos en HDFS.

> `ventas_limpias` es `EXTERNAL_TABLE` y su `Location` es `/retail/clean/ventas_limpias`: el archivo `part-...` que escribió Pig. Si borro esta tabla, los datos se conservan.

> `ventas_enriquecidas` es `MANAGED_TABLE`: Hive es dueño de sus datos, que están en el warehouse, `/user/hive/warehouse/retail_dw.db`, en formato ORC. Si la borro, Hive borra también los archivos.

## Paso 3 — Ejecutar las consultas (≈3:00)

Opción A (todo de una vez, salida a archivo de evidencia):
```bash
hive -f scripts/consultas.hql 2>/dev/null | tee resultados/hive_consultas.txt
```

Opción B (más didáctica para el video): abrir `hive` y pegar cada consulta, una a la vez.
```bash
hive
```

> **Q0, control:** Hive cuenta 174 filas, las mismas 174 que dejó Pig. El total vendido válido es 59.910.000 pesos.

> **Q1, por región:** agrupo con `GROUP BY region`. Santiago lidera con 18.371.000 pesos, el 30,7 %, seguido de Valparaíso, La Serena y Concepción. Gracias a la normalización de Pig aparecen exactamente cuatro regiones; sin ella, Santiago estaría repartido en tres grupos: "Santiago", "SANTIAGO" y "Stgo.".

> **Q2, por categoría:** hago un JOIN con la dimensión productos para obtener la categoría. Tecnología concentra 36.850.000 pesos, el 61,5 % de las ventas.

> **Q3, top 3 productos:** JOIN y agregación por producto, ordenado por facturación. Primero está el Notebook con 34.500.000, luego la Bicicleta con 14.000.000 y la Aspiradora con 4.560.000.

> **Q4:** con un LEFT JOIN encuentro productos del catálogo que no tienen ninguna venta: la Cafetera y las Mancuernas.

## Paso 4 — Explicar 2 resultados (≈1:00)

> **Resultado 1:** Tecnología representa el 61,5 % de la facturación, pero casi todo viene de un solo producto: el Notebook, con 34,5 millones de los 59,9 millones totales, es decir, el 57,6 % de todas las ventas. Mouse y Teclado juntos suman apenas 2,35 millones. El negocio depende fuertemente de un producto de alto precio: vendió 50 unidades a 690.000 pesos, que es su precio de referencia.

> **Resultado 2:** Concepción tiene 44 ventas, más que La Serena con 43 y Valparaíso con 41, pero es la región con menor facturación: 11.820.000 pesos. Su ticket promedio es cerca de 268.600 pesos, contra unos 399.400 en Santiago. El problema en Concepción no es la cantidad de ventas sino el valor de lo que se vende: ahí hay una oportunidad para promover productos de mayor valor.

(Ticket promedio = total / num_ventas; puedes mostrarlo con: `SELECT region, ROUND(SUM(monto_clp)/COUNT(*)) FROM ventas_limpias GROUP BY region;`)

## Paso 5 — Puente hacia HBase (≈30 s)

> La consulta Q6 obtiene el número de compras y el monto total de cuatro clientes. Estos valores los voy a cargar en HBase en la familia `actividad`, para que los perfiles salgan de datos reales del mismo negocio.

---

## Qué debe verse

**Q0**
| filas | total_clp |
|---|---|
| 174 | 59910000 |

**Q1 — por región**
| region | num_ventas | unidades | total_clp | pct |
|---|---|---|---|---|
| Santiago | 46 | 96 | 18371000 | 30.7 |
| Valparaiso | 41 | 85 | 15695000 | 26.2 |
| La Serena | 43 | 83 | 14024000 | 23.4 |
| Concepcion | 44 | 84 | 11820000 | 19.7 |

**Q2 — por categoría**
| categoria | num_ventas | unidades | total_clp | pct |
|---|---|---|---|---|
| Tecnologia | 75 | 150 | 36850000 | 61.5 |
| Deportes | 50 | 100 | 17400000 | 29.0 |
| Hogar | 49 | 98 | 5660000 | 9.4 |

**Q3 — top 3 productos**
| producto_id | producto | categoria | unidades | facturacion_clp |
|---|---|---|---|---|
| P001 | Notebook | Tecnologia | 50 | 34500000 |
| P007 | Bicicleta | Deportes | 50 | 14000000 |
| P004 | Aspiradora | Hogar | 48 | 4560000 |

**Q4 — sin ventas:** P005 Cafetera (Hogar), P009 Mancuernas (Deportes)

**Q5 — por segmento**
| segmento | num_ventas | total_clp |
|---|---|---|
| Plus | 58 | 21052000 |
| Basico | 58 | 20549000 |
| Premium | 58 | 18309000 |

**Q6 — para HBase**
| cliente_id | num_compras | monto_total_clp |
|---|---|---|
| C001 | 5 | 1296000 |
| C002 | 6 | 689000 |
| C003 | 5 | 485000 |
| C005 | 6 | 4977000 |

## Checklist de rúbrica

- [x] Criterio 4 — base `retail_dw`, tablas de ventas, clientes y productos, ubicación en HDFS, metadatos, JOIN + GROUP BY, región/categoría/top 3, 2 resultados explicados con cifras.
- [x] Criterio 8 — rol físico vs lógico; tabla externa vs administrada.
- [x] Criterio 1 — Q0 demuestra la trazabilidad Pig → Hive (174 = 174).
