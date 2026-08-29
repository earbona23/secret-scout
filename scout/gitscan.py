"""Recorrido del repositorio: árbol de trabajo E historial completo de git.

POR QUÉ EL HISTORIAL IMPORTA MÁS QUE EL ÁRBOL
Borrar un secreto de un archivo y hacer commit NO lo elimina: sigue vivo en el commit
anterior, para siempre, y cualquiera con el repo lo recupera con `git show`. Escanear
solo el estado actual es la razón por la que las filtraciones sobreviven años. Por eso
esta herramienta recorre cada blob de cada commit.
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass

from scout.allowlist import cargar_ignore, esta_ignorada
from scout.detect import Detector, Hallazgo


@dataclass
class HallazgoUbicado:
    hallazgo: Hallazgo
    fuente: str        # ruta del archivo, o "commit <sha>: <ruta>"
    commit: str = ""

    def como_dict(self) -> dict:
        d = self.hallazgo.como_dict()
        d["fuente"] = self.fuente
        if self.commit:
            d["commit"] = self.commit
        return d


def _git(args: list[str], repo: str) -> str:
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, check=False)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} falló: {r.stderr.strip()}")
    return r.stdout


def escanear_arbol(repo: str, det: Detector) -> list[HallazgoUbicado]:
    """Archivos versionados en el estado ACTUAL."""
    salida: list[HallazgoUbicado] = []
    ignore = cargar_ignore(repo)
    archivos = _git(["ls-files"], repo).splitlines()
    for ruta in archivos:
        if esta_ignorada(ruta, ignore):
            continue
        try:
            contenido = _git(["show", f":{ruta}"], repo)
        except RuntimeError:
            continue
        for h in det.escanear_texto(contenido):
            salida.append(HallazgoUbicado(h, ruta))
    return salida


def escanear_historial(repo: str, det: Detector, max_commits: int | None = None) -> list[HallazgoUbicado]:
    """Cada blob de cada commit. Deduplica por (regla, huella, ruta) para no repetir
    el mismo secreto en cada commit donde sobrevive."""
    salida: list[HallazgoUbicado] = []
    ignore = cargar_ignore(repo)
    vistos: set[tuple] = set()
    args = ["log", "--pretty=format:%H", "--no-merges"]
    if max_commits:
        args += ["-n", str(max_commits)]
    commits = _git(args, repo).split()
    for sha in commits:
        archivos = _git(["show", "--pretty=format:", "--name-only", sha], repo).splitlines()
        for ruta in filter(None, archivos):
            if esta_ignorada(ruta, ignore):
                continue
            try:
                contenido = _git(["show", f"{sha}:{ruta}"], repo)
            except RuntimeError:
                continue  # el archivo no existe en ese commit (fue borrado/renombrado)
            for h in det.escanear_texto(contenido):
                clave = (h.regla, h.huella, ruta)
                if clave in vistos:
                    continue
                vistos.add(clave)
                salida.append(HallazgoUbicado(h, f"commit {sha[:8]}: {ruta}", commit=sha))
    return salida
