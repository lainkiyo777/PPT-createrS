## Shared render contract

**Mode:** `adaptive-layout` with high template fidelity. The source slide is the visual authority.

### Template locks

- 16:9 white canvas; keep the original top title band, thin blue rule, upper-right China Huaneng logo, bottom blue rule, bottom-right angled corner and page number.
- Preserve the source palette: Huaneng blue as the primary accent, deep navy for headings, neutral black/dark gray body text, light blue-gray panels, and the existing red accent only for warnings, totals and key metrics.
- Preserve the source typography language: Microsoft YaHei/微软雅黑 or the closest installed Chinese sans-serif. Title 28–32 pt equivalent; section labels 20–22 pt; body 17–19 pt where space allows; dense tables/flows never below 14 pt; footnotes 12–14 pt. Never solve overflow by making every text box tiny.
- Preserve the source visual grammar: flat white cards, thin blue borders, blue header bars, restrained gray fills, small blue/red emphasis, simple arrows and numbered chips. No dark tech background, neon glow, 3D perspective, unrelated stock-photo style, or decorative gradients.
- Keep the template's brand bands and visual rhythm recognizable, but the page composition may be reorganized for the new content. Columns, card counts, image-to-text ratios, grouping, and reading order may change; cards may be moved, resized, merged, split, removed or added when that makes the existing content clearer. Do not invent a new claim, section or page.

### Content locks

- Every source text item in the slide prompt is verbatim and must remain verbatim. Do not translate, rewrite, summarize, add claims, remove qualifiers, change numbers, change units, or alter symbols such as `≥`, `→`, `｜`, `·`, `三措两案` and `VLM+RAG`.
- Do not invent missing field photos. Keep the exact label `待插入真实素材` in its existing frame when the source slide contains it.
- Tables, metrics, arrows, labels and chart values must be rendered by a deterministic text/vector layer after image generation. The image model may supply background treatment, card polish, non-text decoration, safe crop guidance, and diagram geometry (architecture nodes, flow connectors, swimlanes, timeline rails and chart scaffolding). It must not hallucinate Chinese text, numbers or logos. New diagrams are allowed only when they visualize information already present in the source text.
- Keep the original page number and all source footer text. Do not add a date, subtitle, slogan or watermark.

### Per-slide input

Use the matching file in `reference-slides/source-slide-XX.png` as the primary reference image. Use the source text lock and page-specific layout notes below. Return a clean 16:9 visual treatment that can receive the deterministic text/vector overlay without changing the source meaning.
