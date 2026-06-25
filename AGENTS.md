# AGENTS.md — Guía para Agentes de IA en BIOANALISIS

## Propósito del Proyecto

Generación, evaluación y gestión de material educativo para la asignatura **Física para Ciencias de la Salud (005-1713)** — Universidad de Oriente/Núcleo Sucre, dirigida a estudiantes de Bioanálisis.

## Estructura del Espacio de Trabajo

```
BIOANALISIS/
├── .agent/                       # Instrucciones de sistema y contexto del agente
│   ├── AGENT_FRAMEWORK.md        # Arquitectura de 3 capas (Directives, Orchestration, Execution)
│   └── AGENT_INSTRUCTIONS.md     # Rol del asistente y reglas LaTeX/Bash
├── directives/                   # Layer 1: SOPs en YAML (flujos de trabajo)
│   ├── evaluar_examen_estudiante.yaml
│   └── _template.yaml
├── execution/                    # Layer 3: Scripts deterministas en Python
│   ├── evaluar_examen.py         # Evalúa PDFs con Gemini multimodal
│   ├── generar_informe.py        # Convierte JSON de evaluación a informe .tex
│   └── alert_user.py             # Alertas audibles (success/waiting/error)
├── flujo_completo.py             # Layer 2: Orquestador del flujo de evaluación
├── examenes/                     # Exámenes organizados por unidad
│   ├── 01/                       # Unidad I
│   │   ├── examen_estudiantes/   # PDFs de exámenes de estudiantes (30)
│   │   ├── examen_sol/           # Solucionario maestro
│   │   └── evaluacion_*.pdf/tex  # Evaluaciones individuales con informe
│   ├── 02/                       # Unidad II
│   └── ...
├── tareas/                       # Infografías y problemas individuales
│   ├── problema_{1..25}.tex      # Unidad I
│   ├── problema_{1..8}_u2.tex    # Unidad II
│   ├── main.tex / main_u2.tex    # Documentos compiladores
│   └── compilar_todo.sh          # Script de compilación LaTeX
├── docs/                         # Programa de asignatura, propuestas, documentación
│   ├── latex.md                  # Registro de errores y soluciones LaTeX
│   ├── ia_salud.tex              # Propuesta: IA en Ciencias de la Salud
│   └── propuesta_ia_renal.tex    # Propuesta: IA en enfermedad renal
├── curso/                        # Archivos del curso (PDF + Excel)
├── clean_latex.py                # Limpia archivos auxiliares LaTeX
├── git-update.sh                 # Script de commit + update_repo
└── update_repo.sh                # Script de git pull/commit/push
```

## Arquitectura de 3 Capas

1. **Layer 1 — Directives (`directives/`)**: SOPs en YAML que definen _qué_ hacer. Cada archivo describe un flujo de trabajo repetible con objetivo, inputs, pasos, outputs esperados y casos límite.

2. **Layer 2 — Orchestration (`flujo_completo.py` o el agente)**: Toma de decisiones. Lee la directiva, elige scripts, ejecuta flujos multietapa, valida entradas/salidas, gestiona errores y guarda estado en `.tmp/run_state.json`.

3. **Layer 3 — Execution (`execution/`)**: Scripts Python deterministas con una sola responsabilidad. Entradas por CLI, secretos en `.env`, salidas JSON por stdout. Códigos de salida: 0=éxito, 1+=fallo.

## Convenciones Importantes

### LaTeX
- Clase base: `\documentclass[12pt,letterpaper]{article}`, márgenes 2.5cm
- Compilación con `latexmk -pdf -interaction=nonstopmode`
- Usar `\usetikzlibrary{babel}` cuando se use TikZ con babel español
- En bucles `\foreach` en TikZ, separar coordenadas como `\x/\y` (nunca `\pos` con paréntesis)
- Unidades SI formateadas con `\text{}` (ej: `9.8 \text{ m/s}^2`)
- Gravedad: `g = 9.8 \text{ m/s}^2`

### Python
- Snake_case para scripts y funciones
- Cada script = una responsabilidad
- Entradas por `argparse`, salidas JSON por stdout
- API keys desde `.env` con `python-dotenv`
- Errores con códigos de salida numerados

### Git
- Usar `git-update.sh` (add → commit → pull → push)
- No modificar `.clinerules` ni `.cursorrules`

## Flujo de Evaluación de Exámenes

```
flujo_completo.py --pdf examenes/01/examen_estudiantes/Ana_Alcala.pdf
  ├── Paso 1: evaluar_examen.py → renderiza PDF a imágenes → Gemini → JSON
  ├── Paso 2: generar_informe.py → JSON → informe LaTeX (.tex)
  └── Paso 3: alert_user.py success → notificación audible
```

Estado intermedio guardado en `.tmp/run_state.json`. Máximo 3 reintentos ante fallos.

## Variables de Entorno Requeridas

- `GOOGLE_API_KEY` — API key de Google AI Studio (obligatoria para evaluar exámenes)

## Dependencias (requirements.txt)

- `pymupdf>=1.24.0` — Renderizado de PDF a imágenes
- `google-generativeai>=0.8.0` — API Gemini
- `python-dotenv>=1.0.0` — Variables de entorno
- `pyyaml>=6.0` — Lectura de directivas YAML
