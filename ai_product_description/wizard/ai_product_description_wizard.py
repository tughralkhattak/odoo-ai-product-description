# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import html_escape

TONES = [
    ("professional", "Professional"),
    ("friendly", "Friendly"),
    ("persuasive", "Persuasive / Salesy"),
    ("luxury", "Luxury / Premium"),
    ("technical", "Technical"),
    ("playful", "Playful"),
]

LENGTHS = [
    ("short", "Short (1-2 sentences)"),
    ("medium", "Medium (one paragraph)"),
    ("long", "Long (detailed)"),
]

LENGTH_HINTS = {
    "short": "1-2 short, punchy sentences",
    "medium": "one concise paragraph",
    "long": "2-3 detailed paragraphs",
}


class AIProductDescriptionWizard(models.TransientModel):
    _name = "ai.product.description.wizard"
    _description = "AI Product Description Wizard"

    product_tmpl_id = fields.Many2one(
        "product.template", string="Product", required=True, ondelete="cascade",
    )
    tone = fields.Selection(TONES, string="Tone", default="persuasive", required=True)
    length = fields.Selection(LENGTHS, string="Length", default="medium", required=True)
    language = fields.Char(string="Language", default="English")
    keywords = fields.Char(
        string="Keywords / Selling points",
        help="Optional. Comma-separated points to emphasize (e.g. eco-friendly, handmade).",
    )
    generated_text = fields.Text(string="Generated Description")
    has_ecommerce = fields.Boolean(compute="_compute_has_ecommerce")

    @api.depends("product_tmpl_id")
    def _compute_has_ecommerce(self):
        has_field = "website_description" in self.env["product.template"]._fields
        for wizard in self:
            wizard.has_ecommerce = has_field

    def _build_prompts(self):
        self.ensure_one()
        product = self.product_tmpl_id
        attributes = []
        for line in product.attribute_line_ids:
            values = ", ".join(line.value_ids.mapped("name"))
            if values:
                attributes.append("%s: %s" % (line.attribute_id.name, values))

        system_prompt = (
            "You are an expert eCommerce copywriter. You write accurate, engaging, "
            "conversion-focused product descriptions. Never invent specifications that "
            "were not provided. Return only the description text — no titles, labels, "
            "quotation marks or markdown."
        )

        lines = [
            "Write %s for the following product." % LENGTH_HINTS[self.length],
            "Tone: %s." % dict(TONES).get(self.tone, self.tone),
            "Language: %s." % (self.language or "English"),
            "Product name: %s." % (product.name or ""),
        ]
        if product.categ_id:
            lines.append("Product category: %s." % product.categ_id.name)
        if product.description_sale:
            lines.append("Existing notes: %s." % product.description_sale)
        if attributes:
            lines.append("Attributes: %s." % "; ".join(attributes))
        if self.keywords:
            lines.append("Emphasize these selling points: %s." % self.keywords)
        return system_prompt, "\n".join(lines)

    def _reopen(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("AI Product Description"),
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_generate(self):
        self.ensure_one()
        if not self.product_tmpl_id.name:
            raise UserError(_("The product needs a name before generating a description."))
        system_prompt, user_prompt = self._build_prompts()
        self.generated_text = self.env["ai.product.description.service"].generate(
            system_prompt, user_prompt,
        )
        return self._reopen()

    def _ensure_text(self):
        if not self.generated_text:
            raise UserError(_("Please generate a description first."))

    def action_apply_sales(self):
        self.ensure_one()
        self._ensure_text()
        self.product_tmpl_id.description_sale = self.generated_text
        return {"type": "ir.actions.act_window_close"}

    def action_apply_ecommerce(self):
        self.ensure_one()
        self._ensure_text()
        product = self.product_tmpl_id
        if "website_description" not in product._fields:
            raise UserError(_("Install the eCommerce (Website) app to use this option."))
        html = "".join(
            "<p>%s</p>" % html_escape(para.strip())
            for para in self.generated_text.split("\n") if para.strip()
        )
        product.website_description = html
        return {"type": "ir.actions.act_window_close"}
