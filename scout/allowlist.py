"""Lista de exclusión: rutas que legítimamente contienen secretos de ejemplo.

Todo escáner de secretos necesita esto: un repo tiene fixtures de test, ejemplos de
documentación, y datos falsos a propósito. Sin una forma de excluirlos, el escáner
grita en cada corrida y la gente lo apaga — y un escáner apagado no encuentra nada.

Se lee de `.secretscout.yaml` en la raíz del repo:

    ignore_paths:
      - "tests/**"
      - "rules/rules.yaml"

Es una lista de exclusión por RUTA, no de secretos: nunca listás el secreto en sí
(eso sería otra copia), listás dónde vive el ejemplo conocido.
"""
from __future__ import annotations

import fnmatch
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

CONFIG = ".secretscout.yaml"


def cargar_ignore(repo: str) -> list[str]:
    ruta = Path(repo) / CONFIG
    if not ruta.exists() or yaml is None:
        return []
    datos = yaml.safe_load(ruta.read_text(encoding="utf-8")) or {}
    return list(datos.get("ignore_paths", []))


def esta_ignorada(ruta: str, patrones: list[str]) -> bool:
    # Coincide contra el glob completo y contra cada prefijo de directorio, para que
    # "tests/**" atrape "tests/data/x.txt" igual que fnmatch de la ruta entera.
    for pat in patrones:
        if fnmatch.fnmatch(ruta, pat):
            return True
        # soporte simple de "dir/**"
        if pat.endswith("/**") and (ruta == pat[:-3] or ruta.startswith(pat[:-2])):
            return True
    return False
