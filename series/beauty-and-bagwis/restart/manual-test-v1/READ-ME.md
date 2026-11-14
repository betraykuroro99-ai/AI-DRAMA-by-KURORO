# Beauty and Bagwis — Manual opening test

This pack covers the first approximately30 seconds from the beginning, plus 15-second neutral Tagalog voice references for all five main characters. It does not submit video jobs. The previous approved Wan previews remain unchanged.

## Quick start

Choose Wan3.0 Reference, portrait9:16,480p. Make three ten-second clips. For each one, upload only its listed scene image as @image1, then paste the prompt below the file header. Numbering resets with every clip. The all-character board is an appearance guide, not a scene to animate.

The optional dialogue/Clip-01-Bell-and-Foley-10s.wav supplies the existing nonverbal bell and suitcase cue for the silent opening. No new music is needed.

1. Clip01 uses 01-Market-Opening-Stone.png: visible stone snag, accidental suitcase tip and helping.
2. Clip02 uses 02-Market-Dialogue.png: notebook/biscuits exchange.
3. Clip03 uses 02-Market-Dialogue.png: understated joke and putting biscuits away.

Review actual end states before the next clip. If poses/objects differ, update the next start state or use an accepted final frame in a supported first-frame workflow. An image reference is not an exact first-frame lock. Reusing a still alone does not guarantee temporal continuation. For the same appearance, retain each character’s originalface, hair, clothes and screenposition; never upload the entire five-person board as the only scene reference.

## Audio: choose the available mode

**Native generated dialogue:** enable audio for Clips02–03 if your interface supports it. The prompts request only the exact Tagalog lines, with natural pauses. If the interface accepts voice reference uploads, use the appropriate character’s neutral15-second file, explicitly as VOICE IDENTITY ONLY. Do not ask the model to recite the reference sample. Audio input support depends on your provider/interface; the Venice Wan Reference API currently marks it unsupported. Do not assume that typing @audio1 attaches a file.

For a UI that genuinely supports audio references, upload Bagwis as @audio1 and Beauty as @audio2 for Clip02, then append: “@audio1 controls only Bagwis’s voice identity. @audio2 controls only Beauty’s voice identity. Speak only the exact script dialogue, never the reference recordings’ transcripts.” For Clip03 use Bagwis as @audio1. Keep @image1 as the stated scene image. Do not use these optional tags if there is no actual audio-reference input.

**Separate dubbing (the reviewed Wan method):** disable generated audio. Use dialogue/Clip-02-Exact-Dialogue-10s.wav and Clip-03-Exact-Dialogue-8s.wav as post-production tracks. The final two seconds of Clip03 can be trimmed or used for the meaningful gathering action; do not stretch voices. Individual opening lines are also included. These are actual story performances. The five neutral voice files are audition/conditioning references, NOT the opening’s dialogue audio. Mouth alignment is approximate with the dubbing method.

## Voice files

Beauty/Leda; Bagwis/Orus; Tomas/Algenib; Moy/Puck; Ning/Aoede, generated with Gemini3.1 Flash TTS. WAV files are exactly15 seconds, mono24kHz. MP3 copies are provided for convenient upload/listening and may include small encoder padding. Playback levels are normalized for consistent audition volume. Source performances are not sped up or slowed; trailing silence is used if the neutral performance is shorter than15 seconds. Transcripts, measured source durations and voice directions are in voice-manifest.json.

## Quality checks

The accident must show wheel-stone contact BEFORE the fall, with Beauty trying to save the case. Reject a deliberate release or push. Preserve her exact approved face. Case opens only after impact, notebook stays dry, Bagwis stays left, Beauty stays right. Keep lip movement restrained and closed during silence. Do not rush dialogue, add unrelated dialogue, or render captions/logos inside the model. Add your captions and moving Kuro Dorama logo locally after approval.

References and prompts come from the established anime-character / detailed2D painted-market design. The opening child-injury scene is excluded. No future episode scripts, secret reveal notes, API keys or private provider responses are included.
