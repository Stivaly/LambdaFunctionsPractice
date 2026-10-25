# 04:00 – 10:00 · Etapa 2 — Apache Pig (ETL)

## Tarjeta de transición

**Slide 4** de `ES3_Retail_Transiciones.pptx`: mostrar 3–5 s al iniciar la etapa. El texto de la slide es este:

```text
Etapa 2 · Apache Pig
ETL: filtrar montos inválidos y estandarizar regiones
/retail/raw/ventas  →  Pig Latin  →  /retail/clean/ventas_limpias
```

## Script principal — guardar como `scripts/etl_ventas.pig`

```pig
-- =====================================================================
-- etl_ventas.pig  ·  ES3 Big Data TI2081  ·  Retail Inteligente
-- Entrada : /retail/raw/ventas/ventas_raw.csv  (180 ventas + encabezado)
-- Salidas : /retail/clean/ventas_limpias          ventas válidas normalizadas
--           /retail/clean/ventas_descartadas      ventas con monto <= 0
--           /retail/clean/conteos_etl             filas entrada / salida / descartadas
--           /retail/clean/mapeo_regiones          region_raw -> region oficial (con conteo)
--           /retail/clean/ejemplos_normalizacion  5 ejemplos de normalización
-- =====================================================================

-- Re-ejecutable: Pig falla si la salida ya existe
rmf /retail/clean/ventas_limpias
rmf /retail/clean/ventas_descartadas
rmf /retail/clean/conteos_etl
rmf /retail/clean/mapeo_regiones
rmf /retail/clean/ejemplos_normalizacion

-- 1) Carga: todo como texto para controlar la conversión
raw = LOAD '/retail/raw/ventas/ventas_raw.csv' USING PigStorage(',')
      AS (venta_id:chararray, fecha:chararray, cliente_id:chararray, producto_id:chararray,
          region_raw:chararray, cantidad:chararray, monto_txt:chararray);

-- 2) Quitar el encabezado
sin_header = FILTER raw BY venta_id != 'venta_id';

-- 3) Tipar. TRIM elimina espacios y el '\r' final (el CSV viene con fin de línea Windows)
tipadas = FOREACH sin_header GENERATE
            TRIM(venta_id)    AS venta_id,
            TRIM(fecha)       AS fecha,
            TRIM(cliente_id)  AS cliente_id,
            TRIM(producto_id) AS producto_id,
            TRIM(region_raw)  AS region_raw,
            (int)  TRIM(cantidad)  AS cantidad,
            (long) TRIM(monto_txt) AS monto_clp;

-- 4) Regla de negocio: solo montos positivos
validas     = FILTER tipadas BY monto_clp IS NOT NULL AND monto_clp > 0;
descartadas = FILTER tipadas BY monto_clp IS NULL OR monto_clp <= 0;

-- 5) Estandarizar region_raw a los 4 nombres oficiales
normalizadas = FOREACH validas GENERATE
    venta_id, fecha, cliente_id, producto_id, region_raw,
    (CASE UPPER(region_raw)
        WHEN 'SANTIAGO'   THEN 'Santiago'
        WHEN 'STGO.'      THEN 'Santiago'
        WHEN 'VALPARAISO' THEN 'Valparaiso'
        WHEN 'VALPO.'     THEN 'Valparaiso'
        WHEN 'CONCEPCION' THEN 'Concepcion'
        WHEN 'CONCE.'     THEN 'Concepcion'
        WHEN 'LA SERENA'  THEN 'La Serena'
        WHEN 'SERENA'     THEN 'La Serena'
        ELSE 'SIN_REGION'
     END) AS region,
    cantidad, monto_clp;

-- 6) Salidas principales (sin encabezado, separadas por coma: listas para Hive)
STORE normalizadas INTO '/retail/clean/ventas_limpias'     USING PigStorage(',');
STORE descartadas  INTO '/retail/clean/ventas_descartadas' USING PigStorage(',');

-- 7) Evidencia: conteos de entrada / salida / descartadas
g_in  = GROUP tipadas ALL;
n_in  = FOREACH g_in  GENERATE 'entrada'        AS etapa, COUNT(tipadas)      AS filas;
g_ok  = GROUP normalizadas ALL;
n_ok  = FOREACH g_ok  GENERATE 'salida_validas' AS etapa, COUNT(normalizadas) AS filas;
g_bad = GROUP descartadas ALL;
n_bad = FOREACH g_bad GENERATE 'descartadas'    AS etapa, COUNT(descartadas)  AS filas;
conteos = UNION n_in, n_ok, n_bad;
STORE conteos INTO '/retail/clean/conteos_etl' USING PigStorage(',');

-- 8) Evidencia: tabla de mapeo region_raw -> region, con cuántas filas tomó cada regla
g_map  = GROUP normalizadas BY (region_raw, region);
mapeo  = FOREACH g_map GENERATE FLATTEN(group) AS (region_raw, region), COUNT(normalizadas) AS filas;
mapeo_ord = ORDER mapeo BY region, region_raw;
STORE mapeo_ord INTO '/retail/clean/mapeo_regiones' USING PigStorage(',');

-- 9) Evidencia: 5 ejemplos donde la región cambió
cambiadas = FILTER normalizadas BY region_raw != region;
camb_ord  = ORDER cambiadas BY venta_id;
ejemplos  = LIMIT camb_ord 5;
STORE ejemplos INTO '/retail/clean/ejemplos_normalizacion' USING PigStorage(',');
```

## Script de dimensiones — guardar como `scripts/limpieza_dimensiones.pig`

Hive necesita las dimensiones sin encabezado y sin el `\r` de Windows (si no, el último campo, `segmento` y `precio`, quedaría con un carácter invisible y los JOIN/filtros fallarían).

```pig
-- limpieza_dimensiones.pig · deja dim_clientes y dim_productos listas para Hive
rmf /retail/clean/dim_clientes
rmf /retail/clean/dim_productos

cli_raw = LOAD '/retail/raw/clientes/dim_clientes.csv' USING PigStorage(',')
          AS (cliente_id:chararray, nombre_ficticio:chararray, region:chararray, segmento:chararray);
cli_ok  = FILTER cli_raw BY cliente_id != 'cliente_id';
clientes = FOREACH cli_ok GENERATE TRIM(cliente_id), TRIM(nombre_ficticio), TRIM(region), TRIM(segmento);
STORE clientes INTO '/retail/clean/dim_clientes' USING PigStorage(',');

pro_raw = LOAD '/retail/raw/productos/dim_productos.csv' USING PigStorage(',')
          AS (producto_id:chararray, producto:chararray, categoria:chararray, precio_txt:chararray);
pro_ok  = FILTER pro_raw BY producto_id != 'producto_id';
productos = FOREACH pro_ok GENERATE TRIM(producto_id), TRIM(producto), TRIM(categoria), (int) TRIM(precio_txt);
STORE productos INTO '/retail/clean/dim_productos' USING PigStorage(',');
```

---

## Paso 1 — Mostrar el script (≈1:30)

```bash
cd ~/retail_es3
cat scripts/etl_ventas.pig        # o abrirlo en el editor con fuente grande
```

> Este es el script Pig Latin. Primero carga el CSV crudo desde HDFS, todo como texto, para controlar yo la conversión de tipos.

> Luego elimina la fila de encabezado y convierte cantidad y monto a números. Uso `TRIM` porque el archivo viene con fin de línea de Windows: cada línea termina en un retorno de carro invisible, pegado al monto, que es la última columna, y eso puede hacer fallar la conversión a número. Lo detecté al revisar el archivo con `cat -A`.

> La regla de negocio está en el `FILTER`: solo pasan ventas con monto mayor que cero. Las demás no se borran: se guardan aparte en `ventas_descartadas` para mantener trazabilidad.

> La estandarización usa un `CASE` sobre la región en mayúsculas, así "Santiago", "SANTIAGO" y "Stgo." terminan como "Santiago". Si apareciera una variante no prevista, quedaría como `SIN_REGION` en vez de perderse en silencio. Además conservo la columna original `region_raw` junto a la nueva `region`, para poder auditar cada cambio.

> Al final guardo la salida limpia y tres archivos de evidencia: los conteos, la tabla de mapeo y cinco ejemplos.

Evidencia del problema del `\r` (opcional, 10 s):

```bash
head -2 datos/ventas_raw.csv | cat -A      # se ve ^M$ al final de cada línea
```

## Paso 2 — Ejecutar (≈1:30, cortar la espera en edición)

```bash
pig -x mapreduce scripts/etl_ventas.pig 2>&1 | tee resultados/pig_etl.log
pig -x mapreduce scripts/limpieza_dimensiones.pig 2>&1 | tee resultados/pig_dims.log
```

> Ejecuto en modo MapReduce, es decir, Pig traduce el script a trabajos que corren en YARN sobre HDFS.

Al terminar, mostrar el resumen de Pig (aparece al final de la salida):

```bash
grep -E "Success|Successfully (read|stored)" resultados/pig_etl.log
```

> Pig termina con "Success" y su propio resumen: leyó 181 registros, que son 180 ventas más el encabezado, y almacenó 174 registros en `ventas_limpias` y 6 en `ventas_descartadas`.

## Paso 3 — Comprobar conteos (≈1:00)

```bash
hdfs dfs -ls /retail/clean
hdfs dfs -cat /retail/clean/conteos_etl/part-*
hdfs dfs -cat /retail/clean/ventas_descartadas/part-*
hdfs dfs -cat /retail/clean/ventas_limpias/part-* | wc -l
```

> Entraron 180 ventas, salieron 174 válidas y se descartaron 6. 174 más 6 da 180, así que no se perdió ninguna fila. Las 6 descartadas tienen monto negativo, y las seis eran de Valparaíso.

## Paso 4 — Comprobar la normalización (≈1:00)

```bash
hdfs dfs -cat /retail/clean/ejemplos_normalizacion/part-*
hdfs dfs -cat /retail/clean/mapeo_regiones/part-*
hdfs dfs -cat /retail/clean/ventas_limpias/part-* | cut -d, -f6 | sort | uniq -c
```

> Estos son cinco ejemplos reales: la venta V0003 venía como "VALPARAISO" y quedó "Valparaiso"; la V0004 venía como "Stgo." y quedó "Santiago"; la V0009 venía como "LA SERENA" y quedó "La Serena".

> La tabla de mapeo muestra las doce variantes originales y a qué región oficial fue cada una, con su cantidad de filas. Y en la salida limpia la columna región tiene solo cuatro valores. No aparece ningún `SIN_REGION`, así que todas las variantes fueron reconocidas.

## Paso 5 — Dimensiones limpias (≈20 s)

```bash
hdfs dfs -cat /retail/clean/dim_clientes/part-* | head -3
hdfs dfs -cat /retail/clean/dim_productos/part-*
```

> También limpié las dimensiones con Pig: sin encabezado y sin el retorno de carro, para que Hive las lea correctamente. No edité ningún CSV a mano.

---

## Qué debe verse

**conteos_etl**
```text
entrada,180
salida_validas,174
descartadas,6
```
(el orden de las filas puede variar)

**ventas_descartadas** (6 filas, todas monto negativo)
```text
V0029,2026-09-02,C026,P006,Valparaiso,3,-66000
V0058,2026-09-03,C022,P002,Valpo.,2,-36000
V0087,2026-09-04,C018,P007,VALPARAISO,1,-280000
V0116,2026-09-05,C014,P003,Valparaiso,3,-87000
V0145,2026-09-06,C010,P008,Valpo.,2,-136000
V0174,2026-09-07,C006,P004,VALPARAISO,1,-95000
```

**ejemplos_normalizacion**
```text
V0003,2026-09-04,C022,P007,VALPARAISO,Valparaiso,1,280000
V0004,2026-09-05,C029,P003,Stgo.,Santiago,2,58000
V0006,2026-09-07,C013,P004,SANTIAGO,Santiago,1,95000
V0009,2026-09-10,C004,P002,LA SERENA,La Serena,1,18000
V0012,2026-09-13,C026,P008,VALPARAISO,Valparaiso,1,68000
```

**mapeo_regiones** (12 filas; 115 de las 174 filas cambiaron de forma)
```text
CONCEPCION,Concepcion,16
Conce.,Concepcion,16
Concepcion,Concepcion,12
LA SERENA,La Serena,16
La Serena,La Serena,14
Serena,La Serena,13
SANTIAGO,Santiago,14
Santiago,Santiago,18
Stgo.,Santiago,14
VALPARAISO,Valparaiso,12
Valparaiso,Valparaiso,15
Valpo.,Valparaiso,14
```

**Filas por región oficial en ventas_limpias**
```text
44 Concepcion
43 La Serena
46 Santiago
41 Valparaiso
```

## Checklist de rúbrica

- [x] Criterio 3 — carga CSV, filtra montos ≤ 0, normaliza, genera salida, valida recuentos (entrada/salida/descartadas) y 5 ejemplos.
- [x] Criterio 7 — problema/solución: fin de línea CRLF → `TRIM` antes del cast.
- [x] Criterio 1 — la salida queda en `/retail/clean`, que es la entrada de Hive.
