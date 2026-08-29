from scout.allowlist import esta_ignorada


def test_glob_directorio():
    pats = ["tests/**", "rules/rules.yaml"]
    assert esta_ignorada("tests/data/x.txt", pats)
    assert esta_ignorada("rules/rules.yaml", pats)
    assert not esta_ignorada("scout/detect.py", pats)


def test_sin_patrones_no_ignora_nada():
    assert not esta_ignorada("cualquier/ruta.py", [])
