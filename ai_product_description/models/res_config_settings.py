# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ai_pd_provider = fields.Selection(
        selection=[
            ("groq", "Groq (free API key)"),
            ("gemini", "Google Gemini (free tier)"),
            ("openrouter", "OpenRouter (free models available)"),
            ("ollama", "Ollama (local, free, no key)"),
            ("openai", "OpenAI"),
            ("anthropic", "Anthropic (Claude)"),
        ],
        string="AI Provider",
        default="groq",
        config_parameter="ai_product_description.provider",
    )
    ai_pd_api_key = fields.Char(
        string="API Key",
        config_parameter="ai_product_description.api_key",
    )
    ai_pd_model = fields.Char(
        string="Model",
        config_parameter="ai_product_description.model",
        help="Leave empty to use a sensible default for the selected provider.",
    )
    ai_pd_base_url = fields.Char(
        string="API Base URL",
        config_parameter="ai_product_description.base_url",
        help="Advanced: override the provider endpoint. Leave empty for the default.",
    )
    ai_pd_temperature = fields.Float(
        string="Creativity",
        default=0.7,
        config_parameter="ai_product_description.temperature",
        help="0 = precise and factual, 1 = more creative.",
    )
