# 17:00 – 22:00 · Etapa 4 — Apache HBase (perfiles por RowKey)

## Tarjeta de transición

```text
Etapa 4 · Apache HBase
Tabla perfiles_cliente · RowKey = cliente_id
Familias: datos | actividad · create · put · get · scan · update · delete
```

## Modelo de la tabla

| RowKey | Familia `datos` | Familia `actividad` |
|---|---|---|
| `cliente_id` (C001…) | `nombre`, `region`, `segmento` (desde `dim_clientes`) | `num_compras`, `monto_total_clp` (desde la consulta Q6 de Hive) |

- La familia `datos` guarda hasta 3 versiones, para poder mostrar el historial tras la actualización.
- Clientes cargados: **C001, C002, C003** (mínimo exigido) y **C005** (el cliente con mayor monto comprado).

## Comandos — guardar como `scripts/hbase_perfiles.txt`

```ruby
# hbase_perfiles.txt · ES3 Retail Inteligente · ejecutar: hbase shell -n scripts/hbase_perfiles.txt
# (en el video se ejecutan uno a uno dentro de `hbase shell`)

create 'perfiles_cliente', {NAME => 'datos', VERSIONS => 3}, {NAME => 'actividad'}
describe 'perfiles_cliente'

# --- Inserción: clientes reales de dim_clientes, RowKey = cliente_id ---
put 'perfiles_cliente', 'C001', 'datos:nombre',   'Cliente 001'
put 'perfiles_cliente', 'C001', 'datos:region',   'Santiago'
put 'perfiles_cliente', 'C001', 'datos:segmento', 'Basico'
put 'perfiles_cliente', 'C001', 'actividad:num_compras',     '5'
put 'perfiles_cliente', 'C001', 'actividad:monto_total_clp', '1296000'

put 'perfiles_cliente', 'C002', 'datos:nombre',   'Cliente 002'
put 'perfiles_cliente', 'C002', 'datos:region',   'Valparaiso'
put 'perfiles_cliente', 'C002', 'datos:segmento', 'Plus'
put 'perfiles_cliente', 'C002', 'actividad:num_compras',     '6'
put 'perfiles_cliente', 'C002', 'actividad:monto_total_clp', '689000'

put 'perfiles_cliente', 'C003', 'datos:nombre',   'Cliente 003'
put 'perfiles_cliente', 'C003', 'datos:region',   'Concepcion'
put 'perfiles_cliente', 'C003', 'datos:segmento', 'Premium'
put 'perfiles_cliente', 'C003', 'actividad:num_compras',     '5'
put 'perfiles_cliente', 'C003', 'actividad:monto_total_clp', '485000'

put 'perfiles_cliente', 'C005', 'datos:nombre',   'Cliente 005'
put 'perfiles_cliente', 'C005', 'datos:region',   'Santiago'
put 'perfiles_cliente', 'C005', 'datos:segmento', 'Plus'
put 'perfiles_cliente', 'C005', 'actividad:num_compras',     '6'
put 'perfiles_cliente', 'C005', 'actividad:monto_total_clp', '4977000'

# --- Lectura por RowKey ---
get 'perfiles_cliente', 'C001'

# --- Scan limitado ---
scan 'perfiles_cliente', {LIMIT => 2}
scan 'perfiles_cliente', {COLUMNS => ['datos:segmento'], LIMIT => 3}

# --- Actualización con put y verificación ---
put 'perfiles_cliente', 'C005', 'datos:segmento', 'Premium'
get 'perfiles_cliente', 'C005', 'datos:segmento'
get 'perfiles_cliente', 'C005', {COLUMN => 'datos:segmento', VERSIONS => 3}

# --- Delete controlado de una columna de prueba y verificación ---
put 'perfiles_cliente', 'C003', 'actividad:nota_prueba', 'columna temporal de prueba'
get 'perfiles_cliente', 'C003'
delete 'perfiles_cliente', 'C003', 'actividad:nota_prueba'
get 'perfiles_cliente', 'C003'

count 'perfiles_cliente'
exit
```

---

## Paso 1 — Crear la tabla (≈40 s)

```bash
hbase version 2>/dev/null | head -1
hbase shell
```

```ruby
list
create 'perfiles_cliente', {NAME => 'datos', VERSIONS => 3}, {NAME => 'actividad'}
describe 'perfiles_cliente'
```

> Creo la tabla `perfiles_cliente` con dos familias de columnas. `datos` guarda los atributos del cliente que vienen de `dim_clientes`, y `actividad` guarda su comportamiento de compra. En HBase cada familia se almacena físicamente por separado, por eso separo los datos que cambian poco de los que cambian seguido. A `datos` le dejo 3 versiones para poder ver el historial de cambios.

## Paso 2 — Insertar clientes (≈1:00)

Pegar los `put` de C001, C002, C003 y C005.

> La RowKey es el `cliente_id`, la misma clave de `dim_clientes`. Inserto cuatro clientes que existen en esa dimensión. Los valores de actividad, número de compras y monto total, son los que calculé en Hive con la consulta Q6: por ejemplo C001 tiene 5 compras por 1.296.000 pesos.

## Paso 3 — get y scan (≈1:00)

```ruby
get 'perfiles_cliente', 'C001'
scan 'perfiles_cliente', {LIMIT => 2}
scan 'perfiles_cliente', {COLUMNS => ['datos:segmento'], LIMIT => 3}
```

> Con `get` obtengo todo el perfil de C001 de forma directa por su clave: cada celda muestra familia:columna, timestamp y valor. Con `scan` y `LIMIT` recorro solo las primeras filas, ordenadas por RowKey, y también puedo limitar a una columna.

## Paso 4 — Actualización con put + verificación (≈40 s)

```ruby
put 'perfiles_cliente', 'C005', 'datos:segmento', 'Premium'
get 'perfiles_cliente', 'C005', 'datos:segmento'
get 'perfiles_cliente', 'C005', {COLUMN => 'datos:segmento', VERSIONS => 3}
```

> Simulo que el cliente C005, el que más compra con casi 5 millones, sube de segmento Plus a Premium. En HBase actualizar es simplemente otro `put` sobre la misma celda. El `get` confirma el valor nuevo, y al pedir versiones se ven las dos: Premium con el timestamp más reciente y Plus con el anterior.

## Paso 5 — Delete de columna de prueba + verificación (≈40 s)

```ruby
put 'perfiles_cliente', 'C003', 'actividad:nota_prueba', 'columna temporal de prueba'
get 'perfiles_cliente', 'C003'
delete 'perfiles_cliente', 'C003', 'actividad:nota_prueba'
get 'perfiles_cliente', 'C003'
count 'perfiles_cliente'
```

> Agrego una columna de prueba a C003 y la veo en el `get`. Luego borro solo esa columna con `delete`, y el nuevo `get` muestra que desapareció, pero el resto del perfil sigue intacto. El `count` confirma 4 filas.

## Paso 6 — Almacenamiento físico (opcional, ≈20 s)

```bash
hdfs dfs -ls -R /hbase/data/default/perfiles_cliente | head -15
```

> Físicamente la tabla está en HDFS bajo `/hbase`, con una carpeta por región y una subcarpeta por familia: `datos` y `actividad`.

(Si los datos recién insertados aún están en memoria, en el MemStore, puedes ejecutar `flush 'perfiles_cliente'` en la shell para que aparezcan los HFiles.)

## Paso 7 — Justificación HBase vs Hive (≈40 s)

> ¿Por qué la consulta por cliente se hace en HBase y no en Hive? Hive está diseñado para **análisis**: cada consulta recorre archivos completos y se ejecuta como trabajo MapReduce. Para responder "dame el perfil de C001" tardaría varios segundos leyendo toda la tabla, y además sus tablas de texto no permiten actualizar una fila individual.

> HBase está diseñado para **acceso por clave**: las filas están ordenadas e indexadas por RowKey, así que un `get` va directo a la fila en milisegundos, y permite modificar o borrar una sola celda con `put` y `delete`, con historial de versiones. Por eso los perfiles operativos, que se consultan y actualizan cliente por cliente, van en HBase, y los totales por región y categoría van en Hive.

---

## Qué debe verse

- `describe`: dos familias, `datos` con `VERSIONS => '3'` y `actividad` con `VERSIONS => '1'`.
- `get 'perfiles_cliente','C001'`: 5 celdas → `actividad:monto_total_clp=1296000`, `actividad:num_compras=5`, `datos:nombre=Cliente 001`, `datos:region=Santiago`, `datos:segmento=Basico`.
- `scan ... LIMIT => 2`: filas C001 y C002 (orden lexicográfico de RowKey).
- Versiones de `C005 datos:segmento`: `Premium` (más reciente) y `Plus`.
- C003 tras el `delete`: 5 celdas, sin `actividad:nota_prueba`.
- `count`: `4 row(s)`.

## Checklist de rúbrica

- [x] Criterio 5 — tabla con 2 familias, RowKey `cliente_id`, put / get / scan, actualización y delete controlado con verificación.
- [x] Criterio 8 — análisis (Hive) vs acceso por clave (HBase).
- [x] Criterio 1 — clientes existentes en `dim_clientes`; actividad tomada de Hive (fuente coherente).
