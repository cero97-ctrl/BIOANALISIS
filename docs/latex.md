# Registro de Errores y Soluciones en LaTeX

Este documento recopila los errores comunes de compilación encontrados al trabajar con LaTeX y TikZ en este proyecto, junto con sus respectivas soluciones, para servir como referencia futura.

## 1. Conflicto entre TikZ y Babel (Español)

**El Problema:**
Al utilizar el paquete `babel` con el idioma español (`\usepackage[spanish]{babel}`), caracteres como `>` y `<` se vuelven "activos" (*active characters*). Esto interfiere directamente con la sintaxis que utiliza TikZ para dibujar flechas (por ejemplo, al usar `->` en los comandos `\draw`), provocando fallos de compilación.

**La Solución:**
Cargar la librería específica de TikZ diseñada para manejar incompatibilidades con paquetes de idiomas. Se debe agregar la siguiente línea en el preámbulo del documento, justo después de cargar TikZ:

```latex
\usepackage{tikz}
\usetikzlibrary{babel}
```

## 2. Parseo de Coordenadas en bucles `\foreach` (TikZ)

**El Problema:**
El error `Cannot parse this coordinate (Missing character: There is no ( in font nullfont!)` ocurre cuando se intenta iterar una macro que contiene un par de coordenadas completas con paréntesis (ej. `\pos`) y pasarlas a parámetros como `shift={\pos}`. TikZ no logra "desempaquetar" correctamente los paréntesis internos de la variable.

**La Solución:**
En lugar de iterar sobre una única variable que contenga las coordenadas agrupadas con paréntesis, se deben separar las coordenadas `x` e `y` explícitamente utilizando una barra diagonal `/` en la declaración del bucle `\foreach`. Luego, los paréntesis se colocan de forma manual en el uso.

**Ejemplo incorrecto (genera error):**
```latex
\foreach \pos in {(-1.2,-0.8), (-0.8,-1.5)} {
    \begin{scope}[shift={\pos}]
        % ...
    \end{scope}
}
```

## 3. Incluir Imágenes Externas en LaTeX (`graphicx`)

**El Problema:**
De forma nativa, LaTeX básico no cuenta con un comando directo para insertar archivos de imagen (como `.jpg`, `.png` o `.pdf`) con control de escala y posicionamiento dentro del texto.

**La Solución:**
Se debe utilizar el paquete estándar `graphicx`. Este paquete proporciona el comando `\includegraphics`, el cual permite importar imágenes y modificar sus atributos (como el ancho, el alto o el ángulo de rotación).

**Ejemplo de uso:**

```latex
% 1. Añadir al preámbulo (antes de \begin{document}):
\usepackage{graphicx}

% 2. Usar en el cuerpo del documento:
% (Se recomienda envolverlo en un entorno 'center' o 'figure' para alinearlo)
\begin{center}
    % El parámetro 'width=0.6\textwidth' ajusta la imagen al 60% del ancho del texto
    \includegraphics[width=0.6\textwidth]{ruta/o/nombre_de_la_imagen.jpg}
\end{center}
```
```

**Ejemplo corregido:**
```latex
\foreach \x/\y in {-1.2/-0.8, -0.8/-1.5} {
    \begin{scope}[shift={(\x,\y)}]
        % ...
    \end{scope}
}
```

## 4. Valor inválido `none` en `drop shadow` (tcolorbox / pgfkeys)

**El Problema:**
Al usar el paquete `tcolorbox` con la opción `drop shadow=none` para intentar desactivar la sombra de una caja, se produce el error:

```
! Package pgfkeys Error: I do not know the key '/tikz/none' and I am going to ignore it.
```

Esto ocurre porque `none` no es un valor reconocido por la clave `drop shadow` del sistema `pgfkeys`/`tikz`. El motor interpreta `none` como una clave independiente (`/tikz/none`) en lugar de un valor para `drop shadow`.

**La Solución:**
Reemplazar `drop shadow=none` por `no shadow`, que es la opción correcta de `tcolorbox` para desactivar sombras.

**Ejemplo incorrecto (genera error):**
```latex
\begin{tcolorbox}[drop shadow=none]
    % ...
\end{tcolorbox}
```

**Ejemplo corregido:**
```latex
\begin{tcolorbox}[no shadow]
    % ...
\end{tcolorbox}
```
## 5. Caracteres Unicode no soportados por pdflatex (U+2713, U+03C0, etc.)

**Contexto:** Generación de informes LaTeX a partir de texto producido por modelos de lenguaje (Gemini). El modelo incluye en sus respuestas caracteres Unicode como `✓` (U+2713), `π` (U+03C0), `≤` (U+2264), `²` (U+00B2), etc.

**El Problema:**

`pdflatex` con `\usepackage[utf8]{inputenc}` soporta Latin-Extended pero **no** el rango completo de Unicode. Al encontrar caracteres fuera del soporte de `inputenc`, lanza el error:

```
LaTeX Error: Unicode character ✓ (U+2713) not set up for use with LaTeX.
LaTeX Error: Unicode character π (U+03C0) not set up for use with LaTeX.
```

Esto ocurre incluso con `[utf8]{inputenc}` porque dicho paquete solo mapea los bloques que han sido declarados explícitamente (Latin-1, Latin Extended-A/B, etc.). Los símbolos matemáticos, letras griegas y símbolos especiales Unicode no están incluidos.

**La Solución:**

Existen dos enfoques:

### Opción A — Cambiar a XeLaTeX o LuaLaTeX (soporte Unicode nativo)

Sustituir `pdflatex` por `xelatex` o `lualatex` en la compilación. Estos motores soportan Unicode completo de forma nativa sin `inputenc`:

```latex
% Reemplazar:
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}

% Por (para xelatex/lualatex):
\usepackage{fontspec}
\setmainfont{Latin Modern Roman}
```

Compilar con:
```bash
xelatex informe.tex
```

### Opción B — Convertir Unicode a comandos LaTeX antes de generar el .tex (recomendada para generación programática)

Cuando el `.tex` se genera desde Python, aplicar un mapa de sustitución Unicode → LaTeX **antes** de escribir el archivo. Esto mantiene compatibilidad con `pdflatex`:

```python
_UNICODE_TO_LATEX = [
    ("π", "$\\pi$"),   ("α", "$\\alpha$"), ("β", "$\\beta$"),
    ("Δ", "$\\Delta$"), ("θ", "$\\theta$"), ("λ", "$\\lambda$"),
    ("μ", "$\\mu$"),   ("ω", "$\\omega$"), ("Ω", "$\\Omega$"),
    ("≤", "$\\leq$"),  ("≥", "$\\geq$"),  ("≠", "$\\neq$"),
    ("±", "$\\pm$"),   ("×", "$\\times$"), ("²", "$^{2}$"),
    ("³", "$^{3}$"),   ("°", "$^{\\circ}$"),
    ("✓", "$\\checkmark$"),  # requiere \usepackage{amssymb}
    ("→", "$\\rightarrow$"), ("↑", "$\\uparrow$"),
    # ... (ver execution/generar_informe.py para la lista completa)
]

def tex(s: str) -> str:
    # Paso 1: Unicode → LaTeX
    for char, repl in _UNICODE_TO_LATEX:
        s = s.replace(char, repl)
    # Paso 2: escapar chars especiales LaTeX SOLO en texto plano
    # (respetar los bloques $…$ ya convertidos)
    parts = s.split("$")
    result = []
    for i, part in enumerate(parts):
        if i % 2 == 0:  # texto plano
            for char, repl in _LATEX_ESCAPE:
                part = part.replace(char, repl)
        result.append(part)
    return "$".join(result)
```

> **Importante:** El orden es crítico. Se debe sustituir los símbolos Unicode **antes** de escapar los caracteres especiales de LaTeX (`$`, `{`, `}`, `_`, etc.), de lo contrario los comandos LaTeX generados (`$\pi$`) quedan con sus `$` escapados como `\$\pi\$` y no funcionan.

**Síntoma adicional — títulos de `tcolorbox`:**

El mismo error aplica a los títulos de cajas `tcolorbox`. Los emojis o símbolos Unicode en el argumento `title={✓ Fortalezas}` también fallan. Solución: usar texto ASCII en los títulos o sustituirlos por comandos LaTeX válidos:

```latex
% Incorrecto:
\begin{tcolorbox}[title={✓ Fortalezas}]

% Correcto:
\begin{tcolorbox}[title={Fortalezas}]
% o con amssymb:
\begin{tcolorbox}[title={$\checkmark$ Fortalezas}]
```

---

## 6. Referencia `LastPage` indefinida en la primera compilación

**Contexto:** Uso de `\usepackage{lastpage}` con `\pageref{LastPage}` en el pie de página.

**El Problema:**

En la primera compilación, `pdflatex` aún no ha generado el archivo `.aux` con la información del total de páginas, por lo que `\pageref{LastPage}` queda sin resolver y el compilador reporta:

```
LaTeX Warning: Reference `LastPage' on page 1 undefined on input line N.
```

`latexmk` puede detener el proceso con error al detectar referencias indefinidas.

**La Solución:**

Compilar **dos veces** consecutivas. La primera pasada escribe la referencia en `.aux`; la segunda la lee y la resuelve:

```bash
pdflatex informe.tex && pdflatex informe.tex
```

Con `latexmk`, usar la opción `-f` para forzar la finalización incluso con referencias pendientes:

```bash
latexmk -pdf -f informe.tex
```

> Este comportamiento es **normal** en LaTeX y no indica un error en el documento. El PDF de la primera pasada es funcional; solo el número de páginas en el pie puede aparecer como `??`.

## 7. Letras Griegas y Símbolos Matemáticos Unicode en texto plano (ej. `η`, `∝`)

**Contexto:**
Durante la compilación de un informe, puede aparecer un error relacionado con caracteres griegos o símbolos matemáticos sin escapar, por ejemplo:
```
! LaTeX Error: Unicode character η (U+03B7) not set up for use with LaTeX.
! LaTeX Error: Unicode character ∝ (U+221D) not set up for use with LaTeX.
```

**El Problema:**
Este error ocurre cuando caracteres Unicode correspondientes a letras griegas (como `η`, `α`, `β`, etc.) o símbolos matemáticos (como `∝`) se insertan directamente en el texto del documento `.tex` en lugar de utilizar su comando en modo matemático. `pdflatex` configurado con `utf8` no soporta la representación directa de estos caracteres.

**La Solución:**
1. **Corrección manual:** Buscar el carácter conflictivo en el archivo `.tex` y reemplazarlo por su equivalente en modo matemático. En este caso, cambiar `η` por `$\eta$` o `∝` por `$\propto$`.
2. **Prevención programática:** Asegurarse de que el script en Python que genera el documento (ej. `generar_informe.py`) incluya el mapeo correspondiente en su lista de conversiones `_UNICODE_TO_LATEX` para interceptarlo antes de escribir el archivo:
```python
    ("η", "$\\eta$"),
    ("∝", "$\\propto$"),
```
