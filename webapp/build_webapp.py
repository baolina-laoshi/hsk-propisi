"""Собирает webapp/index.html для мини-приложения «Прописи».

В файл встраиваются слова учебника из bot.db, библиотека Hanzi Writer (MIT)
и данные черт иероглифов hanzi-writer-data (Arphic Public License, Make Me a Hanzi).

    python webapp/build_webapp.py <папка hanzi-writer> <папка hanzi-writer-data>
"""
from __future__ import annotations

import json
import re
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def main() -> None:
    writer_dir, data_dir = Path(sys.argv[1]), Path(sys.argv[2])
    con = sqlite3.connect(ROOT / "bot.db")
    rows = con.execute(
        "SELECT id, lesson_id, hieroglyph, pinyin, translation FROM words WHERE is_living = 0 ORDER BY lesson_id, id"
    ).fetchall()
    words = [{"id": i, "l": l, "h": h, "p": p, "t": t} for i, l, h, p, t in rows]
    chars = sorted({ch for w in words for ch in re.findall(r"[一-鿿]", w["h"])})
    data = {}
    for ch in chars:
        f = data_dir / f"{ch}.json"
        if f.exists():
            data[ch] = json.loads(f.read_text(encoding="utf-8"))
        else:
            print("нет данных для", ch)
    js = (writer_dir / "dist" / "hanzi-writer.min.js").read_text(encoding="utf-8")
    html = (HERE / "template.html").read_text(encoding="utf-8")
    html = html.replace("/*HANZI_WRITER*/", js.replace("</script", "<\\/script"))
    html = html.replace("/*WORDS*/", json.dumps(words, ensure_ascii=False))
    html = html.replace("/*CHARDATA*/", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    out = HERE / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"{out}: {len(words)} слов, {len(data)} иероглифов, {out.stat().st_size // 1024} КБ")


if __name__ == "__main__":
    main()
