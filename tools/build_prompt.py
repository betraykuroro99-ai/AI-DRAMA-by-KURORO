"""Build an English Wan prompt and ordered media manifest from story.json.

  build_prompt.py <project_dir> <shot_id> [--reference-tags]

API mode uses Image 1 / Video 1 / Audio 1. --reference-tags exports
@image1 / @video1 / @audio1 for compatible Wan Reference web interfaces.
Upload files in the order returned by the media manifest.
"""
import argparse
import json
from pathlib import Path


def build(proj: Path, sid: str, reference_tags=False):
    story = json.loads((proj / "story.json").read_text(encoding="utf-8"))
    shot = next(s for s in story["shots"] if s["id"] == sid)
    anchors = story["anchors"]
    overlap = story.get("continuation_seconds", 4) if shot.get("link") == "extend" else 0
    lastframe = shot.get("link") == "lastframe"
    images = [] if lastframe else list(shot["refs"])
    img_no = {key: i + 1 for i, key in enumerate(images)}
    speakers = list(dict.fromkeys(d["who"] for d in shot.get("dialogue", [])))
    voice_no = {} if lastframe else {
        key: i + 1 for i, key in enumerate(k for k in speakers if anchors[k].get("voice"))
    }

    def tag(kind, number):
        return f"@{kind.lower()}{number}" if reference_tags else f"{kind} {number}"

    def who(key):
        return tag("Image", img_no[key]) if key in img_no else anchors[key]["name"]

    video = tag("Video", 1)
    prefix = f"Extend {video}, continuing: " if overlap else "Begin directly from the supplied first frame: " if lastframe else ""
    lines = [prefix + shot["summary"]]
    refs = []
    if overlap:
        refs.append(f"{video} is the previous clip's ending; continue seamlessly from its final frame")
    if lastframe:
        refs.append("The first frame is the previous clip's last frame; preserve its faces, clothing, setting and lighting")
    for key in images:
        refs.append(f"{who(key)} is {anchors[key]['name']} ({anchors[key]['use']})")
    for key, number in voice_no.items():
        refs.append(f"{tag('Audio', number)} defines the voice of {who(key)}")
    if voice_no:
        refs.append("Use audio references only for vocal identity; never repeat their sample words")
    lines.append("References: " + ("; ".join(refs) if refs else "none") + ".")
    state = (shot.get("start_state_actual") or shot.get("start_state") or "").strip()
    if state:
        if state[-1] not in ".;!?":
            state += "."
        lines.append("Current state: " + state + " Maintain these states unless an action below explicitly changes them.")
    t = 0
    index = 0
    if overlap:
        index += 1
        lines.append(f"Segment {index} (0-{overlap:g}s): continue the final frame of {video}; preserve positions and poses.")
        t = overlap
    for scene in shot["scenes"]:
        index += 1
        end = t + scene["seconds"]
        desc = scene["desc"]
        for key in anchors:
            desc = desc.replace("{" + key + "}", who(key))
        lines.append(f"Segment {index} ({t:g}-{end:g}s): {desc}")
        t = end
    dialogue = shot.get("dialogue", [])
    if dialogue:
        language = shot.get("dialogue_language", story.get("dialogue_language", "English"))
        lines.append(f'Dialogue in {language}: only these {len(dialogue)} lines, in order. The first line must be exactly "{dialogue[0]["text"]}".')
        for line in dialogue:
            lines.append(f'{who(line["who"])} {line.get("verb", "says")}: "{line["text"]}"')
        for key, number in voice_no.items():
            lines.append(f"Use {tag('Audio', number)} for {who(key)}'s voice.")
        lines.append("Only the assigned speaker speaks each line. Accurate lip sync. No overlapping speech or extra dialogue.")
    else:
        lines.append("No dialogue.")
    lines.append("Sound: " + shot.get("sound", story["sound"]))
    lines.append("Style: " + story["style"] + " Keep identities, character count, clothing, prop ownership and spatial directions consistent.")
    lines.append("Avoid: " + ", ".join(story["negative"] + shot.get("negative", [])) + ".")
    media = {
        "ref_images": [str(proj / anchors[key]["image"]) for key in images],
        "ref_audios": [str(proj / anchors[key]["voice"]) for key in voice_no],
        "duration": int(round(overlap + shot["duration"])),
    }
    return "\n".join(lines), media


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project")
    parser.add_argument("shot")
    parser.add_argument("--reference-tags", action="store_true")
    args = parser.parse_args()
    prompt, media = build(Path(args.project).resolve(), args.shot, args.reference_tags)
    print(prompt)
    print(json.dumps(media, ensure_ascii=False))
