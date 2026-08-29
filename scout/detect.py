"""Motor de detección: aplica las reglas a un texto y devuelve hallazgos.

DOS DECISIONES QUE DEFINEN LA HERRAMIENTA
1. El secreto NUNCA se imprime entero. Un escáner de secretos que vuelca el secreto
   en su reporte crea una segunda copia del problema (en el log de CI, en la terminal
   compartida). Se muestra una HUELLA: los primeros y últimos caracteres, más el
   sha256, que permite reconocer y correlacionar sin revelar el valor.
2. Los patrones genéricos exigen ENTROPÍA mínima. "password = 'changeme'" no es un
   secreto; "password = 'S9v!aX2p...'" sí. La entropía de Shannon separa uno del otro
   y es lo que hace usable un patrón genérico sin ahogar en falsos positivos.
"""
from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

REGLAS = Path(__file__).resolve().parent.parent / "rules" / "rules.yaml"


def entropia_shannon(s: str) -> float:
    if not s:
        return 0.0
    frec: dict[str, int] = {}
    for c in s:
        frec[c] = frec.get(c, 0) + 1
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in frec.values())


def huella(secreto: str) -> str:
    """Reconocible pero no revelador: prefijo…sufijo + sha256 corto."""
    dig = hashlib.sha256(secreto.encode("utf-8", "replace")).hexdigest()[:12]
    if len(secreto) <= 12:
        visible = secreto[0] + "…" if secreto else "…"
    else:
        visible = f"{secreto[:4]}…{secreto[-4:]}"
    return f"{visible} (sha256:{dig})"


@dataclass
class Hallazgo:
    regla: str
    huella: str
    linea: int
    entropia: float

    def como_dict(self) -> dict:
        return {"regla": self.regla, "huella": self.huella,
                "linea": self.linea, "entropia": round(self.entropia, 2)}


class Detector:
    def __init__(self, ruta_reglas: Path | None = None) -> None:
        if yaml is None:
            raise SystemExit("Se necesita PyYAML: pip install -r requirements.txt")
        crudas = yaml.safe_load((ruta_reglas or REGLAS).read_text(encoding="utf-8")) or []
        self.reglas = [
            {"nombre": r["nombre"],
             "regex": re.compile(r["patron"]),
             "entropia_min": float(r.get("entropia", 0.0))}
            for r in crudas
        ]

    def escanear_texto(self, texto: str) -> list[Hallazgo]:
        hallazgos: list[Hallazgo] = []
        for num, linea in enumerate(texto.splitlines(), start=1):
            for regla in self.reglas:
                for m in regla["regex"].finditer(linea):
                    # El grupo capturado (si hay) es el secreto; si no, todo el match.
                    secreto = m.group(m.lastindex) if m.lastindex else m.group(0)
                    ent = entropia_shannon(secreto)
                    if ent < regla["entropia_min"]:
                        continue  # match de baja entropía: casi seguro un falso positivo
                    hallazgos.append(Hallazgo(regla["nombre"], huella(secreto), num, ent))
        return hallazgos
