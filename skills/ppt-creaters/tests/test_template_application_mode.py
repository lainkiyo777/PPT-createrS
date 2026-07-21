from pathlib import Path
import importlib.util
import unittest

SKILL_ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = SKILL_ROOT / "scripts" / "template_policy.py"


def load_policy():
    spec = importlib.util.spec_from_file_location("template_policy", POLICY_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def spec(mode="style-reference", **overrides):
    value = {
        "template_application_mode": mode,
        "dominant_visual": "model comparison chart",
        "layout_flexibility": "recompose; move; resize; add chart",
        "visual_inheritance": "blue/cyan palette, Chinese sans typography, restrained geometry",
        "prohibited_inheritance": "exact source copy, source text, fixed source textbox coordinates",
        "composition_id": "comparison-recomposed",
        "layout": {"reuse_mode": "new-composition"},
    }
    value.update(overrides)
    return value


class TemplateApplicationModeTests(unittest.TestCase):
    def test_style_reference_rejects_full_duplicate_slide_mapping(self):
        policy = load_policy()
        errors = policy.validate_slide_spec_template_mode(spec(layout={"reuse_mode": "duplicate-slide"}))
        self.assertTrue(any("duplicate-slide" in error for error in errors))

    def test_style_reference_allows_empty_source_slide_reference(self):
        policy = load_policy()
        errors = policy.validate_slide_spec_template_mode(spec(source_slide_reference=""))
        self.assertEqual([], errors)

    def test_style_reference_requires_new_slide_composition(self):
        policy = load_policy()
        errors = policy.validate_slide_set_template_mode([
            spec(composition_id="same"), spec(composition_id="same"), spec(composition_id="same"),
        ])
        self.assertTrue(any("composition" in error for error in errors))

    def test_template_textboxes_cannot_fix_body_container_size(self):
        policy = load_policy()
        errors = policy.validate_slide_spec_template_mode(spec(layout_flexibility="fixed-source-textboxes"))
        self.assertTrue(any("textbox" in error or "flexibility" in error for error in errors))

    def test_comparison_page_allows_new_chart(self):
        policy = load_policy()
        errors = policy.validate_slide_spec_template_mode(spec(dominant_visual="new chart with direct labels"))
        self.assertEqual([], errors)

    def test_architecture_page_allows_new_nodes_and_arrows(self):
        policy = load_policy()
        errors = policy.validate_slide_spec_template_mode(spec(dominant_visual="new architecture nodes and arrows", layout_flexibility="add nodes; add arrows; resize modules"))
        self.assertEqual([], errors)

    def test_over_capacity_requires_recompose_or_split(self):
        policy = load_policy()
        errors = policy.validate_slide_spec_template_mode(spec(content_density="over-capacity", layout_flexibility="fixed"))
        self.assertTrue(any("capacity" in error or "split" in error for error in errors))

    def test_strict_template_requires_explicit_user_choice(self):
        policy = load_policy()
        errors = policy.validate_config_template_mode({"template_application_mode": "strict-template", "confirmation_method": "auto_inference"})
        self.assertTrue(any("strict-template" in error or "user" in error for error in errors))

    def test_uploaded_template_does_not_auto_switch_to_strict(self):
        policy = load_policy()
        self.assertEqual("style-reference", policy.normalize_template_application_mode({"template_source": "blue.pptx"}))

    def test_style_reference_retains_style_but_changes_composition(self):
        policy = load_policy()
        errors = policy.validate_slide_set_template_mode([
            spec(composition_id="comparison", dominant_visual="chart"),
            spec(composition_id="architecture", dominant_visual="nodes and arrows"),
            spec(composition_id="conclusion", dominant_visual="three-point thesis"),
        ])
        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
