"""Crea un repo git DEMO con secretos FICTICIOS plantados en el historial.

Sirve para dos cosas: que cualquiera vea la herramienta funcionando en un comando,
y que los tests verifiquen el recorrido de historial de verdad (no un mock). El caso
central: un secreto que se BORRA en un commit posterior pero sigue vivo en el pasado.
Todos los valores son inventados; ninguno abre nada real.
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


def _git(args: list[str], repo: str) -> None:
    subprocess.run(["git", "-C", repo, *args], check=True,
                   capture_output=True, text=True)


def crear_repo_demo() -> str:
    d = tempfile.mkdtemp(prefix="secret-scout-demo-")
    _git(["init", "-q"], d)
    _git(["config", "user.email", "demo@example.com"], d)
    _git(["config", "user.name", "Demo"], d)

    # Commit 1: se filtra una clave de AWS y un token de GitHub en la config.
    (Path(d) / "config.py").write_text(
        'AWS_KEY = "' + "AKIA" + "IOSFODNN7EXAMPLE" + '"\n'
        'GITHUB = "' + "ghp_" + "1234567890abcdefghijklmnopqrstuvwx12" + '"\n',
        encoding="utf-8",
    )
    _git(["add", "."], d)
    _git(["commit", "-qm", "add integration config"], d)

    # Commit 2: alguien "arregla" la filtración quitando las claves del archivo.
    # Parece resuelto — pero el commit 1 todavía las contiene.
    (Path(d) / "config.py").write_text(
        'AWS_KEY = os.environ["AWS_KEY"]\n'
        'GITHUB = os.environ["GITHUB_TOKEN"]\n',
        encoding="utf-8",
    )
    _git(["add", "."], d)
    _git(["commit", "-qm", "move secrets to env vars"], d)

    # Commit 3: un secreto que SIGUE en el árbol actual (un .env que no debió subirse).
    (Path(d) / ".env").write_text(
        "STRIPE=" + "sk_live_" + "abcdefghijklmnopqrstuvwx" + "\n"
        'PASSWORD="changeme"\n',  # baja entropía: NO debe reportarse (falso positivo)
        encoding="utf-8",
    )
    _git(["add", "."], d)
    _git(["commit", "-qm", "add local env"], d)
    return d
