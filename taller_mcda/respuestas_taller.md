# Taller MCDA para e-commerce – Respuestas

Archivo de código: `taller_mcda_ecommerce.py` (se ejecuta con `python taller_mcda_ecommerce.py`, requiere `pip install pulp`).

---

## Actividad 1 – Límites de conocimiento

Primero separo lo que es dato medido de lo que es suposición:

- **Dato medido (según el caso):** TCO estimado, latencia medida (ej. 250 ms en ShopFast), disponibilidad, promedios PU/PEOU de una encuesta.
- **Suposición:** que esa latencia se mantenga con más carga, que el TCO no suba en 3 años, que los usuarios de la encuesta representen a todos los clientes.

Tres cosas que la organización **no sabe con certeza**:

| Incertidumbre | Por qué no se sabe | Evidencia para reducirla |
|---|---|---|
| Costos de mantenimiento a 3 años | El TCO es una estimación, pueden subir licencias, soporte o integraciones | Cotizaciones formales del proveedor, contratos, casos de otras empresas que usen la plataforma |
| Comportamiento de la plataforma con más demanda/carga | La latencia se midió en un momento, no en peaks (ej. Cyber Day) | Pruebas de carga y estrés, SLA del proveedor, historial de disponibilidad |
| Impacto real de las técnicas persuasivas en la conversión | No sabemos si la escasez o la prueba social aumentan las ventas en nuestros clientes, ni si generan desconfianza | Pruebas A/B en piloto, tasa de conversión y de devoluciones/reclamos |

También es incierto el comportamiento futuro de los usuarios (si la aceptación medida en una prueba se mantiene en el uso diario).

---

## Actividad 2 – Formular la decisión

> "Dadas las alternativas **ShopFast, TrustCart, LeanCommerce y ProCommerce**, la organización debe seleccionar **una única plataforma de e-commerce** considerando **valor económico, aceptación de los usuarios, desempeño tecnológico, uso responsable de la persuasión y cumplimiento ético/jurídico**."

- **Quién decide:** la gerencia de la organización (por ejemplo, gerencia comercial junto con la gerencia de TI).
- **Quién utilizará la plataforma:** los clientes que compran y los trabajadores internos que la administran (ventas, marketing, TI).
- **Quién puede ser afectado:** clientes (sus datos y su autonomía al comprar), la organización (costos e ingresos), el equipo TI (mantenimiento) y la sociedad en general.
- **Quién establece restricciones:** el área legal/compliance, el regulador (SERNAC, Ley 19.496, Decreto 6 de 2021) y las políticas internas/código de ética de la organización.

---

## Actividad 3 – Árbol axiológico

Valor superior: V0 = Adopción responsable y sostenible de una solución de e-commerce.

| Stakeholder | ¿Qué valora? | ¿Qué objetivo podría representarlo? | Dimensión |
|---|---|---|---|
| Cliente | Comprar fácil y rápido, que no lo engañen, que cuiden sus datos | Maximizar facilidad de uso (PEOU) y utilidad (PU); no usar persuasión engañosa | V1 Valor para el usuario |
| Organización | Que la plataforma sea rentable y aumente las ventas | Minimizar TCO; maximizar soporte de persuasión responsable (conversión) | V2 Valor económico |
| Equipo tecnológico | Que sea estable, rápida y fácil de mantener | Maximizar disponibilidad, minimizar latencia, maximizar mantenibilidad | V4 Sostenibilidad tecnológica |
| Área legal/compliance | Cumplir la ley y las políticas internas | Cumplir Ley 19.496, Decreto 6/2021 y normativa de datos personales (gate legal y privacidad) | V3 Responsabilidad ética/jurídica |
| Sociedad/regulador | Comercio electrónico justo y seguro, protección del consumidor | Respetar autonomía del consumidor y seguridad de la información (gates) | V3 Responsabilidad ética/jurídica |

De aquí salen los criterios del modelo: los de V1, V2 y V4 quedan como criterios con peso (compensatorios), y los de V3 quedan como gates (no compensatorios).

---

## Actividad 4 – Dato vs constructo (TAM)

Escribir `tam = {"A": 9, "B": 8, "C": 7, "D": 9}` no es suficiente porque:

- No se sabe de dónde salen esos números: quién los puso, si se midió algo o es una opinión del equipo.
- TAM tiene dos constructos distintos (PU y PEOU) y ahí se juntan en un solo número, entonces se pierde información (una plataforma puede ser útil pero difícil de usar).
- PU y PEOU según Davis se miden con ítems tipo Likert respondidos por usuarios, no se inventan. Un 9 sin instrumento es un número computable pero no creíble.

Información adicional que necesitaría:

- El cuestionario usado (ítems PU1–PU3 y PEOU1–PEOU3) y la escala (Likert 1–5).
- Cantidad de personas encuestadas y si eran usuarios representativos (clientes reales, no solo gente del equipo).
- La tarea que hicieron antes de responder (ej. una compra de prueba en cada plataforma).
- Fecha de la medición, quién la hizo y el promedio + dispersión (desviación estándar) de cada constructo.

---

## Actividad 5 – Auditar una técnica persuasiva

Técnica elegida: **escasez** ("Quedan 3 unidades").

| Pregunta | Respuesta |
|---|---|
| ¿Qué conducta intenta facilitar? | Que el cliente decida comprar más rápido y no deje el producto para después. |
| ¿Qué evidencia muestra al usuario? | El stock disponible del producto. Para que sea responsable el número debe venir del inventario real en ese momento. |
| ¿Puede ser rechazada? | Sí, el usuario puede ignorar el mensaje y no comprar, no hay nada que lo obligue (no bloquea ni pone contadores de tiempo falsos). |
| ¿Conserva la autonomía? | Sí, siempre que el dato sea verdadero: el usuario recibe información real y decide él. |
| ¿Qué la convertiría en manipulación? | Mostrar "quedan 3" cuando hay 742 (falsa escasez), inventar temporizadores que se reinician, o esconder que el mensaje es automático. Eso es influencia + engaño. |

Usando el criterio del taller (persuasión responsable = influencia + veracidad + autonomía + transparencia), la escasez es responsable solo si el stock es real y el usuario puede ignorarla. Este es justamente el tipo de cosa que hace fallar a ShopFast en el gate de autonomía.

---

## Actividad 6 – Flujo de datos "Productos para ti" (Nissenbaum)

1. **Qué datos utiliza:** historial de compras, productos vistos, búsquedas, carrito, y posiblemente ubicación o datos del perfil.
2. **Quién los recolecta:** la tienda (organización) a través de la plataforma de e-commerce; también puede intervenir el proveedor de la plataforma o un servicio externo de recomendaciones.
3. **Finalidad:** mostrar productos que podrían interesarle al cliente para facilitar la compra y aumentar las ventas.
4. **Quién recibe la inferencia:** el mismo cliente (ve las recomendaciones) y la tienda. No debería llegar a terceros (ej. vender el perfil a otras empresas).
5. **¿Es esperable en el contexto?** Sí, en una tienda online es normal que recomienden productos según lo que compré o vi en esa misma tienda. No sería esperable que usen datos de otros sitios, datos sensibles (salud, por ejemplo) o que compartan el perfil con terceros.
6. **Control del usuario:** debería poder ver por qué le recomiendan algo, desactivar la personalización, y borrar su historial. Además debe estar informado en la política de privacidad.

Norma aplicable: Ley 19.628 (vigente) y Ley 21.719, que entra en vigencia el 1 de diciembre de 2026. Como este taller se hace antes de esa fecha, la 21.719 hay que considerarla como normativa futura, pero conviene que la plataforma ya se ajuste a ella.

Conclusión: el flujo respeta la integridad contextual si los datos se quedan dentro de la tienda y se usan solo para recomendar. Si se comparten con terceros o se usan para otra cosa, se rompe la norma del contexto.

---

## Actividad 7 – Gate de admisibilidad

ADM(a) = Legal(a) ∧ Autonomía(a) ∧ Privacidad(a) ∧ Seguridad(a)

Condiciones obligatorias:

- **Legal:** cumple Ley 19.496 (consumidor) y Decreto 6/2021 (información clara del precio total, derecho de retracto, etc.).
- **Autonomía:** no usa patrones manipulativos (falsa escasez, cuentas regresivas falsas, casillas premarcadas, dificultar cancelar).
- **Privacidad:** trata los datos personales según la normativa vigente, con consentimiento y finalidad clara.
- **Seguridad:** protege los datos y pagos (HTTPS, cumplimiento PCI-DSS en pagos, gestión de vulnerabilidades).

| Alternativa | Legal | Autonomía | Privacidad | Seguridad | ADM |
|---|---|---|---|---|---|
| A ShopFast | PASS | **FAIL** | PASS | PASS | **FAIL** |
| B TrustCart | PASS | PASS | PASS | PASS | PASS |
| C LeanCommerce | PASS | PASS | PASS | PASS | PASS |
| D ProCommerce | PASS | PASS | PASS | PASS | PASS |

Sobre INDETERMINATE: con los datos de la guía ninguna queda indeterminada, porque los gates vienen como True/False. En un caso real, si no hay evidencia de algo (por ejemplo, no hay auditoría de seguridad de una plataforma) la marcaría como INDETERMINATE y no la dejaría pasar hasta tener esa evidencia. En el código se maneja como booleano, así que INDETERMINATE se trataría igual que FAIL.

---

## Pesos (Paso 11) – Justificación

Los pesos los asigno yo como analista, tomando lo que la guía plantea que la organización valora. En un caso real deberían salir de una conversación con los stakeholders.

| Criterio | Peso | Justificación | Rango que se pondera |
|---|---|---|---|
| Costo / TCO | 0.15 | Le importa a la organización, pero no queremos que lo barato gane por sobre todo lo demás | $25.000 a $60.000 |
| Rendimiento (latencia) | 0.10 | Todas las plataformas están en rangos aceptables (210–420 ms), la diferencia no es tan crítica | 150 a 600 ms |
| Disponibilidad | 0.10 | Todas están sobre 99,5 %, se le da peso moderado | 99 % a 100 % |
| PU | 0.20 | Si el cliente no encuentra útil la plataforma no compra; es lo más importante junto a PEOU (TAM) | Likert 1 a 5 |
| PEOU | 0.20 | La facilidad de uso afecta directamente que el cliente termine la compra | Likert 1 a 5 |
| Mantenibilidad | 0.10 | Importa al equipo TI a mediano plazo, pero el cliente no lo ve directamente | 0 a 10 |
| Persuasión responsable soportada | 0.15 | La organización quiere mecanismos de conversión, pero solo responsables; la parte no responsable ya se controla en el gate | 0 a 10 |
| **Total** | **1.00** | | |

La suma se verifica en el código con `assert abs(sum(pesos.values()) - 1.0) < 1e-9`.

---

## Actividad 8 – Problema del scoring puro

Resultado del scoring sin gates:

| Lugar | Alternativa | Score |
|---|---|---|
| 1 | A_ShopFast | 7.949 |
| 2 | B_TrustCart | 7.685 |
| 3 | D_ProCommerce | 7.610 |
| 4 | C_LeanCommerce | 7.011 |

1. **¿Qué alternativa obtiene el score más alto?** ShopFast, con 7.949.
2. **¿Respeta todos los valores no negociables?** No, falla en autonomía. El caso solo entrega el dato `autonomia: False`, no dice exactamente por qué; mi suposición es que su soporte de conversión (persuasión = 10) incluye cosas como falsa escasez o temporizadores, que no respetan la decisión del usuario.
3. **¿Sería correcto compensar la pérdida de autonomía con mejor costo y más conversión?** No. Si se permite compensar, se está diciendo que manipular a los clientes es aceptable siempre que salga más barato, lo que va contra los valores éticos y probablemente contra la ley del consumidor. Por eso la autonomía se trata como veto y no como un criterio más con peso. Se nota que ShopFast gana gracias a la persuasión (10 puntos, aporta 1.5 al score) y al costo, justo lo que no debería poder "comprar" la autonomía.

---

## Actividad 9 – Interpretar "Optimal"

Que PuLP muestre `Optimal` solo significa que encontró la mejor solución **del modelo** que le dimos: con los scores calculados, la restricción de elegir una y los vetos. Ese modelo depende de la **evidencia** que usamos (datos de TCO, latencia, encuestas TAM), que puede ser incompleta o estar mal medida; de las **preferencias** (los pesos y las anclas que elegimos nosotros); y de las **restricciones** que decidimos poner (los gates). Si cambia cualquiera de esas cosas, el "óptimo" puede ser otra alternativa. Por eso `Optimal` no demuestra que TrustCart sea la mejor del mundo real, solo que es la mejor dado lo que pusimos en el modelo.

---

## Trazabilidad (Paso 17)

El programa imprime para cada alternativa: dato → valor normalizado → peso → contribución → score. Ejemplo para TrustCart:

| Criterio | Dato | Valor (0–10) | Peso | Contribución |
|---|---|---|---|---|
| costo | 45000 | 4.286 | 0.15 | 0.643 |
| rendimiento | 300 ms | 6.667 | 0.10 | 0.667 |
| disponibilidad | 99.90 % | 9.000 | 0.10 | 0.900 |
| PU | 4.5 | 8.750 | 0.20 | 1.750 |
| PEOU | 4.6 | 9.000 | 0.20 | 1.800 |
| mantenibilidad | 8.0 | 8.000 | 0.10 | 0.800 |
| persuasion_support | 7.5 | 7.500 | 0.15 | 1.125 |
| **Score** | | | | **7.685** |

Resultado de PuLP: `Estado: Optimal`, seleccionada **B_TrustCart** (x = 1), las demás con x = 0.

---

## Actividad 10 – Verificación manual y validación

### Verificación manual (TrustCart)

- v_costo = 10·(60000 − 45000)/(60000 − 25000) = 10·15000/35000 = 4.286
- v_rend = 10·(600 − 300)/(600 − 150) = 10·300/450 = 6.667
- v_disp = 10·(99.90 − 99)/(100 − 99) = 9.0
- v_PU = 10·(4.5 − 1)/(5 − 1) = 8.75
- v_PEOU = 10·(4.6 − 1)/(5 − 1) = 9.0
- v_mant = 8.0
- v_pers = 7.5

S(B) = 0.15·4.286 + 0.10·6.667 + 0.10·9.0 + 0.20·8.75 + 0.20·9.0 + 0.10·8.0 + 0.15·7.5
= 0.643 + 0.667 + 0.900 + 1.750 + 1.800 + 0.800 + 1.125 = **7.685**

Python entrega 7.685, coincide.

### Checklist de verificación (¿implementamos bien el modelo?)

| Revisión | Resultado |
|---|---|
| Los pesos suman 1 | Sí (assert y print en el código) |
| Se elige exactamente una alternativa | Sí, suma de x = 1 |
| Inadmisibles con x = 0 | Sí, ShopFast tiene x = 0 |
| Score manual = score Python | Sí, 7.685 en ambos |

### Validación (¿el modelo representa el problema real?)

- **¿Faltan stakeholders?** Podrían faltar los vendedores/proveedores de la tienda o el área de atención al cliente, que también usan la plataforma.
- **¿Faltan criterios?** Sí, por ejemplo: integración con medios de pago chilenos (Webpay, etc.), escalabilidad, accesibilidad, calidad del soporte del proveedor y el riesgo de quedar muy dependiente de un proveedor.
- **¿Las escalas representan bien las preferencias?** Son lineales; en la realidad pasar de 99,5 % a 99,9 % de disponibilidad puede valer mucho más que pasar de 99,0 % a 99,4 %, así que una función lineal puede no ser lo más adecuado.
- **¿TAM fue medido con usuarios apropiados?** No lo sabemos, la guía no indica cuántos usuarios respondieron ni quiénes eran. Es una debilidad.
- **¿Los gates son pertinentes?** Sí, los cuatro (legal, autonomía, privacidad, seguridad) son cosas que no deberían negociarse. Faltaría documentar con qué evidencia se dio PASS a cada uno.
- **¿Las anclas son defendibles?** Son las de la guía y parecen razonables, pero no se indica de dónde salen (presupuesto, SLA, benchmarks). El ancla de TCO afecta bastante a D, que es la más cara.

---

## Actividad 11 – Robustez (sensibilidad del peso de PEOU)

Se varía el peso de PEOU y el resto se redistribuye proporcionalmente con `ajustar_peso()`.

| Peso PEOU | Alternativa ganadora | Score | 2° lugar | Diferencia | ¿Cambió? |
|---|---|---|---|---|---|
| 0.10 | D_ProCommerce | 7.592 | B_TrustCart | 0.072 | Sí |
| 0.15 | B_TrustCart | 7.602 | D_ProCommerce | 0.002 | No |
| 0.20 (base) | B_TrustCart | 7.685 | D_ProCommerce | 0.075 | No |
| 0.25 | B_TrustCart | 7.767 | D_ProCommerce | 0.148 | No |
| 0.30 | B_TrustCart | 7.849 | D_ProCommerce | 0.222 | No |

**Clasificación: Sensible.** Al subir el peso de PEOU, TrustCart se mantiene y gana con más ventaja. Pero si se baja a 0.10 gana ProCommerce, y en 0.15 la diferencia entre B y D es de solo 0.002, prácticamente un empate. El cambio de ganador ocurre entre 0.10 y 0.15 ("¿Cambió?" se compara contra el ganador con los pesos base, que es TrustCart). Es decir, la recomendación de TrustCart depende de que la facilidad de uso tenga un peso de al menos ~0.15. Como el resto de las diferencias de score también son pequeñas (B 7.685 vs D 7.610), no se puede decir que sea robusta.

La razón es que TrustCart le gana a ProCommerce solo en costo y en PEOU (9.0 vs 7.75), mientras que ProCommerce es mejor en todo lo demás (PU, rendimiento, disponibilidad, mantenibilidad y persuasión); al quitarle peso a PEOU esos otros criterios pesan más y ProCommerce pasa adelante.

Lo que se podría hacer: probar también con el peso de costo (D es la más cara, si costo pesa menos D podría ganar) y conseguir mejor evidencia de PEOU, que es justo el criterio que define el resultado.

---

## Actividad 12 – Conclusión (Claim – Argument – Evidence)

> "Se recomienda **B – TrustCart** porque supera **los cuatro criterios no compensatorios (legal, autonomía, privacidad y seguridad)**. Entre las alternativas admisibles obtiene **el mayor score compensatorio (7.685)** bajo los pesos y funciones de valor definidos. La evidencia de aceptación proviene de **las encuestas TAM (PU = 4.5 y PEOU = 4.6 en escala Likert 1–5)**. La recomendación es **sensible** frente a variaciones de **el peso de PEOU: se mantiene entre 0.15 y 0.30, pero con 0.10 gana ProCommerce**. Por ello, la conclusión se considera **justificable pero no robusta** bajo las condiciones evaluadas."

Estructura del argumento:

| Claim | Evidencia | Estado |
|---|---|---|
| C0: TrustCart es una recomendación justificable | C1 a C5 | Se sostiene con reservas |
| C1: cumple criterios no compensatorios | E1: checklist ético/jurídico (gates PASS) | Cumple |
| C2: aceptación tecnológica suficiente | E2: instrumento TAM (PU 4.5, PEOU 4.6) | Cumple, aunque no se conoce el tamaño de la muestra |
| C3: maximiza el valor entre admisibles | E3: datos técnicos + E4: ejecución PuLP (Optimal, x_B = 1) | Cumple |
| C4: el modelo fue verificado | Checklist de verificación + cálculo manual 7.685 | Cumple |
| C5: robustez suficiente | E5: análisis de sensibilidad | **Parcial**: cambia con PEOU = 0.10 |

ShopFast queda descartada aunque tenga el score más alto (7.949), porque falla autonomía. Antes de la decisión final recomendaría hacer una medición TAM más grande comparando TrustCart y ProCommerce, ya que entre esas dos está la decisión.

---

## Desafío final – Quinta plataforma

Como la guía no le da nombre, la llamé **E_NovaShop**. Datos: TCO 41.000, latencia 270 ms, disponibilidad 99,85 %, PU 4.3, PEOU 4.7, mantenibilidad 7.8, persuasión 8.2, todos los gates PASS.

**1–2. Incorporación y normalización:**

| Criterio | Dato | Valor (0–10) | Peso | Contribución |
|---|---|---|---|---|
| costo | 41000 | 10·(60000−41000)/35000 = 5.429 | 0.15 | 0.814 |
| rendimiento | 270 | 10·(600−270)/450 = 7.333 | 0.10 | 0.733 |
| disponibilidad | 99.85 | 8.5 | 0.10 | 0.850 |
| PU | 4.3 | 8.25 | 0.20 | 1.650 |
| PEOU | 4.7 | 9.25 | 0.20 | 1.850 |
| mantenibilidad | 7.8 | 7.8 | 0.10 | 0.780 |
| persuasion_support | 8.2 | 8.2 | 0.15 | 1.230 |
| **Score** | | | | **7.908** |

**3. Ranking sin gates:** ShopFast 7.949 > NovaShop 7.908 > TrustCart 7.685 > ProCommerce 7.610 > LeanCommerce 7.011.

**4. Admisibilidad:** NovaShop PASS en los cuatro gates. ShopFast sigue en FAIL por autonomía.

**5. PuLP:** Estado Optimal, seleccionada **E_NovaShop** (x = 1), resto x = 0. Verificación: pesos suman 1, una sola elegida, ShopFast con x = 0.

**6. Sensibilidad de PEOU:**

| Peso PEOU | Ganador | Score | 2° lugar | Diferencia | ¿Cambió? |
|---|---|---|---|---|---|
| 0.10 | E_NovaShop | 7.740 | D_ProCommerce | 0.148 | No |
| 0.15 | E_NovaShop | 7.824 | B_TrustCart | 0.221 | No |
| 0.20 | E_NovaShop | 7.908 | B_TrustCart | 0.223 | No |
| 0.25 | E_NovaShop | 7.992 | B_TrustCart | 0.225 | No |
| 0.30 | E_NovaShop | 8.075 | B_TrustCart | 0.226 | No |

En todo el rango gana NovaShop, así que respecto a PEOU es **robusta**.

**7. Conclusión:**

> "Se recomienda **E – NovaShop** porque supera **los cuatro criterios no compensatorios**. Entre las alternativas admisibles obtiene **el mayor score (7.908)** bajo los pesos y funciones de valor definidos. La evidencia de aceptación proviene de **las mediciones TAM (PU = 4.3, PEOU = 4.7)**. La recomendación es **robusta** frente a variaciones de **el peso de PEOU entre 0.10 y 0.30**. Por ello, la conclusión se considera **creíble** bajo las condiciones evaluadas."

Observaciones: NovaShop solo es la mejor en PEOU (4.7), en el resto no es la mejor pero tampoco tiene puntajes bajos (es equilibrada), y en una suma ponderada eso le favorece. Comparada con TrustCart, le gana en costo (+0.171), rendimiento, persuasión y PEOU, y pierde un poco en PU, disponibilidad y mantenibilidad. Como gran parte de su ventaja viene de PEOU, la calidad de esa medición sigue siendo clave. Solo se probó la sensibilidad de un peso, faltaría probar otros (costo, PU) para afirmar que es robusta en general.

---

## Preguntas de cierre (respuestas breves)

1. **¿Por qué MCDA no comienza por los pesos?** Porque los pesos solo tienen sentido después de saber qué se valora y qué criterios representan esos valores. Si se parte por los pesos se termina ponderando lo que es fácil de medir y no lo que importa.
2. **¿Qué aporta Keeney?** El Value-Focused Thinking: partir por los valores y objetivos, y ver las alternativas como medios para lograrlos. En el taller se refleja en el árbol V0 → V1..V4.
3. **¿Diferencia entre Roy y el "óptimo absoluto"?** Roy plantea que el modelo ayuda a decidir (decision aid) y se construye con los participantes; no existe una mejor alternativa objetiva independiente de los valores y el contexto.
4. **¿Por qué PU y PEOU requieren evidencia empírica?** Porque son percepciones de los usuarios; solo se pueden conocer preguntándoles con un instrumento válido, no suponiéndolas.
5. **¿Qué aporta Fogg y qué limitación ética se añade?** Fogg explica cómo la tecnología puede influir en el comportamiento (recomendaciones, recordatorios, etc.). La limitación es que la influencia debe ser veraz, transparente y respetar la autonomía; si no, es manipulación.
6. **¿Cómo ayuda Value Sensitive Design?** Obliga a preguntar qué valores afecta cada funcionalidad (privacidad, autonomía, confianza) y diseñarla considerando eso desde el inicio, no después.
7. **¿Por qué privacidad puede ser límite axiológico?** Porque una violación de privacidad no se arregla con un menor costo o mejor rendimiento; además es una obligación legal. Por eso va como veto.
8. **¿Diferencia entre criterio compensatorio y veto?** En el compensatorio una debilidad se puede compensar con otra fortaleza (trade-off aceptable). En el veto, si falla, la alternativa queda fuera sin importar su score.
9. **¿Qué demuestra PuLP con Optimal?** Que encontró la mejor solución del modelo formulado (scores, restricción y vetos), no que sea la mejor en la realidad.
10. **¿Diferencia entre verificar y validar?** Verificar es revisar que el modelo esté bien implementado (cálculos, código). Validar es revisar si el modelo representa bien el problema real (criterios, stakeholders, datos).
11. **¿Por qué la sensibilidad aumenta la credibilidad?** Porque muestra si la recomendación depende de un peso específico o se mantiene con cambios razonables. En el caso base mostró que la elección entre TrustCart y ProCommerce era frágil.
12. **¿Cómo se relacionan Claim, Argument y Evidence?** El claim es lo que se afirma (ej. "TrustCart es justificable"), la evidencia son los datos que lo apoyan (TAM, gates, PuLP, sensibilidad) y el argumento es el razonamiento que explica por qué esa evidencia sostiene el claim.
