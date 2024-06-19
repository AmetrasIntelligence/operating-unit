# Copyright 2024 Ametras intelligence GmbH (https://www.ametras.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Purchase Order Sequence by Operating Unit",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "category": "Sales",
    "author": "Ametras intelligence GmbH, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/operating-unit",
    "maintainer": "Ametras intelligence GmbH",
    "summary": "Custom Purchase Order Sequence by Operating Unit",
    "depends": ["purchase", "operating_unit"],
    "data": ["views/operating_unit_view.xml"],
    "installable": True,
    "post_init_hook": "assign_ou_sequences",
}
