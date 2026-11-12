"""Create a new project folder with the standard layout, a story.json draft and the first gate.

  new_project.py <name> [--source novel.txt] [--title "…"] [--ratio 16:9] [--budget 200]

Creates projects/<name>/ with source/ anchors/voice/ prompts/ clips/ tails/ qa/ exports/,
copies the source text to source/novel.md, writes a story.json draft (style, anchors and shots
are filled in later by Claude, each step confirmed by the human) and requests the `source` gate.
Refuses to touch an existing project.
"""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate  # noqa: E402

DIRS = ["source", "anchors/voice", "prompts", "clips", "tails", "qa", "exports"]

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("name", help="folder name: letters, digits, - or _")
    ap.add_argument("--source", help="path to the story text; can also be added later as source/novel.md")
    ap.add_argument("--title", default="")
    ap.add_argument("--ratio", default="16:9", help="16:9 (landscape) or 9:16 (portrait)")
    ap.add_argument("--budget", type=int, default=200, help="max billed video seconds for this project")
    ap.add_argument("--language", default="English", help="dialogue language (for example Tagalog)")
    ap.add_argument("--whisper-language", default="auto", help="Whisper language code: en, tl, auto, etc.")
    a = ap.parse_args()
    if a.ratio not in ("16:9", "9:16") or a.budget <= 0:
        ap.error("ratio must be 16:9 or 9:16 and budget must be positive")

    if not re.fullmatch(r"[\w-]+", a.name):
        sys.exit("Project names may contain letters, digits, underscores and hyphens only")
    proj = ROOT / "projects" / a.name
    if proj.exists():
        sys.exit(f"Project already exists: {proj}; resume it instead (nothing overwritten)")
    if a.source and not Path(a.source).is_file():
        sys.exit(f"Source text not found: {a.source}")

    for d in DIRS:
        (proj / d).mkdir(parents=True)
    if a.source:
        shutil.copyfile(a.source, proj / "source/novel.md")
    story = {
        "title": a.title or a.name,
        "model": "wan3.0-video",
        "ratio": a.ratio,
        "dialogue_language": a.language,
        "whisper_language": a.whisper_language,
        "ocr_languages": "eng",
        "speech_words_per_second": 2.2,
        "continuation_seconds": 4,
        "budget_billed_seconds": a.budget,
        "style": "",
        "sound": "",
        "negative": ["No subtitles", "No watermarks", "No complex text", "No brand logos"],
        "anchors": {},
        "shots": [],
    }
    (proj / "story.json").write_text(json.dumps(story, ensure_ascii=False, indent=1))
    gate.set_status(str(proj), "source", "pending",
                    summary=f"New project {a.name}: source {'source/novel.md' if a.source else '(not provided yet)'}, "
                            f"ratio {a.ratio}; model wan3.0-video; budget {a.budget} billed seconds")
    print(f"Created {proj}")
