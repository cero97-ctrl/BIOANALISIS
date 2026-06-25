# BIOANALISIS — Física para Ciencias de la Salud

Generación, evaluación y gestión de material educativo para la asignatura **Física para Ciencias de la Salud (005-1713)** de la **Universidad de Oriente/Núcleo Sucre**, dirigida a estudiantes de Bioanálisis.

## Estructura del Proyecto

```
BIOANALISIS/
├── .agent/                   # Instrucciones de sistema para agentes de IA
├── directives/               # SOPs en YAML (flujos de trabajo orquestables)
├── execution/                # Scripts Python deterministas
├── examenes/                 # Exámenes organizados por unidad (01, 02, ...)
├── tareas/                   # Infografías y problemas individuales
├── docs/                     # Programa de asignatura y propuestas
├── curso/                    # Archivos del curso (PDF + Excel)
├── flujo_completo.py         # Orquestador del flujo de evaluación
├── clean_latex.py            # Limpiador de archivos auxiliares LaTeX
└── AGENTS.md                 # Guía para agentes de IA
```

## Arquitectura de 3 Capas

1. **Directivas** (`directives/`) — SOPs en YAML que definen qué hacer.
2. **Orquestación** (`flujo_completo.py`) — Toma de decisiones y ejecución multietapa.
3. **Ejecución** (`execution/`) — Scripts Python deterministas con una sola responsabilidad.

## Evaluación de Exámenes con IA

El flujo principal evalúa exámenes en PDF usando Gemini multimodal:

```bash
python3 flujo_completo.py --pdf examenes/01/examen_estudiantes/Ana_Alcala.pdf
```

Esto ejecuta: evaluar PDF → obtener JSON de evaluación → generar informe LaTeX.

## Requisitos

- Python 3.10+
- `GOOGLE_API_KEY` en `.env`
- Instalar dependencias: `pip install -r requirements.txt`

## Compilación LaTeX

```bash
cd tareas && ./compilar_todo.sh
```

Usa `latexmk -pdf -interaction=nonstopmode` como motor de compilación.

## Licencia

Material educativo de la Universidad de Oriente/Núcleo Sucre.
