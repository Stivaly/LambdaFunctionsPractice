# Taller MCDA para e-commerce
# Seleccion de una plataforma de e-commerce usando funciones de valor,
# pesos, gates de admisibilidad y PuLP.

import pulp

# ==================================================
# 1. DATOS
# ==================================================
# Los datos son los que entrega la guia del taller. En un caso real cada
# dato deberia tener fuente, fecha, metodo y responsable.

alternativas = {
    "A_ShopFast": {
        "tco": 35000,
        "latencia": 250,
        "disponibilidad": 99.70,
        "PU": 4.4,
        "PEOU": 4.0,
        "mantenibilidad": 7.0,
        "persuasion_support": 10.0,
        # Gates no compensatorios
        "legal": True,
        "autonomia": False,
        "privacidad": True,
        "seguridad": True
    },
    "B_TrustCart": {
        "tco": 45000,
        "latencia": 300,
        "disponibilidad": 99.90,
        "PU": 4.5,
        "PEOU": 4.6,
        "mantenibilidad": 8.0,
        "persuasion_support": 7.5,
        "legal": True,
        "autonomia": True,
        "privacidad": True,
        "seguridad": True
    },
    "C_LeanCommerce": {
        "tco": 30000,
        "latencia": 420,
        "disponibilidad": 99.50,
        "PU": 4.0,
        "PEOU": 4.2,
        "mantenibilidad": 7.5,
        "persuasion_support": 6.5,
        "legal": True,
        "autonomia": True,
        "privacidad": True,
        "seguridad": True
    },
    "D_ProCommerce": {
        "tco": 52000,
        "latencia": 210,
        "disponibilidad": 99.95,
        "PU": 4.7,
        "PEOU": 4.1,
        "mantenibilidad": 8.5,
        "persuasion_support": 8.0,
        "legal": True,
        "autonomia": True,
        "privacidad": True,
        "seguridad": True
    }
}

# ==================================================
# 2. FUNCIONES DE VALOR (escala 0-10)
# ==================================================

def valor_menor_mejor(x, minimo, maximo):
    valor = 10 * (maximo - x) / (maximo - minimo)
    return max(0, min(10, valor))


def valor_mayor_mejor(x, minimo, maximo):
    valor = 10 * (x - minimo) / (maximo - minimo)
    return max(0, min(10, valor))


# ==================================================
# 3. TRANSFORMACION
# ==================================================
# Anclas (de la guia): TCO 25000-60000, latencia 150-600 ms,
# disponibilidad 99-100 %, TAM 1-5. Mantenibilidad y persuasion ya vienen 0-10.

def calcular_valores(alternativas):
    valores = {}
    for nombre, d in alternativas.items():
        valores[nombre] = {
            "costo": valor_menor_mejor(d["tco"], 25000, 60000),
            "rendimiento": valor_menor_mejor(d["latencia"], 150, 600),
            "disponibilidad": valor_mayor_mejor(d["disponibilidad"], 99.0, 100.0),
            "PU": valor_mayor_mejor(d["PU"], 1, 5),
            "PEOU": valor_mayor_mejor(d["PEOU"], 1, 5),
            "mantenibilidad": d["mantenibilidad"],
            "persuasion_support": d["persuasion_support"]
        }
    return valores

# ==================================================
# 4. PREFERENCIAS (pesos)
# ==================================================
# Justificacion breve (mas detalle en respuestas_taller.md):
# - costo 0.15: importa a la organizacion, pero no es lo unico.
# - rendimiento 0.10 y disponibilidad 0.10: todas las opciones estan en
#   rangos aceptables, asi que se les da un peso moderado.
# - PU 0.20 y PEOU 0.20: si los usuarios no aceptan la plataforma no sirve
#   de nada lo demas, por eso son los pesos mas altos (TAM).
# - mantenibilidad 0.10: importa al equipo TI a mediano plazo.
# - persuasion_support 0.15: la organizacion quiere usar mecanismos
#   persuasivos, pero solo responsables (lo no responsable va en el gate).

pesos = {
    "costo": 0.15,
    "rendimiento": 0.10,
    "disponibilidad": 0.10,
    "PU": 0.20,
    "PEOU": 0.20,
    "mantenibilidad": 0.10,
    "persuasion_support": 0.15
}

assert abs(sum(pesos.values()) - 1.0) < 1e-9

# ==================================================
# 5. SCORING COMPENSATORIO
# ==================================================

def calcular_scores(valores, pesos):
    score = {}
    for nombre in valores:
        score[nombre] = sum(
            pesos[c] * valores[nombre][c]
            for c in pesos
        )
    return score

# ==================================================
# 6. GATE NO COMPENSATORIO
# ==================================================

def es_admisible(d):
    return (
        d["legal"]
        and d["autonomia"]
        and d["privacidad"]
        and d["seguridad"]
    )

# ==================================================
# 7. MODELO PULP
# ==================================================

def resolver_pulp(alternativas, score, admisibles):
    modelo = pulp.LpProblem("Seleccion_Plataforma_Ecommerce", pulp.LpMaximize)

    x = pulp.LpVariable.dicts("seleccionar", alternativas.keys(), cat="Binary")

    # Funcion objetivo
    modelo += pulp.lpSum(score[a] * x[a] for a in alternativas)

    # Elegir exactamente una plataforma
    modelo += pulp.lpSum(x[a] for a in alternativas) == 1

    # Vetos no compensatorios
    for a in alternativas:
        if not admisibles[a]:
            modelo += x[a] == 0

    modelo.solve(pulp.PULP_CBC_CMD(msg=False))
    return modelo, x

# ==================================================
# 8. SENSIBILIDAD
# ==================================================

def ajustar_peso(base, criterio_objetivo, nuevo_peso):
    restantes = {k: v for k, v in base.items() if k != criterio_objetivo}
    suma_restantes = sum(restantes.values())

    nuevos = {}
    for k, v in base.items():
        if k == criterio_objetivo:
            nuevos[k] = nuevo_peso
        else:
            nuevos[k] = (v / suma_restantes) * (1 - nuevo_peso)
    return nuevos


def sensibilidad(alternativas, valores, admisibles, pesos, criterio, lista_pesos):
    print("\nSENSIBILIDAD DE", criterio)

    # ganador con los pesos base, para comparar si cambia
    score_base = calcular_scores(valores, pesos)
    candidatos = [a for a in alternativas if admisibles[a]]
    ganador_base = max(candidatos, key=lambda a: score_base[a])

    print("peso   ganador          score   2do lugar        diferencia  cambio?")
    for nuevo in lista_pesos:
        w = ajustar_peso(pesos, criterio, nuevo)
        scores_esc = calcular_scores(valores, w)

        ordenados = sorted(candidatos, key=lambda a: scores_esc[a], reverse=True)
        ganador = ordenados[0]
        segundo = ordenados[1]
        dif = scores_esc[ganador] - scores_esc[segundo]

        if ganador != ganador_base:
            cambio = "SI"
        else:
            cambio = "NO"

        print(f"{nuevo:.2f}   {ganador:<16} {scores_esc[ganador]:.3f}   "
              f"{segundo:<16} {dif:.3f}       {cambio}")


# ==================================================
# 9. FLUJO COMPLETO
# ==================================================

def ejecutar(alternativas, titulo):
    print("=" * 60)
    print(titulo)
    print("=" * 60)

    valores = calcular_valores(alternativas)
    score = calcular_scores(valores, pesos)

    print("\nVALORES NORMALIZADOS (0-10)")
    for a in valores:
        print(a, {c: round(v, 2) for c, v in valores[a].items()})

    # Ranking sin gates (Actividad 8)
    print("\nSCORING SIN GATES")
    ranking = sorted(score.items(), key=lambda t: t[1], reverse=True)
    for i, (nombre, s) in enumerate(ranking, 1):
        print(i, nombre, round(s, 3))

    # Admisibilidad (Actividad 7)
    admisibles = {nombre: es_admisible(d) for nombre, d in alternativas.items()}
    print("\nADMISIBILIDAD")
    for nombre, ok in admisibles.items():
        fallas = [g for g in ["legal", "autonomia", "privacidad", "seguridad"]
                  if not alternativas[nombre][g]]
        texto = "PASS" if ok else "FAIL (falla: " + ", ".join(fallas) + ")"
        print(nombre, texto)

    # PuLP
    modelo, x = resolver_pulp(alternativas, score, admisibles)
    print("\nESTADO:", pulp.LpStatus[modelo.status])

    seleccionada = None
    for a in alternativas:
        print(a, "score=", round(score[a], 3), "admisible=", admisibles[a],
              "x=", x[a].value())
        if x[a].value() == 1:
            seleccionada = a
    print("\nSELECCIONADA:", seleccionada, "Score:", round(score[seleccionada], 3))

    # Trazabilidad: dato -> valor -> peso -> contribucion -> score
    print("\nDETALLE (trazabilidad)")
    campo_dato = {
        "costo": "tco", "rendimiento": "latencia",
        "disponibilidad": "disponibilidad", "PU": "PU", "PEOU": "PEOU",
        "mantenibilidad": "mantenibilidad",
        "persuasion_support": "persuasion_support"
    }
    for a in alternativas:
        print("\n", a, "| Admisible:", admisibles[a], "| Score:", round(score[a], 3))
        for criterio in pesos:
            contribucion = pesos[criterio] * valores[a][criterio]
            print(f"   {criterio:<19} dato={alternativas[a][campo_dato[criterio]]:<8}"
                  f" valor={valores[a][criterio]:.3f}"
                  f" peso={pesos[criterio]:.2f}"
                  f" contribucion={contribucion:.3f}")

    # Verificacion (Sargent)
    print("\nVERIFICACION")
    suma_x = sum(x[a].value() for a in alternativas)
    print("Pesos suman 1:", abs(sum(pesos.values()) - 1) < 1e-9)
    print("Se elige exactamente una alternativa:", suma_x == 1)
    print("Inadmisibles con x=0:",
          all(x[a].value() == 0 for a in alternativas if not admisibles[a]))
    # El ganador de PuLP debe ser el mismo que el maximo entre admisibles
    mejor_admisible = max([a for a in alternativas if admisibles[a]],
                          key=lambda a: score[a])
    print("PuLP coincide con el maximo admisible:", mejor_admisible == seleccionada)

    sensibilidad(alternativas, valores, admisibles, pesos, "PEOU",
                 [0.10, 0.15, 0.20, 0.25, 0.30])

    return valores, score, admisibles


valores, score, admisibles = ejecutar(alternativas, "CASO BASE: 4 PLATAFORMAS")

# Verificacion manual (Actividad 10) para B_TrustCart, hecha a mano:
# 0.15*4.286 + 0.10*6.667 + 0.10*9.0 + 0.20*8.75 + 0.20*9.0 + 0.10*8.0 + 0.15*7.5
score_manual_B = (0.15 * (60000 - 45000) / 35000 * 10
                  + 0.10 * (600 - 300) / 450 * 10
                  + 0.10 * 9.0
                  + 0.20 * 8.75
                  + 0.20 * 9.0
                  + 0.10 * 8.0
                  + 0.15 * 7.5)
print("\nScore manual B:", round(score_manual_B, 3),
      "| Score Python B:", round(score["B_TrustCart"], 3))

# ==================================================
# 10. DESAFIO FINAL: quinta plataforma
# ==================================================
# La guia no le pone nombre, le llamamos E_NovaShop.

alternativas_5 = dict(alternativas)
alternativas_5["E_NovaShop"] = {
    "tco": 41000,
    "latencia": 270,
    "disponibilidad": 99.85,
    "PU": 4.3,
    "PEOU": 4.7,
    "mantenibilidad": 7.8,
    "persuasion_support": 8.2,
    "legal": True,
    "autonomia": True,
    "privacidad": True,
    "seguridad": True
}

print("\n")
ejecutar(alternativas_5, "DESAFIO FINAL: 5 PLATAFORMAS")
