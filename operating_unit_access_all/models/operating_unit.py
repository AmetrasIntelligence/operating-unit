from odoo import _, models

from odoo.exceptions import AccessError

class OperatingUnit(models.Model):

    _inherit = "operating.unit"

    def write(self, vals):
        if "active" in vals:
            if self.env.user.has_group(
                "operating_unit_access_all.group_all_operating_unit"
            ):
                return super(OperatingUnit, self.sudo()).write(vals)
            else:
                raise AccessError(
                    _(
                        "Only operating unit managers can archive / unarchive operating units!"
                    )
                )
        return super(OperatingUnit, self).write(vals)
