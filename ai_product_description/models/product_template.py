# -*- coding: utf-8 -*-
from odoo import _, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_ai_generate_description(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("AI Product Description"),
            "res_model": "ai.product.description.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_product_tmpl_id": self.id},
        }
