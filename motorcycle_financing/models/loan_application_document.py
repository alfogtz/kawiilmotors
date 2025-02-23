from odoo import fields, models

class LoanApplicationDocument(models.Model):

    _name = 'loan.application.document'
    _description = 'Document related with the loan'

    name = fields.char(string = 'Document name', required = True)
    application_id = fields.Many2one('loan.application', string='Loan Application')
    type_id = fields.Many2one('loan.application.document.type', string="Document Type")
    attachment = fields.Binary(string="File")
    state = fields.Selection([
        ('new', 'New'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='new', string="Status")