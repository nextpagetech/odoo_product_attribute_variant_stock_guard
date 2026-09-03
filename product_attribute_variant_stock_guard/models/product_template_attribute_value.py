from odoo import models, _
from odoo.exceptions import UserError


class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"

    def unlink(self):
        """Block deletion if any related variant has stock.

        This module is optional: when installed, it enforces the rule;
        without it, Odoo behaves as usual.
        """
        StockQuant = self.env["stock.quant"].sudo()
        blocked_values = self.env["product.template.attribute.value"]

        for ptav in self:
            variants = ptav.ptav_product_variant_ids
            if not variants:
                continue

            domain = [
                ("product_id", "in", variants.ids),
                ("location_id.usage", "=", "internal"),
                "|",
                ("quantity", ">", 0.0),
                ("reserved_quantity", ">", 0.0),
            ]

            if StockQuant.search_count(domain, limit=1):
                blocked_values |= ptav

        if blocked_values:
            # Single generic message as requested.
            raise UserError(
                _(
                    "You cannot delete this variant because it has stock in inventory."
                )
            )

        return super().unlink()

