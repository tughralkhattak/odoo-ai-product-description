# -*- coding: utf-8 -*-
from unittest.mock import MagicMock, patch

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged

POST_PATH = "odoo.addons.ai_product_description.models.ai_service.requests.post"


def _fake_response(status=200, payload=None, text=""):
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = payload or {}
    resp.text = text
    return resp


def _openai_ok(content="A wonderful, high-quality product."):
    return _fake_response(payload={"choices": [{"message": {"content": content}}]})


@tagged("post_install", "-at_install")
class TestAIProductDescription(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.template"].create({"name": "Test Widget"})
        cls.icp = cls.env["ir.config_parameter"].sudo()
        cls.icp.set_param("ai_product_description.provider", "openai")
        cls.icp.set_param("ai_product_description.api_key", "test-key")

    def _wizard(self, **vals):
        vals.setdefault("product_tmpl_id", self.product.id)
        return self.env["ai.product.description.wizard"].create(vals)

    # --- configuration ---------------------------------------------------
    def test_config_uses_provider_preset(self):
        cfg = self.env["ai.product.description.service"]._get_config()
        self.assertEqual(cfg["provider"], "openai")
        self.assertEqual(cfg["base_url"], "https://api.openai.com/v1")
        self.assertTrue(cfg["model"], "A default model should always be set")

    def test_config_free_provider_defaults(self):
        self.icp.set_param("ai_product_description.provider", "groq")
        cfg = self.env["ai.product.description.service"]._get_config()
        self.assertIn("groq", cfg["base_url"])
        self.assertTrue(cfg["needs_key"])
        self.icp.set_param("ai_product_description.provider", "openai")

    # --- prompt building -------------------------------------------------
    def test_build_prompts_includes_product_context(self):
        wizard = self._wizard(keywords="eco-friendly, handmade", language="French")
        system_prompt, user_prompt = wizard._build_prompts()
        self.assertTrue(system_prompt)
        self.assertIn("Test Widget", user_prompt)
        self.assertIn("eco-friendly", user_prompt)
        self.assertIn("French", user_prompt)

    # --- action wiring ---------------------------------------------------
    def test_button_opens_wizard(self):
        action = self.product.action_ai_generate_description()
        self.assertEqual(action["res_model"], "ai.product.description.wizard")
        self.assertEqual(action["context"]["default_product_tmpl_id"], self.product.id)

    # --- happy path ------------------------------------------------------
    def test_generate_then_apply_to_sales(self):
        wizard = self._wizard()
        with patch(POST_PATH, return_value=_openai_ok("Buy this amazing widget.")) as mock_post:
            wizard.action_generate()
        mock_post.assert_called_once()
        self.assertEqual(wizard.generated_text, "Buy this amazing widget.")
        wizard.action_apply_sales()
        self.assertEqual(self.product.description_sale, "Buy this amazing widget.")

    def test_apply_ecommerce_when_unavailable_raises(self):
        wizard = self._wizard()
        wizard.generated_text = "Some description"
        if "website_description" not in self.env["product.template"]._fields:
            with self.assertRaises(UserError):
                wizard.action_apply_ecommerce()

    # --- error handling --------------------------------------------------
    def test_missing_api_key_raises_userfriendly_error(self):
        self.icp.set_param("ai_product_description.api_key", "")
        wizard = self._wizard()
        with self.assertRaises(UserError):
            wizard.action_generate()
        self.icp.set_param("ai_product_description.api_key", "test-key")

    def test_provider_http_error_raises_usererror(self):
        wizard = self._wizard()
        bad = _fake_response(
            status=401,
            payload={"error": {"message": "Invalid API key"}},
            text='{"error":{"message":"Invalid API key"}}',
        )
        with patch(POST_PATH, return_value=bad):
            with self.assertRaises(UserError):
                wizard.action_generate()

    def test_apply_before_generate_raises(self):
        wizard = self._wizard()
        with self.assertRaises(UserError):
            wizard.action_apply_sales()
