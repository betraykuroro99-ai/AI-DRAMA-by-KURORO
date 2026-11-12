# Tagalog dialogue and Wan Reference

Repository instructions and exported prompt scaffolding are English. Set the desired story language separately:

```bash
python3 tools/new_project.py my-drama --ratio 9:16 --language Tagalog --whisper-language tl
```

The new story includes `dialogue_language`, `whisper_language`, `ocr_languages` and `speech_words_per_second`. Use `tl` for Tagalog transcription, or `auto` when language detection is preferable. Whisper transcription and pronunciation quality are not guaranteed. Manually listen to every line.

Start at 2.2 spoken words per second, adjust from a recorded read, and leave room for pauses and nonoverlapping action. CJK text retains a separate 4.5 characters/second heuristic. These estimates are warnings, not verified performance durations.

## Reference tags

```bash
python3 tools/build_prompt.py projects/my-drama S1 --reference-tags
```

Upload the returned `ref_images` in order. The first is `@image1`, not a global project-wide image number. `refs: ["ana", "rico", "porch"]` maps to `@image1`, `@image2`, `@image3` for that shot. A single combined image may instead use one scene anchor whose description explicitly identifies both people.

Use a reference image for appearance. Use a first frame for an exact opening composition. Use a previous-video reference for continuation. These are distinct modes. The inherited Wan adapter does not combine first-frame mode with other reference media.

For independent shots, give a complete `start_state`. For continuation shots, use the previous approved clip's actual end state. Do not assume that retaining @image1 alone preserves poses, lighting changes or prop handoffs.

## Illustration reference prompt

Create a vertical 9:16 illustration of a modest Filipino veranda beside a sari-sari store at rainy November dusk. Exactly two Filipino adults: a 24-year-old daughter with black hair in a low ponytail, mustard T-shirt and blue jeans on the left; her 55-year-old father with short graying hair, navy polo and charcoal trousers seated on the right. Between them, a cream-paper bamboo star lantern with a red patch on its lower-left point rests on a wooden table. The lantern and loose battery-powered LED string are both off. Warm porch light, cool blue wet street. 2D realistic illustrated drama, refined drawn outlines and layered painterly shading, realistic proportions, textured painted backgrounds, restrained expressions. No text, subtitles, logos, extra people, snow or Christmas celebration.

For reusable character anchors, generate separate neutral full-body identity images on a light-gray background, empty hands and flat light. Keep the illustration style consistent. Use the combined scene image for setting/composition and neutral identities for stronger character control when the interface supports multiple references.

No user images or generated private film assets are bundled in the repository. Add your approved references under your ignored project folder.
