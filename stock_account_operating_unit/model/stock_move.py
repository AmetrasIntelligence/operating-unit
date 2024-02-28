# © 2019 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar
# © 2019 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import _, exceptions, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _generate_valuation_lines_data(
        self,
        partner_id,
        qty,
        debit_value,
        credit_value,
        debit_account_id,
        credit_account_id,
        svl_id,
        description,
    ):
        if not svl_id:
            if (
                self.operating_unit_id
                and self.operating_unit_dest_id
                and self.operating_unit_id != self.operating_unit_dest_id
                and credit_account_id != debit_account_id
            ):
                raise exceptions.UserError(
                    _(
                        "You cannot create stock moves involving separate source"
                        " and destination accounts related to different "
                        "operating units."
                    )
                )

            if not self.operating_unit_dest_id and not self.operating_unit_id:
                ou_id = (
                    self.picking_id.picking_type_id.warehouse_id.operating_unit_id.id
                )
            else:
                ou_id = False
            # This method returns a dictionary to provide
            # an easy extension hook to modify the valuation
            # lines (see purchase for an example)
            self.ensure_one()

            line_vals = {
                "name": description,
                "product_id": self.product_id.id,
                "quantity": qty,
                "product_uom_id": self.product_id.uom_id.id,
                "ref": description,
                "partner_id": partner_id,
            }

            rslt = {
                "credit_line_vals": {
                    **line_vals,
                    "balance": -credit_value,
                    "account_id": credit_account_id,
                    "operating_unit_id": ou_id
                    or self.operating_unit_id.id
                    or self.operating_unit_dest_id.id,
                },
                "debit_line_vals": {
                    **line_vals,
                    "balance": debit_value,
                    "account_id": debit_account_id,
                    "operating_unit_id": ou_id
                    or self.operating_unit_dest_id.id
                    or self.operating_unit_id.id,
                },
            }

            if credit_value != debit_value:
                # for supplier returns of product in average costing method, in anglo saxon mode
                diff_amount = debit_value - credit_value
                price_diff_account = self.env.context.get("price_diff_account")
                if not price_diff_account:
                    raise exceptions.UserError(
                        _(
                            "Configuration error. Please configure the price "
                            "difference account on the product or its category "
                            "to process this operation."
                        )
                    )

                rslt["price_diff_line_vals"] = {
                    "name": self.name,
                    "product_id": self.product_id.id,
                    "quantity": qty,
                    "product_uom_id": self.product_id.uom_id.id,
                    "balance": -diff_amount,
                    "ref": description,
                    "partner_id": partner_id,
                    "account_id": price_diff_account.id,
                    "operating_unit_id": ou_id
                    or self.operating_unit_id.id
                    or self.operating_unit_dest_id.id,
                }
                return rslt
        return super(StockMove, self)._generate_valuation_lines_data(
            partner_id,
            qty,
            debit_value,
            credit_value,
            debit_account_id,
            credit_account_id,
            svl_id,
            description,
        )

    def _action_done(self, cancel_backorder=False):
        """
        Generate accounting moves if the product being moved is subject
        to real_time valuation tracking,
        and the source or destination location are
        a transit location or is outside of the company or the source or
        destination locations belong to different operating units.
        """
        res = super(StockMove, self)._action_done(cancel_backorder)
        for move in self:

            if move.product_id.valuation == "real_time":
                # Inter-operating unit moves do not accept to
                # from/to non-internal location
                if (
                    move.location_id.company_id
                    and move.location_id.company_id == move.location_dest_id.company_id
                    and move.operating_unit_id != move.operating_unit_dest_id
                ):
                    (
                        journal_id,
                        acc_src,
                        acc_dest,
                        acc_valuation,
                    ) = move._get_accounting_data_for_valuation()

                    move_lines = move._prepare_account_move_line(
                        move.product_qty,
                        move.product_id.standard_price,
                        acc_valuation,
                        acc_valuation,
                        False,
                        _("%s - OU Move") % move.product_id.display_name,
                    )
                    am = (
                        self.env["account.move"]
                        .with_context(
                            force_company=move.location_id.company_id.id,
                            company_id=move.company_id.id,
                        )
                        .create(
                            {
                                "journal_id": journal_id,
                                "line_ids": move_lines,
                                "company_id": move.company_id.id,
                                "ref": move.picking_id and move.picking_id.name,
                                "stock_move_id": move.id,
                            }
                        )
                    )
                    am._post()
        return res
