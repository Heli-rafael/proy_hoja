# ============================================================
# PROMPT DE DETECCIÓN
# ============================================================

def construir_prompt(width, height):

    return f"""
Analiza la imagen completa como un sistema de visión computacional
agrícola especializado en detección visual de alteraciones vegetales.

OBJETIVO
Detecta y localiza únicamente daños o alteraciones VISIBLES en tejido
vegetal. La localización precisa es prioritaria.

No asumas especie, cultivo ni enfermedad.
No inventes lesiones ni síntomas.
No diagnostiques enfermedades que no puedan justificarse visualmente.

IMAGEN
Ancho: {width} px
Alto: {height} px

------------------------------------------------------------
1. QUÉ DETECTAR
------------------------------------------------------------

Detecta lesiones o alteraciones visualmente distinguibles, incluyendo:

- manchas;
- necrosis;
- clorosis;
- decoloraciones;
- perforaciones;
- pudrición;
- daños mecánicos;
- marchitez;
- deformaciones;
- patrones compatibles visualmente con hongos, plagas u otros daños.

Detecta lesiones grandes, medianas y pequeñas cuando sean
visualmente distinguibles.

IMPORTANTE:

Cuando existan muchas alteraciones MUY PEQUEÑAS dentro de una zona
concentrada, no generes necesariamente una caja para cada microlesión.

Si esas alteraciones:

- están próximas entre sí;
- presentan un patrón visual similar;
- pertenecen claramente a una misma región;
- forman una concentración o agrupación;
- y analizarlas individualmente produciría demasiadas cajas pequeñas;

agrúpalas en UNA SOLA LESIÓN REGIONAL.

La caja debe representar la región real donde se concentra el daño.

NO conviertas cada punto, mancha diminuta o pequeña alteración en una
lesión independiente si visualmente forman parte de un mismo patrón.

------------------------------------------------------------
2. AGRUPACIÓN DE MICROLESIONES
------------------------------------------------------------

Cuando existan múltiples daños pequeños dentro de una zona:

PRIMERO determina si forman un patrón común.

Si las microlesiones están claramente agrupadas, crea UNA caja que
abarque la concentración completa.

Ejemplo conceptual:

        • •
      • • • •
       • • •
         •

Esto debe considerarse preferentemente como una región dañada si
todas las alteraciones forman un patrón visual coherente.

La caja debe rodear únicamente la concentración:

       ┌───────────┐
       │  • •      │
       │ • • • •   │
       │  • • •    │
       │    •      │
       └───────────┘

NO generes una caja independiente para cada punto.

NO hagas una caja que abarque toda la hoja solamente porque existen
varias microlesiones.

La agrupación debe seguir la DENSIDAD REAL DEL DAÑO.

Si existen varias concentraciones claramente separadas, crea una caja
para cada concentración.

Ejemplo:

    • • •                         • •
   • • •                           • •
    • •                             •

Estas dos regiones deben tener cajas independientes si existe una
separación visual clara entre ellas.

------------------------------------------------------------
3. CUÁNDO NO AGRUPAR
------------------------------------------------------------

NO agrupes automáticamente lesiones únicamente porque estén dentro
de la misma hoja.

NO agrupes lesiones separadas espacialmente si presentan regiones
claramente independientes.

NO combines dos concentraciones alejadas solamente para reducir el
número de cajas.

NO unas lesiones diferentes mediante una caja que incluya grandes
áreas de tejido sano.

La proximidad debe evaluarse junto con:

- continuidad;
- densidad;
- patrón;
- apariencia;
- distribución espacial;
- relación visual entre las alteraciones.

La unidad de detección debe ser la REGIÓN DE DAÑO VISUALMENTE
COHERENTE, no necesariamente cada pequeña mancha individual.

------------------------------------------------------------
4. QUÉ IGNORAR
------------------------------------------------------------

Ignora completamente:

- fondo;
- suelo;
- tierra;
- piedras;
- macetas;
- herramientas;
- manos o dedos;
- etiquetas;
- objetos externos;
- ramas que no presenten daño;
- sombras externas;
- reflejos;
- brillos;
- iluminación;
- nervaduras normales;
- venas normales;
- bordes normales de hojas;
- textura normal;
- variaciones naturales de color.

Analiza únicamente tejido vegetal visible.

------------------------------------------------------------
5. BOUNDING BOX
------------------------------------------------------------

Cada lesión o región de daño debe tener su propio bounding box.

La caja debe ser el RECTÁNGULO MÁS AJUSTADO RAZONABLE que contenga
la lesión o región afectada completa.

Reglas fundamentales:

- No uses toda la imagen.
- No uses toda la hoja si el daño ocupa solo una parte.
- No uses toda la planta.
- No incluyas grandes cantidades de tejido sano.
- No incluyas fondo.
- No agregues márgenes innecesarios.
- No cortes parte de la lesión.
- Una lesión pequeña debe tener una caja pequeña.
- Una lesión grande debe tener una caja grande.
- Una agrupación de microlesiones debe tener una caja proporcional
  a la región donde realmente se concentran.
- La caja debe representar aproximadamente el tamaño real del daño.

Para lesiones irregulares utiliza el rectángulo que contenga sus
límites visibles completos.

------------------------------------------------------------
6. REGLA CRÍTICA: EVITAR CAJAS GIGANTES
------------------------------------------------------------

NO crees una caja que cubra una hoja completa, planta completa o
prácticamente toda la imagen cuando el daño está localizado en
regiones más pequeñas.

Una caja grande SOLO es válida si el daño realmente ocupa esa
superficie.

Antes de crear una caja grande, verifica:

"¿La mayor parte del área dentro de esta caja está realmente dañada?"

Si la respuesta es NO, reduce la caja.

El tejido sano entre lesiones NO debe utilizarse como justificación
para crear una única caja gigante.

------------------------------------------------------------
7. REGLA CRÍTICA: EVITAR CAJAS PADRE INNECESARIAS
------------------------------------------------------------

NO generes una caja general grande que contenga otras cajas más
pequeñas simplemente para indicar que todas están dentro de la misma
hoja.

Ejemplo INCORRECTO:

Caja grande:
┌──────────────────────────────┐
│   ┌─────┐       ┌─────┐      │
│   │     │       │     │      │
│   └─────┘       └─────┘      │
│                              │
│       ┌───────┐              │
│       │       │              │
│       └───────┘              │
└──────────────────────────────┘

Si las cajas pequeñas representan las verdaderas lesiones, NO crees
la caja exterior solamente porque todas están dentro de la misma hoja.

Devuelve las cajas de las regiones de daño reales.

Una caja exterior únicamente es válida cuando representa por sí misma
una REGIÓN DE DAÑO real y visualmente distinguible.

------------------------------------------------------------
8. JERARQUÍA ESPACIAL DE LAS LESIONES
------------------------------------------------------------

Utiliza esta lógica:

NIVEL 1:
Región general realmente afectada.

NIVEL 2:
Concentraciones de microlesiones dentro de esa región.

NIVEL 3:
Lesiones individuales claramente diferenciables.

Pero NO generes todos los niveles simultáneamente.

Selecciona solamente el nivel que mejor represente el daño visible.

REGLA:

Si varias microlesiones forman una única concentración:
→ una caja regional.

Si existen varias concentraciones separadas:
→ una caja por concentración.

Si existe una lesión grande continua:
→ una caja para esa lesión.

Si existe una lesión específica claramente independiente dentro de
otra región de daño:
→ pueden existir dos cajas, pero solo si ambas representan daños
visualmente diferentes.

------------------------------------------------------------
9. COORDENADAS
------------------------------------------------------------

Usa coordenadas NORMALIZADAS respecto a la IMAGEN COMPLETA.

NO uses coordenadas relativas a una hoja.
NO uses coordenadas relativas a una planta.
NO uses píxeles.

Convención:

x1 = límite izquierdo
y1 = límite superior
x2 = límite derecho
y2 = límite inferior

Restricciones:

0 <= x1 < x2 <= 1
0 <= y1 < y2 <= 1

Determina visualmente los cuatro límites de cada lesión antes de
generar las coordenadas.

No coloques una caja simplemente alrededor del centro de una zona.

------------------------------------------------------------
10. MÚLTIPLES REGIONES
------------------------------------------------------------

Si existen varias regiones de daño:

cada región visualmente independiente debe ser un objeto separado.

Ejemplo:

Región A:
zona de microlesiones concentradas en la parte superior.

Región B:
zona de daño diferente en la parte inferior.

Devuelve dos objetos independientes.

No combines regiones separadas únicamente para reducir el número
de resultados.

------------------------------------------------------------
11. LESIONES INTERNAS
------------------------------------------------------------

Una caja dentro de otra SOLO está permitida cuando existen realmente
dos niveles visualmente distinguibles.

Ejemplo:

- una región general claramente dañada;
- dentro de ella existe una lesión específica diferente.

En ese caso pueden existir dos cajas.

Pero NO generes una caja exterior simplemente porque contiene varias
lesiones.

NO uses cajas anidadas para representar simplemente:

"varias lesiones están dentro de la misma hoja".

La hoja NO es una lesión.

Si existe un único daño, devuelve una única caja.

------------------------------------------------------------
12. DUPLICADOS Y SOLAPAMIENTO
------------------------------------------------------------

Antes de responder, comprueba si dos cajas representan el mismo daño.

Si es así, conserva únicamente la caja más precisa.

Evita:

- cajas idénticas;
- cajas casi idénticas;
- cajas superpuestas sin justificación;
- cajas padre innecesarias;
- múltiples cajas para una misma lesión;
- una caja grande que englobe otras cajas pequeñas sin representar
  un daño independiente.

El solapamiento solo es válido cuando representa:

1. lesiones realmente diferentes;
2. regiones visualmente independientes;
3. una lesión interna claramente diferenciable.

Cuando dos lesiones sean independientes y no estén anidadas,
procura que sus cajas no se superpongan innecesariamente.

------------------------------------------------------------
13. CLASIFICACIÓN
------------------------------------------------------------

Utiliza SOLO uno de estos tipos:

Necrosis
Mancha Foliar
Clorosis
Hongo
Mildiu
Oídio
Quemadura Foliar
Pudrición
Daño Mecánico
Deficiencia Nutricional
Plaga
Marchitez
Deformación
Perforación
Decoloración
Lesión
Área Sospechosa
Otro

Selecciona el tipo más específico que pueda justificarse
VISUALMENTE.

Ejemplos:

Tejido marrón claramente muerto -> "Necrosis"

Zona amarilla -> "Clorosis"

Agujero o perforación -> "Perforación"

Daño físico evidente -> "Daño Mecánico"

Mancha visible sin características suficientes -> "Mancha Foliar"

Alteración difícil de clasificar -> "Área Sospechosa"

Una agrupación de microlesiones debe clasificarse según el patrón
visual predominante de la región.

Usa "Hongo", "Mildiu" u "Oídio" únicamente cuando existan
características visuales suficientemente claras.

No conviertas una observación visual en un diagnóstico definitivo.

------------------------------------------------------------
14. TITLE
------------------------------------------------------------

Máximo 3 palabras.

Debe resumir visualmente la alteración o región detectada.

No uses nombres científicos.
No agregues explicaciones.

Ejemplos:

"Mancha Foliar"
"Necrosis"
"Zona Clorótica"
"Daño Mecánico"

------------------------------------------------------------
15. DESCRIPTION
------------------------------------------------------------

Máximo 8 palabras.

Describe SOLO características visualmente observables.

Debe ser breve y objetiva.

Ejemplos:

"Área marrón con bordes oscuros."
"Manchas amarillas sobre tejido verde."
"Perforaciones irregulares en la hoja."
"Zona seca de color marrón."
"Múltiples manchas pequeñas concentradas."

No utilices:

"Se observa"
"Posible"
"Aparentemente"
"Compatible con"
"Podría ser"
"Parece"

------------------------------------------------------------
16. CONFIDENCE
------------------------------------------------------------

Devuelve un número entre 0 y 1.

Evalúa conjuntamente:

- certeza de que existe un daño;
- precisión de la localización;
- precisión de la clasificación;
- coherencia de la agrupación.

Usa valores conservadores.

No uses 1.0 salvo evidencia excepcionalmente clara.

Una región de microlesiones puede tener alta confianza si el patrón
general es claramente visible, aunque cada microlesión individual
no sea perfectamente distinguible.

------------------------------------------------------------
17. REVISIÓN FINAL
------------------------------------------------------------

Antes de generar el JSON verifica internamente:

DETECCIÓN
- ¿La alteración está realmente en tejido vegetal?
- ¿Es visualmente distinguible?
- ¿Estoy evitando falsos positivos?

AGRUPACIÓN
- ¿Existen muchas microlesiones cercanas que pertenecen a una misma
  región?
- ¿Las he agrupado correctamente?
- ¿Estoy creando demasiadas cajas pequeñas?
- ¿Existen varias concentraciones claramente separadas?
- ¿Las he mantenido independientes?

BOUNDING BOX
- ¿La caja contiene todo el daño?
- ¿La caja es lo más ajustada posible?
- ¿Estoy incluyendo demasiado tejido sano?
- ¿Estoy incluyendo fondo?
- ¿Estoy creando una caja gigante sin necesidad?
- ¿Estoy creando una caja de toda la hoja?
- ¿Estoy creando una caja padre innecesaria?

RELACIONES ENTRE CAJAS
- ¿Dos cajas representan realmente daños diferentes?
- ¿Existe solapamiento innecesario?
- ¿Estoy creando cajas anidadas sin justificación?
- ¿Existe realmente una lesión interna independiente?
- ¿Estoy duplicando una lesión?

COORDENADAS
- ¿x1 < x2?
- ¿y1 < y2?
- ¿Todas las coordenadas están entre 0 y 1?
- ¿Las coordenadas corresponden a los límites visuales reales?
- ¿Cada región tiene su propia caja?

CLASIFICACIÓN
- ¿El tipo está justificado visualmente?
- ¿Estoy realizando un diagnóstico que la imagen no permite confirmar?

Corrige cualquier inconsistencia antes de responder.

------------------------------------------------------------
18. FORMATO DE SALIDA
------------------------------------------------------------

Devuelve ÚNICAMENTE JSON válido.

No Markdown.
No explicaciones.
No texto antes ni después del JSON.
No comentarios.
No campos adicionales.

Formato obligatorio:

{{
    "damages": [
        {{
            "title": "string",
            "description": "string",
            "type": "string",
            "confidence": 0.0,
            "bbox": {{
                "x1": 0.0,
                "y1": 0.0,
                "x2": 0.0,
                "y2": 0.0
            }}
        }}
    ]
}}

REGLAS DEL JSON:

"damages" siempre existe y siempre es un arreglo.

Cada elemento representa una única lesión o una única región
coherente de daño.

Cada elemento DEBE contener exactamente:

title
description
type
confidence
bbox

"confidence" debe ser numérico entre 0 y 1.

"x1", "y1", "x2" y "y2" deben ser números entre 0 y 1.

No agregues ningún otro campo.

------------------------------------------------------------
PRIORIDAD ABSOLUTA
------------------------------------------------------------

Prioriza en este orden:

1. LOCALIZACIÓN CORRECTA.
2. AGRUPACIÓN ESPACIAL CORRECTA.
3. BOUNDING BOX AJUSTADO.
4. DETECCIÓN DE DAÑOS REALES.
5. EVITAR FALSOS POSITIVOS.
6. EVITAR CAJAS GIGANTES O PADRE INNECESARIAS.
7. CLASIFICACIÓN VISUAL.
8. DESCRIPCIÓN BREVE.

REGLA ESPECIAL PARA MICROLESIONES:

Muchas alteraciones pequeñas y próximas que forman una concentración
visual coherente deben tratarse preferentemente como UNA REGIÓN DE
DAÑO, no como decenas de lesiones individuales.

REGLA ESPECIAL PARA CAJAS:

NO generes una caja grande que simplemente contenga otras cajas.

Una caja grande debe existir únicamente si esa región grande representa
un daño real por sí misma.

Es preferible devolver:

3 regiones de daño bien delimitadas

que:

20 microcajas innecesarias

o:

1 caja gigante que abarque toda la hoja.

La caja debe seguir la distribución REAL del daño.

No amplíes una caja para compensar incertidumbre.
No reutilices coordenadas.
No dupliques lesiones.
No agrupes regiones visualmente independientes.
No generes cajas padre innecesarias.
No inventes lesiones.

Analiza toda la imagen antes de responder.
"""
