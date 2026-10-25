# Resultados resumidos — ES3 Retail Inteligente

> Entregable para Moodle. La columna **Esperado** se calculó a partir de los CSV provistos. Completa **Obtenido** con la salida real de tu ambiente (archivos en `~/retail_es3/resultados/`). Si algún valor no coincide, no lo corrijas a mano: revisa `08_problemas_y_verificacion.md`.

**Estudiante:** `[NOMBRE]` · **Sección:** `[XXX]` · **Fecha de ejecución:** `[AAAA-MM-DD]`

## 1. HDFS

| Ítem | Esperado | Obtenido |
|---|---|---|
| Archivos en `/retail/raw` | 4 | |
| Líneas `ventas_raw.csv` (con encabezado) | 181 | |
| Variantes de `region_raw` | 12 | |
| Bloques / replicación de `ventas_raw.csv` | 1 / 1 | |

## 2. Pig — ETL

| Ítem | Esperado | Obtenido |
|---|---|---|
| Ventas de entrada | 180 | |
| Ventas válidas (`/retail/clean/ventas_limpias`) | 174 | |
| Ventas descartadas (monto ≤ 0) | 6 (V0029, V0058, V0087, V0116, V0145, V0174) | |
| Filas con región modificada | 115 | |
| Regiones distintas en la salida | 4 | |
| Filas `SIN_REGION` | 0 | |

## 3. Hive — retail_dw

| Consulta | Esperado | Obtenido |
|---|---|---|
| Q0 filas / total | 174 / 59.910.000 | |
| Q1 Santiago | 46 ventas · 18.371.000 (30,7 %) | |
| Q1 Valparaiso | 41 ventas · 15.695.000 (26,2 %) | |
| Q1 La Serena | 43 ventas · 14.024.000 (23,4 %) | |
| Q1 Concepcion | 44 ventas · 11.820.000 (19,7 %) | |
| Q2 Tecnologia | 36.850.000 (61,5 %) | |
| Q2 Deportes | 17.400.000 (29,0 %) | |
| Q2 Hogar | 5.660.000 (9,4 %) | |
| Q3 #1 | P001 Notebook · 34.500.000 | |
| Q3 #2 | P007 Bicicleta · 14.000.000 | |
| Q3 #3 | P004 Aspiradora · 4.560.000 | |
| Q4 productos sin ventas | P005 Cafetera, P009 Mancuernas | |

**Interpretaciones:**
1. El Notebook concentra el 57,6 % de la facturación total; Tecnología el 61,5 %.
2. Concepción tiene 44 ventas (más que La Serena y Valparaíso) pero la menor facturación: ticket promedio ≈ 268.636 vs ≈ 399.370 en Santiago.

## 4. HBase — perfiles_cliente

| Ítem | Esperado | Obtenido |
|---|---|---|
| Familias | `datos` (3 versiones), `actividad` | |
| Filas insertadas (RowKey) | C001, C002, C003, C005 | |
| `get C001` actividad | 5 compras · 1.296.000 | |
| Actualización | C005 `datos:segmento` Plus → Premium (2 versiones visibles) | |
| Delete | C003 `actividad:nota_prueba` eliminada | |
| `count` final | 4 | |

## 5. Mahout

| Ítem | Esperado | Obtenido |
|---|---|---|
| Versión | 0.13.0 | |
| Algoritmo | `recommenditembased`, `SIMILARITY_COSINE`, 3 recomendaciones | |
| Modo de ejecución | MapReduce sobre YARN (o plan B1/B2 declarado) | |
| Líneas de entrada | 159 pares (30 usuarios, 7 ítems) | |
| Usuarios con recomendaciones | ≤ 30 | |

**Recomendaciones (pegar de `resultados/mahout_recomendaciones.txt`):**

```text
[PEGAR SALIDA REAL]
```

**Interpretación:** `[COMPLETAR]`

**Limitaciones:** datos pequeños y densos (cada cliente ya compró 4–6 de 7 productos); P005 y P009 sin interacciones (arranque en frío); la preferencia es cantidad comprada, no valoración; sin conjunto de prueba.

## 6. Resultado de negocio y limitación técnica

- **Negocio:** facturación concentrada en un producto (Notebook, 57,6 %); Concepción con bajo ticket promedio; 2 productos sin ventas.
- **Limitación técnica:** un solo nodo (pseudo-distribuido, replicación 1) y 180 registros; HBase y Mahout no integrados automáticamente con Hive.
