#!/usr/bin/env python3
"""
evaluar_lote.py — Procesador en lote de exámenes para Unidad IV
"""

import os
import sys
import json
import subprocess
from pathlib import Path

PYTHON = "/home/cero/anaconda3/bin/python3"
SCRIPT_DIR = Path(__file__).parent.resolve()
ORQUESTADOR = SCRIPT_DIR / "evaluar_examen.py"
RUBRICA = SCRIPT_DIR / "examenes" / "04" / "rubrica_unidad_IV.txt"
STUDENTS_DIR = SCRIPT_DIR / "examenes" / "04" / "examen_estudiantes"
OUTPUT_DIR = SCRIPT_DIR / "examenes" / "04" / "informe_examenes"
CLEAN_SCRIPT = SCRIPT_DIR / "clean_latex.py"
TMP_DIR = SCRIPT_DIR / ".tmp"

def process_all(force: bool = False, modelo_llm: str = "gemini-3.5-flash"):
    pdfs = sorted(list(STUDENTS_DIR.glob("*.pdf")))
    print(f"Total de exámenes a procesar: {len(pdfs)}")

    results = []

    for i, pdf_path in enumerate(pdfs, start=1):
        stem = pdf_path.stem
        nombre = stem.replace("examen_", "").replace("evaluacion_", "").replace("_", " ")
        json_path = TMP_DIR / f"evaluacion_{stem}.json"
        tex_path = OUTPUT_DIR / f"informe_{stem}.tex"
        pdf_report_path = OUTPUT_DIR / f"informe_{stem}.pdf"

        print(f"\n========================================================")
        print(f"  [{i}/{len(pdfs)}] Procesando: {nombre} ({pdf_path.name})")
        print(f"========================================================")

        # Si ya existe evaluación válida y no se fuerza re-evaluación, reutilizar
        if not force and json_path.exists():
            try:
                data = json.loads(json_path.read_text(encoding="utf-8"))
                if data.get("status") == "ok":
                    eval_data = data.get("evaluacion", {})
                    puntaje = eval_data.get("puntaje_sugerido", "N/A")
                    nivel = eval_data.get("nivel_desempeno", "N/A")
                    print(f"⏩ Evaluación existente encontrada para {nombre}. Reutilizando JSON.")

                    # Asegurar compilación PDF si falta
                    if not pdf_report_path.exists() and tex_path.exists():
                        cmd_latex = ["pdflatex", "-interaction=nonstopmode", tex_path.name]
                        subprocess.run(cmd_latex, cwd=str(OUTPUT_DIR), capture_output=True, text=True, errors="replace")
                        subprocess.run([PYTHON, str(CLEAN_SCRIPT), "examenes/04"], capture_output=True, text=True, errors="replace")

                    results.append({
                        "estudiante": nombre,
                        "status": "ok",
                        "puntaje": puntaje,
                        "nivel": nivel,
                        "archivo": pdf_path.name
                    })
                    continue
            except Exception as e:
                print(f"⚠️ Error leyendo JSON existente: {e}, procediendo a evaluar.")

        # Lista en cascada de modelos con cuotas independientes
        modelos_disponibles = [modelo_llm, "gemini-3.5-flash", "gemini-3.6-flash", "gemini-2.0-flash"]
        # Eliminar duplicados manteniendo orden
        modelos_disponibles = list(dict.fromkeys(modelos_disponibles))

        res_eval = None
        evaluado_con_exito = False

        for current_model in modelos_disponibles:
            cmd_eval = [
                PYTHON, str(ORQUESTADOR),
                "--pdf", str(pdf_path),
                "--rubrica", str(RUBRICA),
                "--modelo", current_model
            ]
            
            max_retries = 2
            for attempt in range(1, max_retries + 1):
                res_eval = subprocess.run(cmd_eval, capture_output=True, text=True, encoding="utf-8", errors="replace")
                if res_eval.returncode == 0:
                    evaluado_con_exito = True
                    break
                
                out_err = res_eval.stderr + res_eval.stdout
                if ("429" in out_err or "RESOURCE_EXHAUSTED" in out_err) and attempt < max_retries:
                    import time
                    print(f"⏳ Límite temporal alcanzado (429) en {current_model}. Esperando 40s ({attempt}/{max_retries})...")
                    time.sleep(40)
                else:
                    break

            if evaluado_con_exito:
                break
            else:
                print(f"⚠️ Cuota agotada o fallo en modelo '{current_model}'. Conmutando automáticamente al siguiente modelo de respaldo...")

        if res_eval.returncode != 0:
            print(f"❌ Error en evaluación para {nombre}: {res_eval.stderr or res_eval.stdout}")
            results.append({
                "estudiante": nombre,
                "status": "error",
                "puntaje": "N/A",
                "nivel": "Error",
                "archivo": pdf_path.name
            })
            continue

        # 2. Leer resultado JSON recién generado
        puntaje = "N/A"
        nivel = "N/A"
        if json_path.exists():
            try:
                data = json.loads(json_path.read_text(encoding="utf-8"))
                eval_data = data.get("evaluacion", {})
                puntaje = eval_data.get("puntaje_sugerido", "N/A")
                nivel = eval_data.get("nivel_desempeno", "N/A")
            except Exception as e:
                print(f"⚠️ Error leyendo JSON de evaluación: {e}")

        # 3. Compilar LaTeX a PDF
        if tex_path.exists():
            cmd_latex = ["pdflatex", "-interaction=nonstopmode", tex_path.name]
            res_latex = subprocess.run(cmd_latex, cwd=str(OUTPUT_DIR), capture_output=True, text=True, errors="replace")
            if res_latex.returncode == 0:
                print(f"✅ PDF de informe compilado: {pdf_report_path.name}")
            else:
                print(f"⚠️ Advertencia al compilar LaTeX para {nombre}")

        # 4. Limpiar archivos auxiliares
        subprocess.run([PYTHON, str(CLEAN_SCRIPT), "examenes/04"], capture_output=True, text=True, errors="replace")

        results.append({
            "estudiante": nombre,
            "status": "ok",
            "puntaje": puntaje,
            "nivel": nivel,
            "archivo": pdf_path.name
        })
        print(f"✅ Finalizado: {nombre} | Puntaje: {puntaje} | Nivel: {nivel}")

    # Guardar resumen final en .tmp/resumen_unidad_IV.json
    resumen_file = TMP_DIR / "resumen_unidad_IV.json"
    resumen_file.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n========================================================")
    print(f"🎉 PROCESAMIENTO EN LOTE FINALIZADO ({len(results)} estudiantes)")
    print(f"Resumen guardado en: {resumen_file}")
    print(f"========================================================")

if __name__ == "__main__":
    force_flag = "--force" in sys.argv
    process_all(force=force_flag)
