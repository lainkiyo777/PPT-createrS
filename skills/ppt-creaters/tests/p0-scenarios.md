# P0 Pressure Scenarios

1. **Guided manual request:** the user asks for a formal deck but supplies no style choice. Expected behavior: emit candidates, wait for `selected-style.yaml`, and do not generate full pages early.
2. **Fast deadline:** the user asks for a quick deck. Expected behavior: `auto` may choose a mode, but config, slide specs, typography, data, and QA gates remain mandatory.
3. **Metric conflict:** two source files disagree on a KPI. Expected behavior: write `build_status: failed`; do not pick one silently and do not generate a chart.
4. **Small-text pressure:** content does not fit at 28 px body text. Expected behavior: edit, restructure, or split the page; never shrink below the token minimum.
5. **Full notes request:** the user asks for a 20-minute deck with full notes. Expected behavior: generate one note per slide, reference metric IDs, write PPTX notes, reopen and compare them, then report the duration check.
6. **Background-only request:** the user wants a fill-in template. Expected behavior: generate backgrounds and JSON guides only; do not bake long copy or immutable key figures into background images.
