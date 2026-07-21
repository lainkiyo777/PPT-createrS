# Multi-Agent Production Contract

Use this reference when implementing or auditing orchestration, model routing, review isolation, revision rounds, and deterministic release decisions.

## 1. Authority matrix

| Capability | Orchestrator | Producer | Workers | Reviewer / Final Reviewer | Deterministic code |
|---|---:|---:|---:|---:|---:|
| Route models | yes | no | no | no | records only |
| Transition workflow state | yes | no | no | no | validates |
| Create narrative/specs/prompts | delegates | yes | bounded tasks | no | schema-checks |
| Generate visuals with image2 | delegates | requests | no | no | provenance-checks |
| Modify evaluation.json | persists returned JSON only | no | no | returns JSON without filesystem access | schema-checks |
| Decide final PASS/FAIL | no | no | no | scores/findings only | yes |
| Assemble PPTX | authorizes after prerequisites | no | no | no | assembly-only adapter |

Keep Reviewer and Final Reviewer sessions isolated and read-only. Expose only paths inside a frozen review pack. Reject all Reviewer writes and calls to `image2`, `presentation`, PPTX mutation, filesystem-write, or `apply_patch`.

## 2. State contract

`build-state.yaml` is the source of truth. `build-status.json` is a compatibility mirror. Every transition requires:

- `actor: orchestrator`
- an allowed edge
- at least one existing evidence file
- timestamp, stage, and message in `transition_history`

Allowed states are:

1. `initialized`
2. `awaiting_configuration`
3. `generating_style_candidates`
4. `awaiting_style_selection`
5. `generating_slide_specs`
6. `generating_previews`
7. `awaiting_preview_approval`
8. `generating_final_images`
9. `assembling_ppt`
10. `reviewing`
11. `revising`
12. `awaiting_human_review`
13. `final_qa`
14. `completed`
15. `failed`

An invocation may advance through work states but must stop at the next human `awaiting_*` Gate. Reject any declared transition sequence that enters two future awaiting states.

## 3. Model routing contract

Treat `agents/model-routing.json` as executable configuration. `scripts/model_router.py` must:

- return the configured role/model decision;
- escalate high/critical Slide Worker work to its declared escalation model;
- use only declared fallback models;
- fail when the requested model is unavailable and no declared available fallback exists;
- append timestamped decisions to `model-routing-manifest.json`.

The routing interface is intentionally separate from provider-specific model invocation. A host may bind the selected model to its own runtime, but it must not rewrite the recorded role or silently choose a different model.

## 4. Configuration and human Gates

The first invocation always writes `deck-config.pending.yaml`, displays all eight required fields, transitions to `awaiting_configuration`, and stops without consuming input.

Manual/guided continuation requires `deck-config.confirmed.yaml` with:

```yaml
confirmed_by: user
confirmation_timestamp: <ISO-8601>
configuration_source:
  presentation_type: user|inferred|default
  visual_style: user|inferred|default
  presentation_effect: user|inferred|default
  template_application_mode: user|inferred|default
  output_mode: user|inferred|default
  notes_mode: user|inferred|default
  target_duration_minutes: user|inferred|default
  content_density: user|inferred|default
```

Manual candidate generation requires twelve successful image2 calls: four page types for each of A, B, and C. Any missing/failed/non-image2 manifest call is fatal. User selection and preview approval are separate Gates.

## 5. Review-pack boundary

Create each `review-pack/round-XX/` once. Copy only allowed source-of-review artifacts, compute SHA-256 and byte size for every file, write `review-pack-manifest.json`, then make files read-only where supported.

Do not copy Producer logs, conversations, model identity, self-assessment, or summaries. Do not expose paths outside the pack to Reviewer sessions.

The Reviewer returns an evaluation object; it does not write the repository. The Orchestrator host persists the response append-only. Reject overwrites and Producer/Worker attempts to edit `reviews/*/evaluation.json`.

## 6. Evaluation and release Gate

Validate Reviewer JSON against `schemas/evaluation.schema.json`. Require every issue to include `id`, `severity`, `criterion`, `slides`, `finding`, `evidence`, and `required_fix`. Treat a missing or empty evidence field as a schema error that blocks passing.

Recalculate weighted score from `dimension_scores`. Ignore Reviewer-supplied `total_score` and `passed`. Apply rubric thresholds and host-generated deterministic checks exactly:

```text
pass = no evaluation errors
       and weighted score >= minimum_score
       and critical failure count <= maximum_critical_failures
       and deterministic_checks_passed is true
```

Only a `gate-decision.json` produced from this calculation may authorize `final_qa` or `completed`.

## 7. Bounded revisions

On review failure, write an immutable `artifacts/round-XX/structured-issues.json` containing only structured issues, artifact version, review phase, and timestamp. Route Producer for revision, then wait in `revising` until `revision-ready.json` records `revised_by: producer`.

Regenerate preview or final artifacts according to the recorded review phase and create a new frozen review pack. Never overwrite a prior review pack, evaluation, or artifact round. After the second failed review round, transition to `awaiting_human_review`.

## 8. Deterministic responsibilities

Keep these outside model discretion:

- schema validation and state transitions;
- file/page/image/note counts;
- PNG resolution;
- font sizing and overflow checks;
- metrics and chart-data consistency;
- chart rendering and deterministic text overlay;
- image-to-slide mapping;
- presentation object-structure validation;
- notesSlides writing, mapping, and text round-trip;
- weighted score and final PASS/FAIL.

Use `scripts/deterministic_checks.py` to aggregate check results into each review round. A missing report is a failed check, not an invitation for model judgment.

## 9. Assembly boundary

Before assembly, require final image count and notes count to equal slide count, final image QA to pass, and `selected_by: user`. Supply the assembly adapter an explicit allowlist containing only blank-deck creation, full-slide image insertion, speaker-note writing, save, reopen, and notes verification.

Reject native body text, shapes, charts, altered final images, non-full-slide image placement, missing notesSlides, mapping errors, or Markdown/PPTX note mismatches.
