"""Embed relative images as base64 into HTML for Word."""
import base64
import re
import shutil
from pathlib import Path

HTML_IN = Path(__file__).parent / "POYASNITELNAYA_ZAPISKA_GOOGLE.html"
HTML_OUT = Path(__file__).parent / "POYASNITELNAYA_ZAPISKA_WORD.html"
HTML_DOWNLOADS = Path.home() / "Downloads" / "Пояснительная записка (Инженеры будущего).html"
DOCS = HTML_IN.parent


def main() -> None:
    text = HTML_IN.read_text(encoding="utf-8")
    pattern = re.compile(r'<img src="([^"]+)" alt="([^"]*)"(?: width="(\d+)")?')

    def repl(m: re.Match) -> str:
        src = m.group(1)
        if src.startswith("data:"):
            return m.group(0)
        path = DOCS / src.replace("\\", "/")
        alt = m.group(2)
        width = m.group(3)
        if not path.exists():
            print("MISSING:", path.name)
            return f'<p><em>[Рисунок: добавьте файл {src}]</em></p>'
        raw = path.read_bytes()
        b64 = base64.b64encode(raw).decode("ascii")
        ext = path.suffix.lower()
        mime = "image/png" if ext == ".png" else "image/jpeg"
        width_attr = f' width="{width}"' if width else ' width="600"'
        return f'<img src="data:{mime};base64,{b64}" alt="{alt}"{width_attr}'

    new_text, count = pattern.subn(repl, text)
    HTML_OUT.write_text(new_text, encoding="utf-8")
    shutil.copy2(HTML_OUT, HTML_DOWNLOADS)
    size_mb = HTML_OUT.stat().st_size / 1024 / 1024
    print(f"OK: {count} images -> {HTML_OUT.name} ({size_mb:.2f} MB)")
    print(f"Copy: {HTML_DOWNLOADS}")


if __name__ == "__main__":
    main()
