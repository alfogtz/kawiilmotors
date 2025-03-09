from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class LoanApplicationDocument(models.Model):

    _name = 'loan.application.document'
    _description = 'Document related with the loan'
    _order = 'sequence'

    sequence = fields.Integer(string="sequence", default=10)

    name = fields.Char(string = 'Document name', required = True)
    application_id = fields.Many2one(
    'loan.application', string='Loan Application', ondelete="cascade")
    type_id = fields.Many2one('loan.application.document.type', string="Document Type")
    attachment = fields.Binary(string="File")
    state = fields.Selection([
        ('new', 'New'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='new', string="Status")

    @api.depends('state')
    def _compute_document_status(self):
        for record in self:
            record.is_approved = record.state == 'approved'

    is_approved = fields.Boolean(string="Is Approved?", compute="_compute_document_status", store=True)

    def action_approve_document(self):
        for record in self:
            record.state = 'approved'

    def action_reject_document(self):
        for record in self:
            record.state = 'rejected'

    def unlink(self):
        """ No permitir eliminar documentos aprobados """
        for record in self:
            if record.state == 'approved' and not self.env.user.has_group('motorcycle_financing.financing_admin'):
                raise ValidationError(_("You cannot delete an approved document."))
        return super(LoanApplicationDocument, self).unlink()