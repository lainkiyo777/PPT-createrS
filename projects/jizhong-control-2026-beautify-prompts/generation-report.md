# Generation report — template-reference image-first demo

## Route

- Skill release: `ppt-creaters` v2.1.0
- `template_application_mode`: `style-reference`
- Source: the 14-slide technical review PPTX and its extracted source text
- Visual adapter: Codex host `image_gen` calls, one page at a time, with the matching `reference-slides/source-slide-XX.png` supplied as a visual reference
- Assembly: image-only 16:9 PPTX; one generated page image per slide; no native body text, table, or chart layout

## Evidence

- 14 source template references: `reference-slides/source-slide-01.png` … `source-slide-14.png`
- 14 prompts: `slide-prompts/slide-01.md` … `slide-14.md`
- 14 approved preview images: `generated-previews/slide-01-preview.png` … `slide-14-preview.png`
- Contact sheet: `generated-previews/all-previews-contact-sheet.png`
- Assembled deck: `presentation.pptx`

## Template application

The prompts inherit the blue/white corporate palette, title-band language, fine rules, cards, engineering diagrams, chart treatment, and restrained technology decoration. They explicitly prohibit copying source text and exact source textbox coordinates. Comparison, architecture, flow, timeline, and result pages are recomposed around the current content.

## Limitation

This checked-in demo uses the reviewed preview images as the deck's image source so the liked visual result is reproducible. It is not a claim that those files are independent high-resolution `final-images`. A production run must pass the separate preview Gate, generate a distinct `final-images/` set, and then assemble from that set.
