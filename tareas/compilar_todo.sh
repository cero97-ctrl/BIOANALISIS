#!/usr/bin/env bash

# Detener el script si ocurre algún error crítico
set -e

# Asegurarse de ejecutar el script en el directorio donde se encuentra
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR"

echo "====================================================="
echo "  Iniciando compilación de infografías (Unidad I)..."
echo "====================================================="

for i in {1..25}; do
    echo "-> Procesando problema_${i}.tex"
    # -quiet suprime la salida excesiva de texto en la terminal
    latexmk -pdf -interaction=nonstopmode -quiet "problema_${i}.tex"
done

echo ""
echo "====================================================="
echo "  Iniciando compilación de infografías (Unidad II)..."
echo "====================================================="

for i in {1..8}; do
    echo "-> Procesando problema_${i}_u2.tex"
    latexmk -pdf -interaction=nonstopmode -quiet "problema_${i}_u2.tex"
done

echo ""
echo "====================================================="
echo "  Compilando documentos principales (main.tex y main_u2.tex)"
echo "====================================================="
# latexmk detectará la instrucción \tableofcontents y automáticamente
# compilará main.tex las veces que sean necesarias (usualmente 2 o 3).
latexmk -pdf -interaction=nonstopmode "main.tex"
latexmk -pdf -interaction=nonstopmode "main_u2.tex"

echo ""
echo "====================================================="
echo "  Limpiando archivos temporales (.aux, .log, .toc, etc.)"
echo "====================================================="
latexmk -c -quiet

echo ""
echo "¡Listo! Todos los archivos fueron compilados con éxito."
echo "Los documentos finales unificados te esperan en: main.pdf y main_u2.pdf"