# Preview Review Checklist

Run only after `preview-images/` contains one `slide-XX.png` for every independent spec. Review the complete ordered set, not a sample.

## Set-level gate

- [ ] Preview count equals `outline.md` `slide_count`.
- [ ] Filenames are contiguous from `slide-01.png` to `slide-NN.png`.
- [ ] Every preview was generated from the matching current spec version.
- [ ] All pages use the same visual-system ID and compatible visual rules.
- [ ] The ordered set has a coherent narrative rhythm and no accidental repetition.
- [ ] The full set has been presented as an ordered gallery or contact sheet for holistic review.

## Per-slide review

- [ ] The key message is obvious within a few seconds.
- [ ] Title copy is correct and has no unintended line break.
- [ ] Body, labels, data, units, legends, citations, and footers are complete.
- [ ] Key figures match checked source material.
- [ ] Title/body hierarchy is balanced; no materially small-text risk is visible.
- [ ] Images, screenshots, and icons follow the spec and preserve required content.
- [ ] Charts communicate the intended comparison without ambiguity.
- [ ] Layout, safe margins, alignment, and whitespace match the spec.
- [ ] Nothing is cropped, clipped, or outside the 16:9 canvas.
- [ ] The page is neither overloaded nor redundant with adjacent pages.

## Rejection rule

When any item fails:

1. Mark the matching preview rejected.
2. Change `slide-specs/slide-XX.md` first.
3. Increment the recorded spec/prompt version.
4. Regenerate that preview.
5. Review it again.

Never fix a rejected preview in PPT assembly code or with a native PowerPoint overlay. All previews must pass before final generation starts.