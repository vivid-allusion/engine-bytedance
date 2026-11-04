import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine_bytedance.catalog import load_catalog  # noqa: E402


def test_seedream_models_are_catalogued():
    catalog = load_catalog()
    assert len(catalog) >= 3
    for spec in catalog.specs():
        assert spec.category == "IMG"
        assert spec.mode == "sync"
        assert spec.api_path == "images/generations"
        assert catalog.status(spec.model) == "experimental"


def test_the_key_environment_variable_is_arks():
    from engine_bytedance import metadata

    assert metadata.API_KEY_ENV_VAR == "ARK_API_KEY"
