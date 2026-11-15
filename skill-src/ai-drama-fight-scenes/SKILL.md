---
name: ai-drama-fight-scenes
description: Plan and review cinematic illustrated fight sequences using approved references and Seedance 2.5 R2V, preserving Kuro Dorama continuity and spending approvals.
---

# Illustrated drama fight scenes

The user selected Seedance 2.5 Reference-to-Video for future fight scenes in Beauty and Bagwis. Keep Wan for the established dialogue workflow unless the user changes it. Do not insert fights or reveal abilities merely because this skill is available. Follow the approved script, directing, visual QA, ending and current per-generation review rules.

## Source and applicability

Adapted from the storyboard-first, character-reference and choreography approaches in [EvoLink's GPT Image 2 / Seedance workflow](https://github.com/Evolink-AI/GPT-Image-2-Seedance-2.5-Workflow), reviewed at commit `89a6b618a096df0ec8a131e67643127544355e31`. Useful sections: [grid planning](https://github.com/Evolink-AI/GPT-Image-2-Seedance-2.5-Workflow#case-2), [multi-frame sequencing](https://github.com/Evolink-AI/GPT-Image-2-Seedance-2.5-Workflow#case-10), [storyboard-first review](https://github.com/Evolink-AI/GPT-Image-2-Seedance-2.5-Workflow#case-19), and [ordered choreography](https://github.com/Evolink-AI/GPT-Image-2-Seedance-2.5-Workflow#case-25).

That repository is a guide and example collection, not a dedicated fight skill or controlled benchmark. Many demonstrations are historical Seedance 2.0 examples. Grid timing, identity preservation and correct action are instructions to verify, not established guarantees. This adaptation does not copy its creative prompts or redistribute community media.

## Prepare the fight

1. State the dramatic purpose: escape, protect someone, reveal information or change a relationship. Establish what changes because of the fight.
2. Keep the approved 2D comic illustration: bold ink outlines, flat cel shading, warm earthy palette and painted Filipino environments. Default delivery remains 9:16 at 480p. Do not switch to photorealistic action or redesign characters.
3. Build a short beat sheet: opening positions and distance, initiating action, response, readable contact or evasion, consequence, recovery and actual end state. Use only abilities and props already approved in the script.
4. Generate reference art here, avoiding Venice image charges. Prepare distinct character identities, the location and a few essential action poses. Inspect faces, left/right anatomy, prop ownership, wardrobe and lighting before video submission.
5. Prefer separate scene/pose references for clear media roles. A storyboard grid can help planning, but use R2V for sequence guidance rather than treating the whole grid as an I2V first frame. The output must be one cinematic scene, without panels or labels. Show the exact reference order and prompt for review.

## Direct readable motion

- Start with short 5–10-second requests when possible; one clear action-and-response exchange per take. Longer clips need a demonstrated reason, not padding.
- Establish screen positions and the action line. Preserve direction across cuts. Name anatomical left/right separately from screen left/right.
- Specify contact timing and resulting movement, rather than saying only "epic fight." Show the consequence before the next exchange. Characters must not pass through each other or teleport between poses.
- Use a readable wide or medium view for important body contact. Add a motivated close-up or one controlled camera move when it clarifies the beat. Do not use constant shake or rapid cutting to conceal failed action.
- Keep ordinary real-time movement. Do not introduce slow motion or stretch dialogue to fill runtime. Build excitement through decisions, reactions, impacts and shot rhythm.
- Prefer nonverbal fight takes with intentional effects. Keep established character voice identities for any approved dialogue. Verify the selected provider's audio-reference support; do not invent a separate TTS/lipsync stage or accept unrelated generated speech.

## Provider and spending

Venice's catalogue listed `seedance-2-5-reference-to-video-basic` as online during this review, with 9:16, 480p and 4–30-second outputs. Read-only quotes with one image and native audio were $0.45 for 5s and $0.90 for 10s. These are observations, not future price commitments or proof of a successful live fight test.

Recheck the live model, request schema, actual reference inputs and price before each authorized submission. Venice's catalogue description and capability flags do not consistently describe reference-video/audio handling; verify each specific field. Do not paste EvoLink model IDs, URLs, `quality`, `image_urls`, draft/upgrade or billing assumptions into a Venice request. There is no need to install EvoLink's CLI or change providers to apply the planning ideas.

This skill does not implement a Seedance backend in the repository's Wan-specific runner. Use a verified provider adapter within actual user authorization. Keep images generated here and preserve the current budget and per-clip approvals. No paid model test, reroll, draft conversion or resolution upgrade is authorized by this skill. Save the original task ID and retrieve it without duplicate submission; failed/uncertain paid takes remain accounted for.

## Review and carry continuity

Review actual footage at normal speed when available, plus enlarged frames around contact, fast turns and landings. Check faces, fingers, two distinct arms, prop sides, impact geometry, foot placement, lighting, unwanted text and speech. Do not describe sampled frames or transcription as full playback/listening.

If a necessary action failed, do not hide it with a crop that removes story meaning or pretend it succeeded in the next prompt. Prefer a valid same-time insert or revised choreography; any paid repair needs authorization. Record actual positions, injuries, props, clothing and lighting from the accepted take before planning the next one. Keep every original take and its cost.
