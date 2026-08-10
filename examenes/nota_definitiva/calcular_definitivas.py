#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""calcular_definitivas.py — Regenera la tabla de notas definitivas en definitivas.tex.

Flujo:
  1) Lee la nómina oficial (rosta) del curso.
  2) Extrae las notas de los informes en examenes/{01..04}/informe_examenes/.
  3) Aplica correcciones y notas especiales (exámenes no presentados = 0, salvo sobreescrituras).
  4) Calcula la noticia definitiva = promedio de las 4 unidades (/10) redondeada con
     HALF_UP a cero decimales.
  5) Regenera el bloque de tabla delimitado por TABLA_DEFINITIVAS_START / TABLA_DEFINITIVAS_END
     dentro de definitivas.tex (o imprime las filas con --stdout).

Uso:
  python3 examenes/nota_definitiva/calcular_definitivas.py            # actualiza definitivas.tex
  python3 examenes/nota_definitiva/calcular_definitivas.py --stdout   # solo imprime las filas LaTeX
  python3 examenes/nota_definitiva/calcular_definitivas.py --roster curso/roster.xlsx

Replicabilidad: para otro curso/espacio de trabajo edite las secciones de CONFIG (ROSTER,
UNITS, mapas de nombres -> C.I., correcciones y sobreescrituras). El script es solo
biblioteca estándar (la lectura de .xlsx es opcional mediante --roster y pandas).
"""

import re
import sys
import argparse
import unicodedata
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP

# ══════════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════════

BASE = Path(__file__).resolve().parents[2]          # raíz del repositorio
TEX_PATH = Path(__file__).resolve().parent / "definitivas.tex"
MARK_START = "% TABLA_DEFINITIVAS_START"
MARK_END = "% TABLA_DEFINITIVAS_END"

UNITS = ["01", "02", "03", "04"]

# Fallback de nómina oficial cuando no se pasa --roster (C.I. -> "Apellidos y Nombres").
ROSTER = {
    "33279962": "ACUÑA VELÁSQUEZ ANAMERC DE LOURDES",
    "30749815": "ALCALA ESPINOZA ANA VIRGINIA",
    "32449538": "BRAVO RAMOS KRISCHEL NAZARETH",
    "32585229": "ECHEZURIA RODRÍGUEZ DÉBORA AURORA",
    "32031568": "ESCRIBANO GONZALEZ DANIELA VALENTINA",
    "32747212": "FRONTADO MARCANO MARIA FERNANDA DEL VALLE",
    "33141963": "GARCÍA GARCÍA LUISANNYS CAROLINA",
    "31516750": "INOJOSA GARCÍA DELIANGELIS ANGELICA",
    "33483425": "LOPEZ TOCUYO MICHELLE GABRIELA",
    "32585180": "MALAVÉ GOICETTY MARÍA FERNANDA",
    "31729255": "MARCANO ASTUDILLO BARBARA VALENTINA",
    "36150392": "MARIBAO CELIS YBRANMARIS ALIANA",
    "33627901": "MARIN CALZADILLA LUISIELIS DEL VALLE",
    "34264392": "MARRERO DIAZ VALERIA VALENTINA",
    "33685873": "MELENDEZ RODRIGUEZ MARIA VIRGINIA",
    "33385584": "NARANJO BETANCOURT YILSELYS SARAI",
    "33171611": "PÉREZ GONZÁLEZ GLANYERNYS ESMERALDA",
    "34254529": "RAMOS HERNANDEZ DANIERSY ALEJANDRA",
    "31435612": "RIVERO DE LA CRUZ DANIELA ALEJANDRA",
    "33628014": "RODRIGUEZ DIAZ KARLA PATRICIA",
    "33278284": "RODRÍGUEZ LÓPEZ FRANYERIKA DEL VALLE",
    "32640760": "RODRIGUEZ ORTIZ BARBARA ANGELINA",
    "33386743": "ROJAS MENDÉZ MARIANA MERCEDES",
    "32824239": "ROJAS PAREJO JOHANNYS DEL VALLE",
    "33093620": "ROMERO BOLIVAR SHANTAL ANNIELA",
    "33570679": "SALAZAR YANEZ MARIANA DEL VALLE",
    "31686375": "SANTOYA RODRÍGUEZ ESTEFANI ALEXANDRA",
    "33685285": "SOSA ESCRIBANO THOMAIRYS ANTONELLA",
    "33386357": "SUCRE BETANCOURT ROSMEILYS ALEXANDRA",
    "32778547": "VALLENILLA ARROYO DANIELA DE LOS ANGELES",
    "32823835": "VELÁSQUEZ BRUZUAL SEBASTIÁN JESÚS",
    "32937064": "CABRERA FRANCO CAMILA ISABEL",
}

# C.I. mal transcritas en nombres de archivo -> C.I. oficial.
CI_CORR = {
    "39254529": "34254529", "36450392": "36150392", "34650392": "36150392",
    "34264302": "34264392", "32828239": "32824239", "32824230": "32824239",
}

# Unidad 1: informe `evaluacion_<clave>.tex` -> C.I. (los PDF no traen C.I.).
U1_MAP = {
    "Alanyermus_Perez": "33171611", "Ana_Alcala": "30749815", "Aramerc_Acuna": "33279962",
    "Barbara_Marcano": "31729255", "Barbara_Rodriguez": "32640760", "Camila_Cabrera": "32937064",
    "D_Ramos": "34254529", "Daniela_Escribano": "32031568", "Daniela_Romero": "31435612",
    "Daniela_Vallenilla": "32778547", "Debora_Echeverria": "32585229", "Estefani_Santoya": "31686375",
    "Franyerika_Rodriguez": "33278284", "Karla_Rodriguez": "33628014", "Krischel_Bravo": "32449538",
    "Luisannys_Garcia": "33141963", "Luisielis_Marin": "33627901", "Maria_Frontado": "32747212",
    "Maria_Malave": "32585180", "Maria_Melendez": "33685873", "Mariana_Rojas": "33386743",
    "Mariana_Salazar": "33570679", "Michelle_Lopez": "33483425", "Oliangeles_Inojosa": "31516750",
    "Rosmeilys_Sucre": "33386357", "Shantal_Romero": "33093620", "Thomairys_Sosa": "33685285",
    "Udrannys_Rojas": "32824239", "Ybramaris_Maribao": "36150392", "Yilselys_Betancourt": "33385584",
}

# Unidad 4: informe `informe_<clave>.tex` -> C.I.
U4_MAP = {
    "Ana_Alcala": "30749815", "Anamerc_Acuña": "33279962", "Barbara_Marcano": "31729255",
    "Barbara_Rodriguez": "32640760", "Daniela_Escribano": "32031568", "Daniela_Rivero": "31435612",
    "Daniela_Vallenilla": "32778547", "Daniersy_Ramos": "34254529", "Debora_Echezuria": "32585229",
    "Deliangelis_Inojosa": "31516750", "Estefani_Santoya": "31686375", "Franyerika_Rodriguez": "33278284",
    "Glanyernys_Perez": "33171611", "Johany_Rojas": "32824239", "Karla_Rodriguez": "33628014",
    "Krischel_Bravo": "32449538", "Luisannys_Garcia": "33141963", "Luisielis_Marin": "33627901",
    "Maria_Fernanda Goicetto": "32585180", "Maria_Frontado": "32747212", "Maria_Melendez": "33685873",
    "Mariana_Rojas": "33386743", "Michelle_Lopez": "33483425", "Rosmeilys_Sucre": "33386357",
    "Shantal_Romero": "33093620", "Thomairys_Sosa": "33685285", "Valeria_Marrero": "34264392",
    "Ybianmaris_Maribao": "36150392", "Yilselys_Naranjo": "33385584",
}

# Unidad 2: archivos sin C.I. en el nombre -> C.I.
U2_extra = {"Franyerika_Rodriguez": "33278284"}

# Notas asignadas manualmente a un examen no presentado (C.I. -> {unidad: nota}).
OVERRIDES = {"34264392": {"U1": 7.0}}  # V. Marrero: Unidad I se le otorga 7.

FUERA = 0.0  # examen no presentado cuenta como esta nota

# ══════════════════════════════════════════════════════════════════════
# LECTURA DE NÓMINA (opcional: .xlsx con pandas; si no, se usa ROSTER)
# ══════════════════════════════════════════════════════════════════════

def leer_roster(ruta=None):
    if ruta:
        try:
            import pandas as pd
        except ImportError:
            sys.exit("pandas no está instalado; use el ROSTER embebido.")
        df = pd.read_excel(ruta)
        # Busca la fila de cabecera (contiene 'Cédula') y extrae Cédula / Apellidos y Nombres.
        df.columns = [str(c) for c in df.columns]
        for i, col in enumerate(df.columns):
            if "cédula" in col.lower() or "cedula" in col.lower():
                enc = i
                for j, c2 in enumerate(df.columns):
                    if "apellidos" in str(c2).lower() or "nombres" in str(c2).lower():
                        nom_col, ci_col = c2, df.columns[enc]
                        break
                break
        out = {}
        for _, r in df.iterrows():
            ci = str(r.get(ci_col, "")).strip()
            nom = str(r.get(nom_col, "")).strip()
            if ci.isdigit():
                out[ci] = nom
        return out
    return dict(ROSTER)

# ══════════════════════════════════════════════════════════════════════
# EXTRACCIÓN DE NOTAS
# ══════════════════════════════════════════════════════════════════════

PAT_U12 = re.compile(r"Calificaci[oó]n Final:\s*(\d+(?:[.,]\d+)?)\s*/\s*10")
PAT_U34 = re.compile(r"\\Huge\\bfseries\\color\{[^}]*\}\s*(\d+(?:[.,]\d+)?)\s*/\s*10")


def notas_del_informe(tex: Path):
    txt = tex.read_text(encoding="utf-8", errors="replace")
    m = PAT_U12.search(txt) or PAT_U34.search(txt)
    if not m:
        return None
    return float(m.group(1).replace(",", "."))


def extraer(roster):
    """Devuelve {ci: {unidad: nota}} con Nota None si el archivo no existe."""
    notas = {ci: {} for ci in roster}

    inf = BASE / "examenes/01/informe_examenes"
    for stem, ci in U1_MAP.items():
        p = inf / f"evaluacion_{stem}.tex"
        notas[ci]["U1"] = notas_del_informe(p) if p.exists() else None

    inf = BASE / "examenes/02/informe_examenes"
    for p in sorted(inf.glob("*.tex")):
        st = p.stem.replace("_corregido", "")
        m = re.search(r"_(\d{8})$", st)
        ci = CI_CORR.get(m.group(1), m.group(1)) if m else U2_extra.get(st)
        if ci in notas:
            notas[ci]["U2"] = notas_del_informe(p)

    inf = BASE / "examenes/03/informe_examenes"
    for p in sorted(inf.glob("*.tex")):
        m = re.search(r"_(\d{8})$", p.stem)
        if m:
            ci = CI_CORR.get(m.group(1), m.group(1))
            if ci in notas:
                notas[ci]["U3"] = notas_del_informe(p)

    inf = BASE / "examenes/04/informe_examenes"
    for stem, ci in U4_MAP.items():
        p = inf / f"informe_{stem}.tex"
        notas[ci]["U4"] = notas_del_informe(p) if p.exists() else None

    return notas

# ══════════════════════════════════════════════════════════════════════
# CÁLCULO Y FORMATO
# ══════════════════════════════════════════════════════════════════════

def fmt_num(v):
    if v is None:
        return "—"
    if float(v).is_integer():
        return str(int(v))
    return f"{v:.1f}".replace(".", ",")


def nota_definitiva(gs):
    total = Decimal(str(sum(gs.values())))  # None ya convertido a FUERA
    prom = (total / Decimal(len(gs))).quantize(Decimal("0.01"))
    entera = prom.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return prom, entera


def ordenar_roster(roster):
    """Lista ordenada (ci, nombre) por apellidos, ignorando acentos/capitalización."""
    def clave(nombre):
        norm = unicodedata.normalize("NFKD", nombre)
        sin = "".join(c for c in norm if not unicodedata.combining(c))
        return sin.casefold()

    return sorted(roster.items(), key=lambda par: clave(par[1]))


def construir_tabla(roster, notas):
    filas = []
    for i, (ci, nombre) in enumerate(ordenar_roster(roster), 1):
        gs = {}
        for u in UNITS:
            key = "U" + u[-1]
            gs[key] = notas.get(ci, {}).get(key)
        gs = {k: (OVERRIDES.get(ci, {}).get(k) if v is None and k in OVERRIDES.get(ci, {}) else (FUERA if v is None else v)) for k, v in gs.items()}
        prom, entera = nota_definitiva(gs)
        colon = " & ".join(fmt_num(gs[f"U{u[-1]}"]) for u in UNITS)
        filas.append(f"{i:2d} & {nombre} & {ci} & {colon} & {int(entera)} \\\\")
    cuerpo = "\n".join(filas)
    return cuerpo

# ══════════════════════════════════════════════════════════════════════
# PLANTILLA DEL BLOQUE DE TABLA
# ══════════════════════════════════════════════════════════════════════

TABLA_TEMPLATE = """{start}
\\rowcolors{{2}}{{azulU1!8}}{{white}}
\\setlength{{\\tabcolsep}}{{5pt}}
\\begin{{longtable}}{{>{{\\centering\\arraybackslash}}p{{0.8cm}}
                  >{{\\RaggedRight}}p{{4.8cm}}
                  >{{\\centering\\arraybackslash}}p{{1.7cm}}
                  >{{\\centering\\arraybackslash}}p{{1.0cm}}
                  >{{\\centering\\arraybackslash}}p{{1.0cm}}
                  >{{\\centering\\arraybackslash}}p{{1.0cm}}
                  >{{\\centering\\arraybackslash}}p{{1.0cm}}
                  >{{\\centering\\arraybackslash}}p{{0.95cm}}}}
\\hline
\\rowcolor{{azulOscuro}}
{{\\color{{white}}\\bfseries N.}} & {{\\color{{white}}\\bfseries Apellidos y Nombres}} &
{{\\color{{white}}\\bfseries C.I.}} & {{\\color{{white}}\\bfseries U. I}} &
{{\\color{{white}}\\bfseries U. II}} & {{\\color{{white}}\\bfseries U. III}} &
{{\\color{{white}}\\bfseries U. IV}} & {{\\color{{white}}\\bfseries Nota}}\\\\
\\hline
\\endfirsthead
\\hline
\\rowcolor{{azulOscuro}}
{{\\color{{white}}\\bfseries N.}} & {{\\color{{white}}\\bfseries Apellidos y Nombres}} &
{{\\color{{white}}\\bfseries C.I.}} & {{\\color{{white}}\\bfseries U. I}} &
{{\\color{{white}}\\bfseries U. II}} & {{\\color{{white}}\\bfseries U. III}} &
{{\\color{{white}}\\bfseries U. IV}} & {{\\color{{white}}\\bfseries Nota}}\\\\
\\hline
\\endhead
{rows}
\\hline
\\end{{longtable}}
{end}"""

def construir_bloque(roster, notas):
    cuerpo = construir_tabla(roster, notas)
    return TABLA_TEMPLATE.format(start=MARK_START, end=MARK_END, rows=cuerpo)

# ══════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════

def main():
    ap = argparse.ArgumentParser(description="Regenera la tabla de notas definitivas.")
    ap.add_argument("--stdout", action="store_true", help="solo imprime las filas LaTeX")
    ap.add_argument("--roster", help="ruta a .xlsx con la nómina (opcional)")
    args = ap.parse_args()

    roster = leer_roster(args.roster)
    notas = extraer(roster)

    if args.stdout:
        print(construir_tabla(roster, notas))
        return 0

    tex = TEX_PATH.read_text(encoding="utf-8")
    if MARK_START not in tex or MARK_END not in tex:
        sys.exit(f"No se encontraron los marcadores {MARK_START!r} / {MARK_END!r} en {TEX_PATH}.")
    s = tex.index(MARK_START)
    e = tex.index(MARK_END) + len(MARK_END)
    nuevo = tex[:s] + construir_bloque(roster, notas) + tex[e:]
    TEX_PATH.write_text(nuevo, encoding="utf-8")

    for i, (ci, nombre) in enumerate(ordenar_roster(roster), 1):
        gs = {k: notas.get(ci, {}).get(k) for k in ("U1", "U2", "U3", "U4")}
        gs = {k: (OVERRIDES.get(ci, {}).get(k) if v is None and k in OVERRIDES.get(ci, {}) else (FUERA if v is None else v)) for k, v in gs.items()}
        prom, entera = nota_definitiva(gs)
        vals = "  ".join(fmt_num(gs[k]).rjust(4) for k in ("U1", "U2", "U3", "U4"))
        print(f"{i:2d}  {nombre[:34]:<34}  {ci}  {vals}   -> {int(entera)}")
    print(f"\nTabla actualizada en {TEX_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())