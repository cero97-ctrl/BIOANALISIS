# Directives — Layer 1: Qué Hacer

Esta carpeta contiene los **SOPs (Standard Operating Procedures)** del proyecto en formato YAML.  
Cada archivo representa un flujo de trabajo repetible y orquestable por el agente.

## Estructura de una directiva

Cada archivo `.yaml` debe contener los siguientes campos:

```yaml
goal: "Descripción clara del objetivo principal"

required_inputs:
  - name: nombre_del_input
    description: "Descripción de qué datos se esperan"

steps:
  - step: 1
    description: "Qué hace este paso"
    script: "execution/nombre_script.py"
    inputs:
      argumento: "{{nombre_del_input}}"
    expected_output: "Descripción del output esperado en este paso"

expected_outputs:
  - name: nombre_del_output
    description: "Qué entrega el flujo completo"

edge_cases:
  - case: "Descripción del caso límite"
    recovery: "Protocolo de recuperación"
```

## Convenciones

- **Un archivo por flujo de trabajo.**
- **Nombres descriptivos en snake_case:** `analizar_muestra.yaml`, `generar_reporte.yaml`
- **Versioning:** Cuando cambies lógica significativamente, conserva la versión anterior:
  - `mi_directiva_v1.yaml` (vieja)
  - `mi_directiva.yaml` (activa)
- **Escribe en lenguaje natural**, como si entrenaras a alguien que nunca vio el flujo.

## Directivas disponibles

| Directiva | Descripción |
|---|---|
| `evaluar_examen_estudiante.yaml` | Evaluación preliminar de un examen en PDF usando Gemini multimodal. Retorna puntaje sugerido, observaciones por pregunta y retroalimentación formativa. |
