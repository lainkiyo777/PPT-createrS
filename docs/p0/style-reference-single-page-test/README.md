# Style-reference single-page test

This design-contract test contains three independent page specifications that share one blue-template visual language while using distinct semantic compositions:

1. `slide-01-model-comparison.yaml`: chart-led comparison with a newly added chart.
2. `slide-02-system-architecture.yaml`: newly composed nodes and arrows.
3. `slide-03-conclusion.yaml`: low-density thesis and action path.

All pages use `template_application_mode: style-reference`, `source_slide_reference: null`, and distinct `composition_id` values. No preview PNG, final PNG, or PPTX is generated. A real build must still run preview generation, visual review, final-image generation, assembly, and QA.
