"""Prueba el recorrido REAL de git contra el repo demo (sin mocks)."""
import shutil

from scout.demo import crear_repo_demo
from scout.detect import Detector
from scout.gitscan import escanear_arbol, escanear_historial

DET = Detector()


def test_el_arbol_actual_solo_ve_lo_que_sigue_presente():
    repo = crear_repo_demo()
    try:
        arbol = escanear_arbol(repo, DET)
        reglas = {h.hallazgo.regla for h in arbol}
        # El .env con la clave de Stripe sigue en el árbol.
        assert "Stripe live secret key" in reglas
        # Las claves de AWS/GitHub fueron removidas del archivo → NO están en el árbol.
        assert "AWS Access Key ID" not in reglas
    finally:
        shutil.rmtree(repo, ignore_errors=True)


def test_el_historial_encuentra_el_secreto_ya_borrado():
    repo = crear_repo_demo()
    try:
        hist = escanear_historial(repo, DET)
        reglas = {h.hallazgo.regla for h in hist}
        # Este es EL punto: el secreto borrado del árbol sigue vivo en el commit 1.
        assert "AWS Access Key ID" in reglas
        assert "GitHub Personal Access Token" in reglas
    finally:
        shutil.rmtree(repo, ignore_errors=True)


def test_historial_no_duplica_el_mismo_secreto_en_cada_commit():
    repo = crear_repo_demo()
    try:
        hist = escanear_historial(repo, DET)
        aws = [h for h in hist if h.hallazgo.regla == "AWS Access Key ID"]
        assert len(aws) == 1, "el mismo secreto no debe repetirse por cada commit donde vive"
    finally:
        shutil.rmtree(repo, ignore_errors=True)
