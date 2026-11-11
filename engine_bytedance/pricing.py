"""Cost of a Seedance 2.5 clip from BytePlus's token pricing (Get started/Pricing.md)."""

from typing import Any

SEEDANCE_25 = "dreamina-seedance-2-5-260628"
_PER_MILLION = {"480p": 10.70, "720p": 10.70, "1080p": 11.70}
# Width x height BytePlus lists for each resolution and ratio (Seedance 2.5 tutorial).
_PIXELS = {
    "480p": {"16:9": (854, 480), "4:3": (752, 560), "1:1": (640, 640), "3:4": (560, 752), "9:16": (480, 854), "21:9": (992, 432)},
    "720p": {"16:9": (1280, 720), "4:3": (1112, 834), "1:1": (960, 960), "3:4": (834, 1112), "9:16": (720, 1280), "21:9": (1470, 630)},
    "1080p": {"16:9": (1920, 1080), "4:3": (1664, 1248), "1:1": (1440, 1440), "3:4": (1248, 1664), "9:16": (1080, 1920), "21:9": (2206, 946)},
}
_FPS = 24


def estimate_cost(endpoint: str, parameters: dict[str, Any]) -> float:
    """US dollars for one clip without video input; raises where BytePlus gives no price."""
    if endpoint != SEEDANCE_25:
        raise ValueError(f"no price known for {endpoint!r}")
    resolution = "480p" if parameters.get("draft") else str(parameters.get("resolution") or "720p").lower()
    if resolution not in _PER_MILLION:
        raise ValueError(f"no price known for resolution {resolution!r}")
    ratio = str(parameters.get("ratio") or "adaptive")
    # An adaptive clip takes the shape of its input, which is not known here.
    width, height = _PIXELS[resolution].get(ratio, _PIXELS[resolution]["16:9"])
    tokens = float(parameters.get("duration") or 5) * width * height * _FPS / 1024
    return tokens * _PER_MILLION[resolution] / 1e6
