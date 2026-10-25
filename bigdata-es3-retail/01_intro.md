# 00:00 – 01:00 · Identificación y caso

## Tarjeta de transición (pantalla inicial, 5–8 s)

```text
Evaluación Sumativa 3 — Big Data (TI2081)
Proyecto integrador: Retail Inteligente
Hadoop/HDFS · Pig · Hive · HBase · Mahout

[TU NOMBRE COMPLETO]
Sección [XXX]
```

## Narración

> Hola, mi nombre es **[tu nombre]**, de la sección **[sección]**. Esta es la Evaluación Sumativa 3 de Big Data: el proyecto integrador Retail Inteligente.

> Retail Inteligente es una empresa ficticia con ventas en cuatro regiones de Chile: Santiago, Valparaíso, Concepción y La Serena. Sus archivos de ventas tienen dos problemas: la región viene escrita de distintas formas, por ejemplo "Stgo." o "VALPARAISO" en mayúsculas, y hay ventas con monto negativo que no son válidas.

> La gerencia necesita tres cosas: analizar ventas por región y categoría, consultar rápidamente el perfil de un cliente por su identificador, y explorar patrones de compra.

> Para resolverlo voy a construir este flujo en mi ambiente real: **HDFS** recibe los archivos originales, **Pig** limpia y transforma las ventas, **Hive** organiza los datos limpios como data warehouse para analizarlos con SQL, **HBase** permite consultar y modificar perfiles de clientes por clave, y **Mahout** genera recomendaciones a partir de las compras. HBase y Mahout usan datos del mismo negocio, pero son ramas de uso, no una integración directa.

> Todo lo que se ve en este video se ejecuta en vivo sobre Zorin OS con Java 8.

## En pantalla mientras narras

Mostrar la terminal con:

```bash
cd ~/retail_es3
ls datos/
cat datos/README_DATOS.txt
```

Y luego (rápido, para dejar evidencia del ambiente):

```bash
java -version
jps
```

## Checklist de rúbrica

- [x] Criterio 10 — identificación inicial (nombre, sección, título).
- [x] Criterio 1 — se anuncia la secuencia HDFS → Pig → Hive y las ramas HBase / Mahout.
