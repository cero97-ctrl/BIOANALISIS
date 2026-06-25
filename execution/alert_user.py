#!/usr/bin/env python3
"""
alert_user.py — Notification Protocol (Layer 3: Execution)

Emite una alerta audible al usuario según el tipo de evento.
Invocado por el agente (Layer 2) antes de notificar al usuario.

Uso:
    python3 execution/alert_user.py success
    python3 execution/alert_user.py waiting
    python3 execution/alert_user.py error

Códigos de salida:
    0 — Alerta emitida correctamente
    1 — Tipo de alerta inválido
    2 — Error al emitir la alerta (sistema de audio no disponible)
"""

import sys
import json
import subprocess
from datetime import datetime

ALERT_TYPES = {
    "success": {
        "message": "✅ Flujo completado exitosamente.",
        "beeps": 2,
        "freq": 880,
        "duration": 200,
    },
    "waiting": {
        "message": "⏳ El agente está esperando tu entrada.",
        "beeps": 3,
        "freq": 660,
        "duration": 150,
    },
    "error": {
        "message": "❌ Se detectó un error. Revisión requerida.",
        "beeps": 4,
        "freq": 440,
        "duration": 300,
    },
}


def emit_beep(freq: int, duration_ms: int, count: int) -> bool:
    """Emite beeps usando 'beep' o fallback con 'paplay' / '\a'."""
    try:
        for _ in range(count):
            subprocess.run(
                ["beep", "-f", str(freq), "-l", str(duration_ms)],
                check=True,
                capture_output=True,
            )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    try:
        for _ in range(count):
            subprocess.run(
                ["paplay", "/usr/share/sounds/freedesktop/stereo/bell.oga"],
                check=True,
                capture_output=True,
            )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Último recurso: terminal bell
    for _ in range(count):
        sys.stderr.write("\a")
    sys.stderr.flush()
    return True


def main():
    if len(sys.argv) < 2:
        result = {
            "status": "error",
            "code": 1,
            "message": "Uso: alert_user.py <success|waiting|error>",
            "timestamp": datetime.utcnow().isoformat(),
        }
        print(json.dumps(result))
        sys.exit(1)

    alert_type = sys.argv[1].lower()

    if alert_type not in ALERT_TYPES:
        result = {
            "status": "error",
            "code": 1,
            "message": f"Tipo inválido: '{alert_type}'. Opciones: {list(ALERT_TYPES.keys())}",
            "timestamp": datetime.utcnow().isoformat(),
        }
        print(json.dumps(result))
        sys.exit(1)

    cfg = ALERT_TYPES[alert_type]

    success = emit_beep(cfg["freq"], cfg["duration"], cfg["beeps"])

    result = {
        "status": "ok" if success else "warning",
        "alert_type": alert_type,
        "message": cfg["message"],
        "timestamp": datetime.utcnow().isoformat(),
    }
    print(json.dumps(result))
    sys.exit(0)


if __name__ == "__main__":
    main()
