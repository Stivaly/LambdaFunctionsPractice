# 22:00 – 27:00 · Etapa 5 — Apache Mahout (recomendaciones)

## Tarjeta de transición

**Slide 7** de `ES3_Retail_Transiciones.pptx`: mostrar 3–5 s al iniciar la etapa. El texto de la slide es este:

```text
Etapa 5 · Apache Mahout 0.13.0
Filtrado colaborativo basado en ítems (recommenditembased)
interacciones cliente-producto → recomendaciones de compra
```

## Decisiones

| Tema | Decisión | Justificación |
|---|---|---|
| Versión | **Mahout 0.13.0** (verificar con `ls $MAHOUT_HOME/*.jar`) | Última versión con algoritmos MapReduce y librería Taste; compatible con Java 8. |
| Algoritmo | `recommenditembased` (filtrado colaborativo ítem-ítem, MapReduce) | Disponible en 0.13.0; el caso pide explorar patrones de compra. |
| Similitud | `SIMILARITY_COSINE` | La preferencia es la cantidad comprada (no binaria); coseno usa esos valores. |
| Entrada | `userID,itemID,preferencia` numéricos | Formato que exige Mahout (IDs `long`). |
| Mapeo de IDs | `C008 → 8`, `P006 → 6` (se quita la letra; el número se conserva) | Reversible y reproducible: el ID numérico es el mismo número del ID original. |
| Preferencia | Suma de `cantidad_comprada` por par cliente-producto | El CSV trae 174 filas pero solo **159 pares únicos** (un cliente compra el mismo producto más de una vez). |

## Preparación de la entrada — guardar como `scripts/prep_mahout.pig`

```pig
-- prep_mahout.pig · transforma interacciones a tripletas numéricas para Mahout
rmf /retail/mahout/input
rmf /retail/mahout/mapeo_clientes

inter_raw = LOAD '/retail/raw/interacciones/interacciones_cliente_producto.csv' USING PigStorage(',')
            AS (cliente_id:chararray, producto_id:chararray, cantidad_txt:chararray);
inter = FILTER inter_raw BY cliente_id != 'cliente_id';

-- Mapeo reproducible: 'C008' -> 8 ; 'P006' -> 6  (SUBSTRING(s, 1, 4) = caracteres 2 a 4)
num = FOREACH inter GENERATE
        TRIM(cliente_id) AS cliente_id,
        (long) SUBSTRING(TRIM(cliente_id), 1, 4)  AS user_id,
        (long) SUBSTRING(TRIM(producto_id), 1, 4) AS item_id,
        (int)  TRIM(cantidad_txt)                 AS cantidad;

-- Un par por cliente-producto; preferencia = unidades totales compradas
g_par = GROUP num BY (user_id, item_id);
pares = FOREACH g_par GENERATE FLATTEN(group) AS (user_id, item_id), (double) SUM(num.cantidad) AS preferencia;
STORE pares INTO '/retail/mahout/input' USING PigStorage(',');

-- Evidencia del mapeo de identificadores
ids  = FOREACH num GENERATE cliente_id, user_id;
mapa = DISTINCT ids;
STORE mapa INTO '/retail/mahout/mapeo_clientes' USING PigStorage(',');
```

## Ejecución — guardar como `scripts/mahout_recomendar.sh`

```bash
#!/usr/bin/env bash
# mahout_recomendar.sh · recomendaciones ítem-ítem sobre YARN/HDFS
set -e
hdfs dfs -rm -r -f /retail/mahout/output /retail/mahout/tmp

mahout recommenditembased \
  --input  /retail/mahout/input \
  --output /retail/mahout/output \
  --tempDir /retail/mahout/tmp \
  --similarityClassname SIMILARITY_COSINE \
  --numRecommendations 3

hdfs dfs -ls /retail/mahout/output
```

## Traducción de la salida a IDs y nombres de producto

Mahout escribe líneas `userID<TAB>[itemID:score,itemID:score,...]`. Este comando devuelve el formato original `C###` / `P###` y agrega el nombre del producto:

```bash
hdfs dfs -cat /retail/mahout/output/part-r-* > resultados/mahout_salida_raw.txt
awk -F'\t' '
  NR==FNR { if (FNR>1) { gsub(/\r/,""); split($0,p,","); nom[p[1]]=p[2] } next }
  { gsub(/[\[\]]/,"",$2); n=split($2,a,",");
    printf "C%03d ->", $1;
    for (i=1;i<=n;i++) { split(a[i],b,":"); id=sprintf("P%03d",b[1]); printf "  %s %s (%.2f)", id, nom[id], b[2] }
    print "" }' datos/dim_productos.csv resultados/mahout_salida_raw.txt | tee resultados/mahout_recomendaciones.txt
```

---

## Paso 1 — Versión y algoritmo (≈30 s)

```bash
echo $MAHOUT_HOME
ls $MAHOUT_HOME/*.jar
mahout 2>&1 | grep -iE "recommenditembased|itemsimilarity|kmeans"
```

> La versión instalada es Apache Mahout 0.13.0, como se ve en el nombre de los jars. Esta versión incluye el algoritmo `recommenditembased`, un filtrado colaborativo basado en ítems que corre como trabajos MapReduce sobre Hadoop. Lo elegí porque está realmente disponible en esta versión y porque el caso pide explorar patrones de compra.

## Paso 2 — Preparación de la entrada (≈1:15)

```bash
cat scripts/prep_mahout.pig
pig -x mapreduce scripts/prep_mahout.pig 2>&1 | tee resultados/pig_mahout.log | grep -E "Success|Successfully"
hdfs dfs -cat /retail/mahout/input/part-* | head -8
hdfs dfs -cat /retail/mahout/input/part-* | wc -l
hdfs dfs -cat /retail/mahout/mapeo_clientes/part-* | head -5
```

> Mahout necesita identificadores numéricos, pero los datos usan códigos como C008 y P006. Hago la transformación con Pig, de forma reproducible: quito la letra y conservo el número, así C008 pasa a ser el usuario 8 y P006 el ítem 6. El mapeo es reversible y lo dejo guardado en HDFS como evidencia.

> Además, el archivo tiene 174 interacciones pero solo 159 pares cliente-producto distintos, porque algunos clientes compraron el mismo producto más de una vez. Agrupo por par y uso como preferencia la suma de unidades compradas. La entrada final tiene 159 líneas con 30 clientes y 7 productos.

## Paso 3 — Ejecutar Mahout (≈1:15, cortar espera)

```bash
cat scripts/mahout_recomendar.sh
bash scripts/mahout_recomendar.sh 2>&1 | tee resultados/mahout_run.log
```

> Ejecuto `mahout recommenditembased` sobre la entrada en HDFS. Mahout calcula la similitud coseno entre productos según qué clientes los compran y en qué cantidad, y para cada cliente recomienda hasta 3 productos que **todavía no ha comprado**. Se ejecuta como una cadena de trabajos MapReduce en YARN.

Mostrar que corrió en Hadoop:

```bash
grep -iE "Running on hadoop|Job .* completed successfully|map 100% reduce 100%" resultados/mahout_run.log | tail -5
```

## Paso 4 — Salida real e interpretación (≈1:15)

```bash
hdfs dfs -cat /retail/mahout/output/part-r-* | head -5      # salida cruda de Mahout
# luego el comando awk de "Traducción de la salida" (arriba)
```

> Esta es la salida real: cada línea es un usuario y una lista de ítems con su puntaje. Con el mapeo inverso la traduzco a los códigos originales y nombres de producto.

> **Interpretación** *(completar con tu salida real)*: Por ejemplo, el cliente C001 ya compró Mouse, Aspiradora, Lámpara, Bicicleta y Zapatillas; del catálogo vendido solo le faltan el Notebook y el Teclado, y Mahout le recomienda **[producto]** con un puntaje de **[x]**. El puntaje es una estimación de preferencia en la misma escala de las cantidades: un valor cercano a **[x]** significa que se espera que compre unas **[x]** unidades, porque ese producto lo compran los mismos clientes que compran lo que C001 ya tiene. Para el negocio esto sirve para ofertas dirigidas: mostrarle a C001 el producto recomendado en su próxima visita.

Otros clientes útiles para interpretar (qué productos les faltan, de los 7 vendidos):

| Cliente | Ya compró | Candidatos posibles |
|---|---|---|
| C001 | P002, P004, P006, P007, P008 | P001, P003 |
| C002 | P002, P003, P004, P006, P008 | P001, P007 |
| C003 | P002, P003, P004, P006, P008 | P001, P007 |
| C008 | P001, P002, P003, P004, P006, P007 | P008 |

## Paso 5 — Limitaciones (≈30 s)

> **Limitación 1, datos pequeños y densos:** son solo 30 clientes y 7 productos con ventas, y cada cliente ya compró entre 4 y 6 de ellos. Por eso cada cliente tiene como máximo 3 candidatos y las similitudes entre productos son muy parecidas: las recomendaciones son válidas como demostración del algoritmo, pero no tienen fuerza estadística.

> **Limitación 2, arranque en frío:** la Cafetera y las Mancuernas nunca se vendieron, así que no tienen interacciones y Mahout no puede recomendarlas nunca. Para eso haría falta otro enfoque, por ejemplo uno basado en contenido o en la categoría.

> **Limitación 3:** la preferencia es la cantidad comprada, no una valoración real del cliente, y no separé datos de prueba para medir la precisión.

---

## Plan B (si `recommenditembased` falla sobre YARN/Hadoop 3)

> Si usas un plan B, **dilo en el video** y explica por qué: el enunciado acepta adaptar el algoritmo si se registra y justifica.

### B1 — Mismo algoritmo en modo local de Mahout

```bash
hdfs dfs -getmerge /retail/mahout/input resultados/mahout_input.csv
rm -rf resultados/mahout_out_local temp
MAHOUT_LOCAL=true mahout recommenditembased \
  --input resultados/mahout_input.csv \
  --output resultados/mahout_out_local \
  --similarityClassname SIMILARITY_COSINE \
  --numRecommendations 3
cat resultados/mahout_out_local/part-r-*
```

### B2 — Programa Java que invoca la API Taste de Mahout 0.13 (no distribuido)

Guardar como `scripts/RecomendadorRetail.java`:

```java
import java.io.File;
import java.util.List;
import org.apache.mahout.cf.taste.impl.common.LongPrimitiveIterator;
import org.apache.mahout.cf.taste.impl.model.file.FileDataModel;
import org.apache.mahout.cf.taste.impl.recommender.GenericItemBasedRecommender;
import org.apache.mahout.cf.taste.impl.similarity.UncenteredCosineSimilarity;
import org.apache.mahout.cf.taste.model.DataModel;
import org.apache.mahout.cf.taste.recommender.RecommendedItem;
import org.apache.mahout.cf.taste.similarity.ItemSimilarity;

/** Recomendador ítem-ítem con Apache Mahout Taste. Entrada: userID,itemID,preferencia */
public class RecomendadorRetail {
  public static void main(String[] args) throws Exception {
    DataModel modelo = new FileDataModel(new File(args[0]));
    ItemSimilarity similitud = new UncenteredCosineSimilarity(modelo);
    GenericItemBasedRecommender recomendador = new GenericItemBasedRecommender(modelo, similitud);

    System.out.printf("Usuarios=%d  Items=%d%n", modelo.getNumUsers(), modelo.getNumItems());
    LongPrimitiveIterator usuarios = modelo.getUserIDs();
    while (usuarios.hasNext()) {
      long u = usuarios.nextLong();
      List<RecommendedItem> recs = recomendador.recommend(u, 3);
      StringBuilder linea = new StringBuilder(String.format("C%03d ->", u));
      for (RecommendedItem r : recs) {
        linea.append(String.format("  P%03d (%.2f)", r.getItemID(), r.getValue()));
      }
      System.out.println(linea);
    }
  }
}
```

```bash
cd ~/retail_es3/scripts
javac -cp "$MAHOUT_HOME/*:$MAHOUT_HOME/lib/*" RecomendadorRetail.java
java  -cp ".:$MAHOUT_HOME/*:$MAHOUT_HOME/lib/*" RecomendadorRetail ../resultados/mahout_input.csv | tee ../resultados/mahout_taste.txt
```

> Si se usa B2, en el video se muestra el código, la compilación con Java 8 contra los jars de Mahout, la ejecución y la salida. No es scikit-learn ni Python: es la API de recomendación de Apache Mahout.

## Qué debe verse

| Comprobación | Valor esperado |
|---|---|
| Líneas en `/retail/mahout/input` | 159 |
| Usuarios distintos / ítems distintos | 30 / 7 (P005 y P009 no aparecen) |
| Formato de entrada | `8,6,2.0` (usuario, ítem, preferencia) |
| Salida | hasta 30 líneas `userID\t[itemID:score,...]`, máx. 3 ítems por usuario, nunca un ítem ya comprado |

## Checklist de rúbrica

- [x] Criterio 6 — versión real, algoritmo compatible, preparación de la entrada, comando Mahout real, salida, interpretación y limitaciones.
- [x] Criterio 1 — se usan las claves compartidas (`cliente_id`, `producto_id`) con mapeo documentado.
- [x] Criterio 7 — pares duplicados detectados (174 → 159) y resueltos con agregación.
