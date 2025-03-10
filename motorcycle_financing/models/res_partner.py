from odoo import _, models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'


    application_ids = fields.One2many(comodel_name="loan.application", inverse_name="partner_id")
    application_count = fields.Integer(compute='_compute_application_count')

    @api.depends('application_ids')
    def _compute_application_count(self):
        for partner in self:
            partner.application_count = self.env['loan.application'].search_count(
                [('partner_id', '=', partner.id)]
            )

    def action_view_loan_applications(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _("Related Applications"),
            'view_mode': 'list,form',
            'res_model': 'loan.application',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }
