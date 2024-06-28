# Copyright 2024 Ametras intelligence GmbH (https://www.ametras.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def create(self, vals):
        if vals.get("operating_unit_id", False):
            ou_id = self.env["operating.unit"].browse(vals["operating_unit_id"])
            if ou_id.purchase_sequence_id:
                vals["name"] = ou_id.purchase_sequence_id.next_by_id()
        return super().create(vals)
