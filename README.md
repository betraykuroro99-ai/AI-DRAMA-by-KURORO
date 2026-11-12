# AI DRAMA by KURORO

An English-language workspace for developing short dramas and turning approved scripts into AI video. It combines the screenwriting workflow from **AI-drama-pound** with the reference, continuity, review and export tools from **storyboard-agent**.

**Documentation, tool messages and prompt instructions are in English. Stories and dialogue can be in any requested language, including Tagalog.** English is the default. This project does not automatically research trends or download story ideas.

## Two ways to use it

| Mode | What you do | API keys needed? |
| --- | --- | --- |
| Manual Wan Reference | Write a script, prepare images, export English prompts with `@image1` tags, then generate in your Wan interface | No keys for local planning or prompt export; your Wan service handles generation charges |
| Automated production | Approve references, voices and shots; Python calls Wan, checks clips and assembles approved takes | Your own Wan and image/voice provider credentials |

Start with one short dialogue shot to check pronunciation, performance and character consistency before generating the full film.

## Get started

```bash
git clone https://github.com/betraykuroro99-ai/AI-DRAMA-by-KURORO.git
cd AI-DRAMA-by-KURORO
```

For writing and manual prompt export, Python 3.10+ is enough. Use an agent that can read repository instructions, such as Codex or Claude Code. See [AGENTS.md](AGENTS.md), [the writing skill](skill-src/ai-short-drama-screenwriter/SKILL.md), and [the production specification](SPEC.md).

Example request:

> Develop a 90-second Tagalog family drama set in November, before Christmas. Use 2D realistic illustrated drama, refined drawn outlines and layered painterly shading. Deliver the script, reference-image prompts and six Wan Reference prompts using @image1. Write production instructions in English and dialogue in Tagalog.

The writing phase can revise the story. Once the final script is approved for production, preserve it as the source of truth; request approval for later script changes.

## Manual Wan Reference workflow

1. Develop the brief, characters and script with `skill-src/ai-short-drama-screenwriter/`.
2. Approve the script and image-reference plan. Generate or upload character, location and prop references.
3. Create a project and fill its `story.json` using [the English example](examples/story.example.json) and [SPEC.md](SPEC.md).
4. Validate and export a shot:

```bash
python3 tools/new_project.py demo --source examples/novel.md --ratio 9:16 --language English
# Fill projects/demo/story.json with approved anchors and shots first.
python3 tools/check_story.py projects/demo
python3 tools/build_prompt.py projects/demo S1 --reference-tags
```

Upload the images in the printed `ref_images` order: first file is `@image1`, second is `@image2`, and so on. Each shot's numbering starts again from its own `refs` list. A combined scene reference can describe multiple characters in its `name` and `use` fields. Reference images guide appearance; they do not lock the opening frame. Give every independent shot an explicit `start_state`.

`build_prompt.py` only prints text and a media manifest; it does not call a paid service. For an `extend` shot, a previous-video reference is also required; image references alone do not preserve action continuity. For a `lastframe` shot, use the previous last frame in first-frame mode and do not upload reference images or voices.

## Automated production setup

Requires macOS or Linux, Python 3.10+, `ffmpeg`, `ffprobe`, `whisper-cli`, a whisper.cpp multilingual model, and subtitle OCR (macOS Vision or Linux Tesseract with the `eng` language pack).

```bash
./setup.sh
cp .env.example .env
# Edit .env locally. Never paste or commit your keys.
```

On macOS, `brew install ffmpeg whisper-cpp` provides the main tools. On Linux, install FFmpeg, Tesseract and whisper.cpp using their official installation instructions. Download `ggml-large-v3-turbo.bin` from [whisper.cpp models](https://huggingface.co/ggerganov/whisper.cpp) and set `WHISPER_MODEL`.

| Setting | Purpose |
| --- | --- |
| `TOKEN_STATION_API_KEY` | Image generation and voice samples through an OpenAI-compatible gateway |
| `TOKEN_STATION_BASE_URL` | Optional gateway override; model IDs must be supported by that gateway |
| `WAN_API_KEY` | Alibaba Cloud Model Studio video generation |
| `WAN_BASE_URL` | Your Model Studio workspace endpoint |
| `WHISPER_MODEL` | Local multilingual speech-recognition model path |

Default image model: `openai/gpt-image-2`. Default voice model: `xiaomi/mimo-v2.5-tts-voicedesign`. The automated shot runner uses Wan 3.0. The low-level `lt.py video` command also retains upstream H3 and Grok adapters; these are separate experimental calls, not interchangeable backends for the gated Wan runner.

## Approvals and production

The production sequence is:

**Final script → reference plan → reference images → voices → storyboard → each shot's prompt and estimate → each shot's review → assembly.**

The agent requests approval, shows you the artifacts, and records your actual response. It must not approve its own work. An approved shot plan covers one submission. A reroll requires a new plan and approval; fetching an already-submitted task does not require paying for a second submission.

```bash
python3 tools/gate.py projects/demo status
python3 tools/run_shot.py projects/demo S1 --plan
# After the user explicitly approves:
python3 tools/gate.py projects/demo approve plan:S1 --note "User approved S1"
python3 tools/run_shot.py projects/demo S1
# Review the video and QA report, then approve review:S1 before accepting:
python3 tools/run_shot.py projects/demo --accept S1 --end-state "Describe the actual final positions and props"
# After all intended shots are accepted and assembly is approved:
python3 tools/assemble.py projects/demo projects/demo/exports/final.mp4
```

Earlier gates must be approved before the illustrated commands can run. See [SPEC.md](SPEC.md) for the complete commands and schema.

## Languages and visual style

Set `dialogue_language` to `Tagalog`, `whisper_language` to `tl` (or `auto`), and `ocr_languages` to `eng` for Latin-script caption detection. Prompts stay English while quoted dialogue stays in the chosen language. Timing uses a configurable words-per-second estimate for Tagalog/English and retains character timing for CJK text. A timed read is still required for emotional pauses and actions.

Use this style string consistently:

> 2D realistic illustrated drama, refined drawn outlines and layered painterly shading. Realistic Filipino features, delicate contour lines, textured painted backgrounds and restrained expressive animation. Preserve faces, clothing, linework and shading across every shot.

Keep changing actions and props out of neutral character identity references. Describe those states in each shot. A sample image prompt and a Tagalog workflow guide are in [docs/](docs/).

## Cost and limitations

Planning, prompt export and local tests do not generate paid media. Image, voice and video generation use your own provider accounts. Budgets are in **billed video seconds**, not finished-film seconds or dollars. An extension adds overlap and reference-input costs; the inherited estimate is `new seconds + 2 × overlap seconds`. Actual provider usage and rates can differ.

Wan may produce unwanted captions, change faces or props, or mispronounce Tagalog. OCR and transcription are checks, not guarantees. Human review remains necessary. The last-frame continuity path is retained from upstream but has not been verified here against live generation. No live provider generation was performed for this integration.

## Verification

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 tests/test_workflow.py
python3 tools/check_story.py examples/story.example.json --no-files
```

The workflow regression script uses fake Wan/speech services and a deterministic transcription stub; it exercises the real media, approval, accounting and export paths without paid requests. It requires FFmpeg and Tesseract (or the macOS OCR binary). Real transcription/model quality needs separate testing.

## Credits and license

Adapted from [POUND0423/AI-drama-pound](https://github.com/POUND0423/AI-drama-pound) and [alabulei1/storyboard-agent](https://github.com/alabulei1/storyboard-agent), both MIT licensed. This is an integration and English adaptation, not a claim of original authorship of those tools. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for pinned source commits and [LICENSE](LICENSE) for retained copyright notices.
