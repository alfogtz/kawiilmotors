from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    application_ids = fields.One2many(
        'loan.application', 'partner_id', string="Loan Applications"
    )

    application_count = fields.Integer(
        string="Loan Applications Count",
        compute="_compute_application_count",
        store=True
    )

    @api.depends('application_ids')
    def _compute_application_count(self):
        for partner in self:
            partner.application_count = len(partner.application_ids)

    def action_view_loans(self):
        """Opens a filtered list of loan applications for this customer."""
        self.ensure_one()
        return {
            'name': 'Loan Applications',
            'type': 'ir.actions.act_window',
            'res_model': 'loan.application',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }