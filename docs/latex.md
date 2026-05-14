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
