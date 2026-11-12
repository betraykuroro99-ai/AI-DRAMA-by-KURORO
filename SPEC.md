# Production specification

This is the English adaptation of storyboard-agent's production workflow, connected to the AI-drama-pound writing skill. Agents follow AGENTS.md; users can work manually in a Wan Reference interface or use the gated Python pipeline.

## 0. Writing to production

Use the writing skill to develop the brief, premise, structure, characters and script. Ask the user to approve a concrete script before production. Create a project using:

```bash
python3 tools/new_project.py demo --source examples/novel.md --ratio 9:16 --budget 200
```

The project contains `source/novel.md`, `story.json`, `anchors/voice/`, `prompts/`, `clips/`, `tails/`, `qa/`, and `exports/`. The source script is the approved baseline; do not silently rewrite it. Project files, approvals, ledger and private outputs are ignored by Git.

Resume with `python3 tools/gate.py projects/demo status`. Never overwrite an existing project or invent prior approvals.

## 1. References (anchors)

| Type | Definition |
| --- | --- |
| Character | Full body, neutral stance and expression, plain light-gray background, even light; fixes identity and clothes, not changing story actions |
| Location | Empty establishing image defining layout and lighting |
| Prop | Close view of a recurring important object; render necessary text accurately |
| Voice | Short neutral audio sample unrelated to the script; defines vocal identity only |
| Continuation | Previous accepted clip's final segment (default 4s), or its last frame |
| Combined composition | Optional reference containing several people; explicitly identify each person's location and clothing |

Keep fixtures such as lamps and curtains in the location reference. Do not register people who are only mentioned in dialogue. Only include references visible or needed in a shot. Keep the chosen visual style consistent across all generated references.

## 2. Planning and duration

Map approved text to timed actions. If the user gives a target duration, make any necessary script reduction visible before approval. Each shot needs a distinct event or emotional change. Merge adjacent continuous action when it fits the model limit.

The gated runner uses Wan 3.0, with a maximum 30-second output including continuation overlap. The separate low-level H3 and Grok adapters are not selectable runner backends. Their model limits must be checked independently before direct use.

English/Tagalog planning uses `speech_words_per_second` (default 2.2). CJK text retains a 4.5 characters/second heuristic. Read the dialogue aloud and account for pauses and actions; estimates are not guarantees. Set `dialogue_language` separately from prompt language. For Tagalog set `whisper_language: "tl"` or use `auto`.

## 3. story.json schema

See `examples/story.example.json` for six complete English shots.

| Story field | Meaning |
| --- | --- |
| `title` | Film title |
| `model` | Runner model: `wan3.0-video` |
| `ratio` | `16:9` or `9:16` |
| `dialogue_language` | Human-readable dialogue language; default English |
| `whisper_language` | whisper.cpp language code, e.g. en, tl, auto; default auto |
| `ocr_languages` | Tesseract language packs, default eng |
| `speech_words_per_second` | Positive planning rate, default 2.2 |
| `continuation_seconds` | Positive integer overlap, default 4 |
| `budget_billed_seconds` | Maximum estimated/recorded video billing seconds |
| `style` | Visual style included verbatim in every prompt |
| `sound` | Default sound directions, explicitly including silence if appropriate |
| `negative` | List of unwanted elements |
| `anchors` | Object mapping anchor keys to reference definitions |
| `shots` | Ordered shot list |

Each anchor has `name` (prompt identity), `image` (project-relative path), and `use` (what the image controls). An optional `voice` path requires `voice_text`, the sample's literal transcript, so QA can check for leakage. Voice-only anchors can omit image/use.

| Shot field | Meaning |
| --- | --- |
| `id` | Unique shot ID, such as S1 |
| `link` | none, extend, lastframe; first shot must be none |
| `duration` | Positive integer new-content seconds, excluding overlap |
| `summary` | One-sentence shot description using names directly |
| `refs` | Ordered anchor keys; order defines image numbering for this shot |
| `start_state` | Explicit opening positions/props/lighting for independent shots |
| `start_state_actual` | For chained shots: written from the previous accepted actual end state by the runner |
| `scenes` | Timed segments: `{seconds, desc}`; seconds must sum to duration |
| `dialogue` | Optional `{who, verb, text}` lines; who is an anchor key; verb defaults to says |
| `dialogue_language` | Optional per-shot override |
| `speech_words_per_second` | Optional per-shot timing-rate override |
| `sound`, `negative` | Optional sound override and additional exclusions |

Use `{anchor_key}` placeholders only in `scenes[].desc`; the builder replaces them with media labels. Write names directly in summary/start_state. `refs` can contain at most 10 image references; at most 5 voice samples are sent.

```bash
python3 tools/check_story.py projects/demo
python3 tools/check_story.py examples/story.example.json --no-files
```

Stage checks are cumulative: anchors_plan validates settings and entries; anchors_review also checks image files; voices_review also checks voice files; board checks complete shots and style/sound. Errors block the workflow. Show every warning to the user, including speech overruns and budget estimates. `--no-files` is for templates and examples, not production readiness.

## 4. Prompt construction

```bash
python3 tools/build_prompt.py projects/demo S1
python3 tools/build_prompt.py projects/demo S1 --reference-tags
```

The builder creates English instructions in this order: summary/continuation, ordered references, current state, timed segments, exact ordered dialogue, voice mapping and lip sync, sound, style, exclusions. Dialogue remains in the requested language.

The API prompt uses `Image 1`, `Video 1`, `Audio 1`. Manual Reference export uses `@image1`, `@video1`, `@audio1`. Upload media in manifest order; numbering is local to each shot. A combined image reference can identify two people, but exact speaker names must remain unambiguous in dialogue.

Manual export does not call a provider or create approvals. For automated production, `run_shot.py --plan` saves the exact prompt for approval. Any subsequent prompt change invalidates that approval for generation.

## 5. Continuity modes

| Mode | Input and behavior | Tradeoff |
| --- | --- | --- |
| none | Independent shot with image/voice references | Must describe complete opening state |
| extend | Previous clip's last 4s (configurable), plus applicable image/voice references | Better action/voice continuity; extra input and output overlap billing |
| lastframe | Previous last frame used as a first frame | No reference images/voices in inherited Wan adapter; identity/voice drift possible |

A reference image guides appearance, not an exact first frame. After every clip, inspect actual prop ownership, positions, clothes and lighting. Record the observed end state; do not write the next prompt as if a failed action succeeded.

For extend, output includes the re-rendered overlap. Assembly keeps the later clip and cuts the overlap from the earlier clip's tail to avoid duplicated or missing dialogue. The lastframe path is implemented but has not been verified here with live model output.

## 6. Generation, QA and accounting

```bash
python3 tools/run_shot.py projects/demo S1 --plan
# After explicit user approval:
python3 tools/gate.py projects/demo approve plan:S1 --note "User approved the shown prompt and estimate"
python3 tools/run_shot.py projects/demo S1
```

The runner checks tools and story data before submitting. It logs the task ID immediately, consumes the one-use approval, and writes a ledger record. It preserves all takes as `clips/S1_take1.mp4`, `S1_take2.mp4`, etc. If a submitted task cannot be fetched, run the same command again; it retrieves that task rather than submitting another one. Do not replan while a submitted task is pending.

`ledger.json` records shot, take, model, link, task_id, status, output name, estimated/billed seconds, elapsed generation time, problems and transcript. Status values are English: submitted, generated, pending_review, qa_failed, failed. A pending task counts at its estimate until actual usage is known. Actual provider prices and billing can differ.

For extend, estimate billed seconds as `new duration + 2 * overlap` (output includes overlap, and the reference input is also counted). Image and voice costs are separate. Exceeding the video-second budget stops submission. A failed submission without a task ID is distinct from a task accepted by the provider that later fails.

QA checks sampled frames for bottom-of-frame captions, transcribes dialogue with the project's Whisper language, checks order/similarity, and detects voice-sample leakage. First-line similarity threshold is 0.9; other lines use 0.75. These heuristics do not replace listening, visual review or acting judgment. A QA crash still preserves paid footage and the ledger.

Generate an optional voice reference after reference images are approved:

```bash
python3 tools/lt.py voice --out projects/demo/anchors/voice/hero.mp3 --text "The garden is quiet this morning." --instructions "Adult voice, calm, natural pace"
```

The default sample is trimmed to about 4s; the full version is retained. Never use story dialogue as sample text; models can accidentally repeat it. Keep sample transcript in voice_text. Language support depends on the selected voice provider.

## 7. Review and export

Show the clip, contact sheet, QA report and proposed actual end state. After the user approves review:<shot>:

```bash
python3 tools/run_shot.py projects/demo --accept S1 --end-state "Actual final positions, props, lighting and clothing"
```

`--take N` can choose a retained take. Human review is required even if QA passes; explain any QA failures before acceptance. Every intended shot must be accepted before requesting final assembly. After approval:

```bash
python3 tools/assemble.py projects/demo projects/demo/exports/final.mp4
```

`--upto S4` exports a reviewed prefix. `--crop-subs` centrally crops the bottom caption area and restores output dimensions; it loses picture content. The main assembler preserves the first clip's dimensions, including portrait orientation. The low-level legacy `lt.py concat` normalizes to 1280x720; use assemble.py for portrait projects.

## 8. Human confirmation gates

| Gate | Show before requesting approval | Enables |
| --- | --- | --- |
| source | Final script, duration, aspect ratio, model | Reference planning |
| anchors_plan | Reference list and image prompts | Reference image generation |
| anchors_review | Generated/uploaded reference images | Voice samples |
| voices_review | Voice samples or an explicit no-sample plan | Storyboard planning |
| board | Shot table, dialogue, durations, all warnings | Shot generation plans |
| plan:S1 | Exact prompt, media and cost estimate | One S1 submission |
| review:S1 | Actual clip, QA results and end state | Accept S1 for continuity |
| assembly | Accepted takes, export scope and crop choice | Export |

```bash
python3 tools/gate.py projects/demo request anchors_plan --summary "Reference list and prompts shown to the user"
# Only after the user explicitly agrees:
python3 tools/gate.py projects/demo approve anchors_plan --note "The user's actual approval"
# Or record requested revisions:
python3 tools/gate.py projects/demo reject anchors_plan --note "Requested changes"
```

Only pending gates can be approved. Earlier unapproved gates block downstream use. Re-requesting/rejecting an earlier gate blocks later actions until prerequisites are approved again. Each submission consumes plan approval; rerolls require a new plan. Agents must never self-approve or fabricate the user's words. Implementation/testing this repository does not authorize live production calls.

## 9. Known limitations and inherited behavior

Wan can burn unwanted text into dialogue close-ups despite exclusions. Inspect it and ask whether to reroll, accept or crop. Reference-state details can leak into every shot; neutral character anchors should contain only identity and clothing. Extension may accumulate visual drift. Tagalog pronunciation and timing require direct review.

The automated runner remains Wan-specific. Low-level direct image/voice/video experiments outside project folders do not enforce all project gates; invoke them only within the user's explicit authorization. Model availability and gateway model IDs are provider-specific. Do not represent upstream anecdotal generation results as verified results of this fork.
