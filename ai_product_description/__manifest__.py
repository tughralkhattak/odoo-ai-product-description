# -*- coding: utf-8 -*-
{
    "name": "AI Product Description Generator",
    "version": "18.0.1.0.0",
    "summary": "Generate compelling product descriptions with AI — "
               "OpenAI, Groq (free), Google Gemini (free), OpenRouter (free), Claude or local Ollama.",
    "description": """
AI Product Description Generator
================================

Write high-converting product descriptions in one click, in any tone and any
language, using the AI provider of your choice - including free ones such as
Groq, Google Gemini, OpenRouter and local Ollama.

See the full feature list and screenshots in the module description page.
""",
    "category": "Sales/Sales",
    "author": "Tughral Khattak",
    "website": "https://github.com/tughralkhattak/odoo-ai-product-description",
    "license": "LGPL-3",
    "depends": ["product"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/ai_product_description_wizard_views.xml",
        "views/res_config_settings_views.xml",
        "views/product_template_views.xml",
    ],
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": False,
    "auto_install": False,
}
