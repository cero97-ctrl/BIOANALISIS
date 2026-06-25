# Execution — Layer 3: Hacer el Trabajo

Esta carpeta contiene los **scripts deterministas en Python** del proyecto.  
Cada script tiene una sola responsabilidad y es invocado por el agente (Layer 2) según las directivas (Layer 1).

## Contrato de cada script

Todo script en este directorio debe cumplir:

| Requisito | Detalle |
|---|---|
| **Entradas** | Por argumentos CLI (`argparse`) |
| **Secretos** | Desde `.env` (nunca hardcodeados) |
| **Salidas** | Por `stdout`, preferiblemente JSON |
| **Código 0** | Éxito |
| **Código 1+** | Fallo categorizado (cada tipo de error tiene su código) |
| **Validación** | El script valida sus propias salidas antes de terminar |
| **Fallo ruidoso** | Si algo está mal, lanza excepción clara; nunca falla silenciosamente |
| **Sin razonamiento** | No improvisa lógica; ejecución confiable y repetible |

## Scripts disponibles

| Script | Descripción |
|---|---|
| `alert_user.py` | Emite alertas audibles al usuario (`success`, `waiting`, `error`) |
| `evaluar_examen.py` | Evalúa exámenes en PDF enviando las páginas como imágenes al modelo Gemini (multimodal). Retorna JSON con puntaje sugerido, observaciones por pregunta y retroalimentación. |
| `generar_informe.py` | Convierte el JSON de `evaluar_examen.py` en un informe académico profesional en formato LaTeX (`.tex`). Acepta `--json <ruta>` o stdin. |

## Convenciones de nombres

- **snake_case** para todos los scripts: `procesar_datos.py`, `generar_reporte.py`
- **Verbos en infinitivo** que describan la acción: `extraer_`, `validar_`, `transformar_`, `exportar_`
- **Un script = una responsabilidad**

## Antes de crear un nuevo script

1. Revisa esta carpeta: ¿ya existe algo reutilizable?
2. Si existe, adapta los argumentos en la directiva.
3. Solo si no hay alternativa, crea uno nuevo y actualiza esta tabla.
