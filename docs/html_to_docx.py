"""Конвертация полной пояснительной записки (HTML) в DOCX через Microsoft Word."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

DOCS = Path(__file__).parent
HTML_SRC = DOCS / "POYASNITELNAYA_ZAPISKA_GOOGLE.html"
HTML_EMBED = DOCS / "POYASNITELNAYA_ZAPISKA_WORD.html"
OUT_PROJECT = DOCS / "POYASNITELNAYA_ZAPISKA.docx"
OUT_DOWNLOADS = Path.home() / "Downloads" / "Пояснительная записка (Инженеры будущего).docx"

# Word: wdFormatXMLDocument = 12 (.docx)
WD_FORMAT_DOCX = 12


def _embed_images() -> None:
    from embed_images_in_html import main as embed_main

    embed_main()


def _convert_with_html2docx(html_path: Path, docx_path: Path) -> None:
    from html2docx import html2docx

    html = html_path.read_text(encoding="utf-8")
    # html2docx expects body fragment; strip outer document if needed
    start = html.find("<body>")
    end = html.rfind("</body>")
    if start != -1 and end != -1:
        html = html[start + 6 : end]
    buf = html2docx(html, title="Пояснительная записка")
    docx_path.write_bytes(buf.getvalue())


def _convert_with_word(html_path: Path, docx_path: Path) -> None:
    try:
        import win32com.client  # type: ignore
    except ImportError as e:
        raise SystemExit(
            "Нужен pywin32: pip install pywin32\n"
            "Либо откройте вручную docs/POYASNITELNAYA_ZAPISKA_WORD.html в Word → Сохранить как .docx"
        ) from e

    html_abs = str(html_path.resolve())
    docx_abs = str(docx_path.resolve())
    if docx_path.exists():
        docx_path.unlink()

    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    try:
        doc = word.Documents.Open(html_abs, ReadOnly=True)
        doc.SaveAs2(docx_abs, FileFormat=WD_FORMAT_DOCX)
        doc.Close(False)
    finally:
        word.Quit()


def main() -> int:
    if not HTML_SRC.is_file():
        print("Not found:", HTML_SRC, file=sys.stderr)
        return 1

    print("Embedding images...")
    _embed_images()

    print("Converting HTML to DOCX...")
    try:
        _convert_with_word(HTML_EMBED, OUT_PROJECT)
    except Exception as exc:
        print("Word COM unavailable, using html2docx:", exc)
        _convert_with_html2docx(HTML_EMBED, OUT_PROJECT)
    shutil.copy2(OUT_PROJECT, OUT_DOWNLOADS)

    print("Saved:", OUT_PROJECT)
    print("Saved:", OUT_DOWNLOADS)
    print("Размер:", OUT_PROJECT.stat().st_size // 1024, "KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
