import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine_bytedance.catalog import load_catalog  # noqa: E402


def test_both_families_are_catalogued():
    catalog = load_catalog()
    image = [s for s in catalog.specs() if s.category == "IMG"]
    video = [s for s in catalog.specs() if s.category == "VID"]
    assert len(image) >= 3
    assert len(video) >= 3
    assert catalog.status(image[0].model) == "experimental"


def test_images_are_sync_and_video_uses_the_content_array():
    for spec in load_catalog().specs():
        if spec.category == "IMG":
            assert spec.mode == "sync"
            assert spec.api_path == "images/generations"
            assert spec.payload_style == "flat"
        else:
            assert spec.mode == "async"
            assert spec.api_path == "contents/generations/tasks"
            assert spec.payload_style == "content_array"


def test_the_key_environment_variable_is_ark():
    from engine_bytedance import metadata

    assert metadata.API_KEY_ENV_VAR == "ARK_API_KEY"
