"""Convert .puml files to .svg via PlantUML public server."""
from __future__ import annotations

import string
import urllib.request
import zlib
from pathlib import Path

UML_DIR = Path(__file__).parent


def _encode6bit(b: int) -> str:
    if b < 10:
        return chr(48 + b)
    b -= 10
    if b < 26:
        return chr(65 + b)
    b -= 26
    if b < 26:
        return chr(97 + b)
    b -= 26
    if b == 0:
        return "-"
    if b == 1:
        return "_"
    return "?"


def _encode3bytes(b1: int, b2: int, b3: int) -> str:
    c1 = b1 >> 2
    c2 = ((b1 & 0x3) << 4) | (b2 >> 4)
    c3 = ((b2 & 0xF) << 2) | (b3 >> 6)
    c4 = b3 & 0x3F
    return "".join(_encode6bit(x) for x in (c1, c2, c3, c4))


def plantuml_encode(text: str) -> str:
    compressed = zlib.compress(text.encode("utf-8"))[2:-4]
    result = []
    for i in range(0, len(compressed), 3):
        chunk = compressed[i : i + 3]
        b1, b2, b3 = chunk[0], chunk[1] if len(chunk) > 1 else 0, chunk[2] if len(chunk) > 2 else 0
        result.append(_encode3bytes(b1, b2, b3))
    return "".join(result)


def puml_to_svg(puml_path: Path, svg_path: Path) -> None:
    source = puml_path.read_text(encoding="utf-8")
    encoded = plantuml_encode(source)
    url = f"https://www.plantuml.com/plantuml/svg/{encoded}"
    req = urllib.request.Request(url, headers={"User-Agent": "MAXBOT-uml-export/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = resp.read()
    if b"<svg" not in data[:500].lower() and b"plantuml" in data.lower():
        raise RuntimeError(f"PlantUML error for {puml_path.name}: {data[:500]!r}")
    svg_path.write_bytes(data)
    print(f"OK: {svg_path.name} ({len(data)} bytes)")


def main() -> None:
    files = [
        "use_case.puml",
        "state_chart.puml",
        "activity_training.puml",
        "deployment.puml",
        "notation_legend.puml",
    ]
    for name in files:
        puml = UML_DIR / name
        svg = UML_DIR / name.replace(".puml", ".svg")
        puml_to_svg(puml, svg)


if __name__ == "__main__":
    main()
