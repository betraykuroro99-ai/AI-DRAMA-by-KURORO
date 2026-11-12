# Agent instructions

Read `SPEC.md` before production work. Use the English writing skill in `skill-src/ai-short-drama-screenwriter/SKILL.md` for story development.

## Writing and handoff

Develop a brief, premise, characters, dramatic beats and script. Preserve the user's language, episode length, budget, format and style choices. English is the default for repository instructions and generated production prompts. Quote dialogue in the user's chosen story language. Do not claim that an idea reflects current trends unless you researched them.

Once the user approves the final script, save it under the project source directory. That script becomes the production baseline. Do not silently rewrite approved dialogue during shot planning.

## Production

Create projects with `tools/new_project.py`; resume with `tools/gate.py <project> status`.
Follow the gates in SPEC.md. Show concrete references, voices, shot plans, full generation prompts and cost estimates before requesting approval. Record only real user approvals; never self-approve. A single approval covers one paid shot submission. Rerolls require another approved plan. Run the same shot command to retrieve a submitted pending task rather than submitting another one.

Review each actual clip and QA report. Record actual ending positions, clothing, props and lighting with `--accept --end-state`. Update the next prompt from that actual state. Stop for repairs if a critical story action failed.

For manual Wan Reference exports, use `build_prompt.py --reference-tags`. Upload files in manifest order and use `@image1`, `@video1`, `@audio1` as indicated. Do not pretend that an image reference is a first-frame lock or a previous-video continuation. Keep instructions English; keep the requested dialogue language.

Never print, log or commit API keys, `.env`, private production outputs, or provider responses containing credentials. Name the project when operating on more than one. Do not run live generation as a test unless the user explicitly authorized that expense.

## Changes to this repository

Keep documentation, comments, examples and tool output in English. Multilingual user-authored dialogue is allowed. Preserve third-party MIT notices. Run unit tests and the fake-provider workflow regression after changing production logic. Do not treat historical upstream validation claims as fresh tests of this fork.
