from odoo import fields, models

class LoanApplicationDocument(models.Model):

    _name = 'loan.application.document'
    _description = 'Document related with the loan'

    name = fields.Char(string = 'Document name', required = True)
    application_id = fields.Many2one('loan.application', string='Loan Application')
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