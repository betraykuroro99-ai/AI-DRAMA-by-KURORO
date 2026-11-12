"""Check story.json before it is shown to the human or used to spend money.

  check_story.py <project_dir | story.json> [--stage anchors_plan|anchors_review|voices_review|board] [--no-files]

Prints the shot table (link, seconds, estimated billed seconds, speaking time) and every problem found;
exit code 1 if there are errors. Errors block, warnings are for the human to judge.
The same check runs inside gate.py when anchors_plan, anchors_review, voices_review or board is
requested or approved, and inside run_shot.py before a shot is planned or generated, so a broken
story.json is caught before any money is spent.

Stages add up: anchors_plan = settings and anchor entries; anchors_review = + anchor image files exist;
voices_review = + voice sample files exist; board = + style, sound and every shot.
--no-files skips the "file exists" checks (for a story.json outside a project, like the example).
"""
import argparse
import json
import re
import sys
from pathlib import Path

STAGES = ["anchors_plan", "anchors_review", "voices_review", "board"]
LINKS = ("none", "extend", "lastframe")
MAX_SECONDS = 30        # Wan 3.0: longest single clip, continuation overlap included (SPEC 2)
MAX_IMAGES = 10         # Wan 3.0: reference images per clip (SPEC 7)
MAX_AUDIOS = 5          # Wan 3.0: reference voices per clip (SPEC 7)
CHARS_PER_SECOND = 4.5  # spoken Chinese (SPEC 2)


def is_num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def is_text(x):
    return isinstance(x, str) and bool(x.strip())


def speech_seconds(shot, story=None):
    """Rough planning estimate; confirm emotional dialogue with a timed read."""
    story = story or {}
    rate = shot.get("speech_words_per_second", story.get("speech_words_per_second", 2.2))
    if not is_num(rate) or rate <= 0:
        rate = 2.2
    lines = shot.get("dialogue") if isinstance(shot.get("dialogue"), list) else []
    seconds = 0.0
    for line in lines:
        if not isinstance(line, dict) or not isinstance(line.get("text"), str):
            continue
        text = line["text"]
        cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
        words = len(re.findall(r"[^\W_]+(?:['’-][^\W_]+)*", re.sub(r"[\u4e00-\u9fff]", " ", text), re.UNICODE))
        seconds += cjk / CHARS_PER_SECOND + words / rate
    return seconds


def billed_estimate(story, shot):
    """Same figure as run_shot.py: output seconds, plus the reference clip again as input for extend."""
    overlap = story.get("continuation_seconds", 4) if shot.get("link") == "extend" else 0
    return shot["duration"] + 2 * overlap


def check(proj, stage="board", files=True, story=None):
    """(errors, warnings) for story.json at the given stage."""
    if story is None:
        try:
            story = json.loads((Path(proj) / "story.json").read_text())
        except (OSError, ValueError) as e:
            return [f"Cannot read story.json: {e}"], []
    if not isinstance(story, dict):
        return ["story.json must contain a top-level object"], []
    level = STAGES.index(stage)
    errors, warnings = [], []

    if not is_text(story.get("ratio")):
        errors.append("Missing ratio (for example 16:9 or 9:16)")
    if "speech_words_per_second" in story and not (is_num(story["speech_words_per_second"]) and story["speech_words_per_second"] > 0):
        errors.append("speech_words_per_second must be positive")
    for field in ("dialogue_language", "whisper_language", "ocr_languages"):
        if field in story and not is_text(story[field]):
            errors.append(f"{field} must be nonempty text")
    overlap = story.get("continuation_seconds", 4)
    if not (isinstance(overlap, int) and not isinstance(overlap, bool) and overlap >= 1):
        errors.append("continuation_seconds must be a positive integer")
        overlap = 4
    budget = story.get("budget_billed_seconds")
    if budget is None:
        warnings.append("budget_billed_seconds is unset; generation has no budget stop")
    elif not (is_num(budget) and budget > 0):
        errors.append("budget_billed_seconds must be positive")
        budget = None

    anchors = story.get("anchors")
    if not isinstance(anchors, dict):
        errors.append("anchors must be an object (may be empty)")
        anchors = {}
    for key, a in anchors.items():
        if not re.fullmatch(r"[\w-]+", key):
            errors.append(f"Anchor key {key} may contain letters, digits, underscores and hyphens only")
        if not isinstance(a, dict):
            errors.append(f"Anchor {key} must be an object")
            continue
        if not is_text(a.get("name")):
            errors.append(f"Anchor {key} is missing name (its name in prompts)")
        for field in ("image", "voice"):
            if field in a and not is_text(a[field]):
                errors.append(f"Anchor {key}: {field} must be a project-relative file path")
        if is_text(a.get("image")):
            if not is_text(a.get("use")):
                errors.append(f"Anchor {key} has an image but no use (what it controls)")
            if files and level >= 1 and not (Path(proj) / a["image"]).is_file():
                errors.append(f"Anchor {key} image is missing: {a['image']}")
        if is_text(a.get("voice")):
            if not is_text(a.get("voice_text")):
                errors.append(f"Anchor {key} has a voice but no voice_text (sample transcript for leakage checks)")
            if files and level >= 2 and not (Path(proj) / a["voice"]).is_file():
                errors.append(f"Anchor {key} voice sample is missing: {a['voice']}")
    if level < 3:
        return errors, warnings

    if not is_text(story.get("style")):
        errors.append("Missing style (included verbatim in every prompt)")
    if not is_text(story.get("sound")):
        errors.append("Missing sound (describe default sound or explicitly request silence)")
    neg = story.get("negative")
    if not (isinstance(neg, list) and all(is_text(n) for n in neg)):
        errors.append("negative must be a list of nonempty strings (list may be empty)")
    shots = story.get("shots")
    if not (isinstance(shots, list) and shots):
        errors.append("shots is empty: no shots planned")
        return errors, warnings

    seen, total_est = set(), 0
    for i, shot in enumerate(shots):
        if not isinstance(shot, dict) or not is_text(shot.get("id")):
            errors.append(f"Shot {i + 1} is missing id")
            continue
        if "speech_words_per_second" in shot and not (is_num(shot["speech_words_per_second"]) and shot["speech_words_per_second"] > 0):
            errors.append(f"{shot['id']}: speech_words_per_second must be positive")
        if "dialogue_language" in shot and not is_text(shot["dialogue_language"]):
            errors.append(f"{shot['id']}: dialogue_language must be nonempty text")
        sid = shot["id"]
        err = lambda msg: errors.append(f"{sid}: {msg}")
        warn = lambda msg: warnings.append(f"{sid}: {msg}")
        if not re.fullmatch(r"[\w-]+", sid):
            err("id may contain letters, digits, underscores and hyphens only")
        if sid in seen:
            err("duplicate id")
        seen.add(sid)

        link = shot.get("link")
        if link not in LINKS:
            err(f"link must be one of {' / '.join(LINKS)}")
        elif i == 0 and link != "none":
            err("First shot has no predecessor; link must be none")
        dur = shot.get("duration")
        if not (isinstance(dur, int) and not isinstance(dur, bool) and dur >= 1):
            err("duration (new-content seconds) must be a positive integer")
            dur = None
        else:
            clip = dur + (overlap if link == "extend" else 0)
            if clip > MAX_SECONDS:
                err(f"Clip is {clip}s" + (f" (including {overlap}s overlap)" if link == "extend" else "") + f"; exceeds model limit of {MAX_SECONDS}s; split the shot")
            total_est += dur + (2 * overlap if link == "extend" else 0)
        if not is_text(shot.get("summary")):
            err("Missing summary (one sentence describing the shot)")
        for field in ("summary", "start_state"):
            used = [k for k in anchors if "{" + k + "}" in str(shot.get(field, ""))]
            if used:
                err(f"{field}: {{{used[0]}}} is not substituted here; write names directly (anchor placeholders work only in scenes.desc)")

        refs = shot.get("refs", [])
        if not isinstance(refs, list):
            err("refs must be a list of anchor keys")
            refs = []
        elif link == "lastframe":
            if refs:
                warn("lastframe cannot include reference images; refs will not be sent")
        else:
            if "refs" not in shot:
                err("Missing refs (visible anchors; use an empty list if none)")
            for k in refs:
                if not isinstance(k, str) or k not in anchors:
                    err(f"refs contains {k}, which is not in anchors")
                elif not is_text(anchors[k].get("image") if isinstance(anchors[k], dict) else None):
                    err(f"refs contains {k}, which has no image")
            if len(set(map(str, refs))) != len(refs):
                err("refs contains duplicate anchors")
            if len(refs) > MAX_IMAGES:
                err(f"{len(refs)} reference images exceed limit of {MAX_IMAGES}")

        scenes = shot.get("scenes")
        if not (isinstance(scenes, list) and scenes):
            err("Missing scenes (timed action segments)")
        else:
            secs = 0
            for n, sc in enumerate(scenes, 1):
                if not isinstance(sc, dict) or not (is_num(sc.get("seconds")) and sc["seconds"] > 0) or not is_text(sc.get("desc")):
                    err(f"Scene segment {n} needs positive seconds and nonempty desc")
                    secs = None
                    break
                secs += sc["seconds"]
                for k in re.findall(r"\{([^{}]*)\}", sc["desc"]):
                    if k not in anchors:
                        err(f"Scene segment {n}: {{{k}}} is not in anchors")
                    elif link != "lastframe" and k not in refs and isinstance(anchors[k], dict) and is_text(anchors[k].get("image")):
                        warn(f"Scene mentions {k} without its image in refs (name only will be used)")
            if secs is not None and dur is not None and abs(secs - dur) > 0.01:
                err(f"Scene seconds total {secs:g}; does not match duration {dur}")

        dia = shot.get("dialogue", [])
        if not isinstance(dia, list):
            err("dialogue must be a list")
            dia = []
        voiced = []
        for n, d in enumerate(dia, 1):
            if not isinstance(d, dict) or not is_text(d.get("text")):
                err(f"Dialogue line {n} is missing text")
                continue
            who = d.get("who")
            if not isinstance(who, str) or who not in anchors:
                err(f"Dialogue line {n}: speaker {who} is not in anchors")
                continue
            a = anchors[who] if isinstance(anchors[who], dict) else {}
            if "verb" in d and not is_text(d["verb"]):
                err(f"Dialogue line {n}: verb must be nonempty (default: says)")
            if link != "lastframe":
                if is_text(a.get("voice")) and who not in voiced:
                    voiced.append(who)
                if is_text(a.get("image")) and who not in refs:
                    warn(f"{who} speaks but their image is missing from refs")
        if len(voiced) > MAX_AUDIOS:
            err(f"{len(voiced)} voiced speakers exceed limit of {MAX_AUDIOS}")
        if dia and link == "lastframe":
            warn("lastframe cannot include voice samples; voices may differ from earlier shots")
        need = speech_seconds(shot, story)
        if dur is not None and need > dur:
            warn(f"Estimated dialogue takes {need:.1f}s, exceeding this shot duration of {dur}s")
        if "negative" in shot and not (isinstance(shot["negative"], list) and all(is_text(x) for x in shot["negative"])):
            err("negative must be a list of nonempty strings")
        if "sound" in shot and not is_text(shot["sound"]):
            err("sound must be nonempty (omit to use the story default)")

    if budget is not None and total_est > budget:
        warnings.append(f"One take per shot is estimated at {total_est:g} billed seconds, exceeding budget {budget:g}s")
    return errors, warnings


def table(story):
    """One line per shot, for the human at the board gate."""
    rows, total = [], 0
    for s in story.get("shots") or []:
        try:
            est = billed_estimate(story, s)
            total += est
            rows.append(f"{s['id']:6} {s['link']:9} new {s['duration']:>2}s  estimated billing {est:>2}s  dialogue ~{speech_seconds(s, story):4.1f}s  {s.get('summary', '')}")
        except (KeyError, TypeError, ValueError):
            rows.append(f"{s.get('id', '?') if isinstance(s, dict) else '?'}  (incomplete shot)")
    if rows:
        rows.append(f"Total estimated billing for one take per shot: {total:g}s; budget {story.get('budget_billed_seconds', 'unset')}s")
    return "\n".join(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="project folder, or a story.json file")
    ap.add_argument("--stage", choices=STAGES, default="board")
    ap.add_argument("--no-files", action="store_true", help="do not check that anchor files exist")
    a = ap.parse_args()
    p = Path(a.path).resolve()
    f = p if p.is_file() else p / "story.json"
    try:
        story = json.loads(f.read_text())
    except (OSError, ValueError) as e:
        sys.exit(f"Cannot read {f}: {e}")
    errors, warnings = check(f.parent, a.stage, files=not a.no_files, story=story)
    if a.stage == "board" and isinstance(story, dict):
        print(table(story))
    for w in warnings:
        print("Warning: " + w)
    for e in errors:
        print("Error: " + e)
    if errors:
        sys.exit(1)
    print(f"story.json passed ({a.stage})" + (f"; {len(warnings)} warnings" if warnings else ""))


if __name__ == "__main__":
    main()
