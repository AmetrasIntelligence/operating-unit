# Copyright 2024 Ametras intelligence GmbH (https://www.ametras.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class OperatingUnit(models.Model):
    _inherit = "operating.unit"

    purchase_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Purchase Order Sequence",
        help="Sequence of purchase order with this operating unit",
    )
