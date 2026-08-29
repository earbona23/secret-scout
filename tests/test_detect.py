from scout.detect import Detector, entropia_shannon, huella

DET = Detector()


def test_atrapa_los_ejemplos_de_cada_regla():
    """Cada regla trae un ejemplo ficticio; todas deben dispararse con su propio ejemplo."""
    from pathlib import Path

    import yaml
    reglas = yaml.safe_load((Path(__file__).resolve().parent.parent / "rules" / "rules.yaml").read_text())
    for r in reglas:
        h = DET.escanear_texto(r["ejemplo"].replace("|", ""))  # rejuntar el token partido
        assert any(x.regla == r["nombre"] for x in h), f"la regla '{r['nombre']}' no atrapa su propio ejemplo"


def test_huella_no_revela_el_secreto_entero():
    secreto = "ghp_1234567890abcdefghijklmnopqrstuvwx12"
    f = huella(secreto)
    assert secreto not in f, "la huella NUNCA debe contener el secreto completo"
    assert "sha256:" in f and "ghp_" in f


def test_password_de_baja_entropia_no_se_reporta():
    # "changeme" tiene baja entropía: la regla genérica exige 4.2 y debe descartarlo.
    h = DET.escanear_texto('password = "changeme"')
    assert not any(x.regla.startswith("Generic") for x in h)


def test_password_de_alta_entropia_si_se_reporta():
    h = DET.escanear_texto('password = "S9v!aX2p_Qz7Lm3RtWc8Yb1Nf6Kd0Hj"')
    assert any(x.regla.startswith("Generic") for x in h)


def test_entropia_ordena_bien():
    assert entropia_shannon("aaaaaaaa") < entropia_shannon("aB3$xK9p")
