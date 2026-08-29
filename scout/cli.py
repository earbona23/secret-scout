"""secret-scout — encuentra secretos filtrados en un repositorio git.

  python -m scout.cli .                    # árbol de trabajo actual
  python -m scout.cli . --historial        # + todo el historial de commits
  python -m scout.cli . --historial --json informe.json
  python -m scout.cli . --demo             # repo de ejemplo con secretos plantados

Código de salida 1 si encuentra algo (útil como paso de CI que bloquea el merge).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scout.detect import Detector
from scout.gitscan import escanear_arbol, escanear_historial

_ROJO = "\033[91m"
_DIM = "\033[90m"
_RESET = "\033[0m"


def _render(hallazgos: list, color: bool) -> str:
    if not hallazgos:
        return "Sin secretos detectados."
    c = (lambda x, col: f"{col}{x}{_RESET}") if color else (lambda x, _c: x)
    lineas = [c(f"{len(hallazgos)} posible(s) secreto(s):", _ROJO), ""]
    for hu in hallazgos:
        d = hu.como_dict()
        lineas.append(f"  {c(d['regla'], _ROJO)}")
        lineas.append(f"    {d['fuente']}:{d['linea']}")
        lineas.append(f"    {c(d['huella'], _DIM)}  ·  entropía {d['entropia']}")
    lineas.append("")
    lineas.append("El valor NO se muestra entero a propósito: la huella permite")
    lineas.append("identificarlo sin crear otra copia del secreto.")
    return "\n".join(lineas)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Encuentra secretos filtrados en un repo git")
    p.add_argument("repo", nargs="?", default=".", help="Ruta del repositorio (por defecto: .)")
    p.add_argument("--historial", action="store_true", help="Escanear también el historial de commits")
    p.add_argument("--max-commits", type=int, default=None)
    p.add_argument("--json", type=Path, help="Escribir el informe JSON a este archivo")
    p.add_argument("--demo", action="store_true", help="Usar un repo de ejemplo con secretos plantados")
    p.add_argument("--sin-color", action="store_true")
    args = p.parse_args(argv)

    det = Detector()

    if args.demo:
        from scout.demo import crear_repo_demo
        repo = crear_repo_demo()
        args.historial = True
    else:
        repo = args.repo

    hallazgos = escanear_arbol(repo, det)
    if args.historial:
        hallazgos += escanear_historial(repo, det, args.max_commits)

    if args.json:
        args.json.write_text(
            json.dumps([h.como_dict() for h in hallazgos], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Escrito: {args.json} ({len(hallazgos)} hallazgos)", file=sys.stderr)
    else:
        print(_render(hallazgos, color=not args.sin_color))

    return 1 if hallazgos else 0


if __name__ == "__main__":
    raise SystemExit(main())
