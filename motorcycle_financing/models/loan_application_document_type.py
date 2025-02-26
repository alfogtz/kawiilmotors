from odoo import models, fields

class LoanApplicationDocumentType(models.Model):
    _name = 'loan.application.document.type'
    _description = 'Loan Application Document Type'

    name = fields.Char(string="Documents", required=True, unique=True)
    active = fields.Boolean(string="Active", default=True)
    type_id = fields.Many2one("loan.application.document.type", string="Document Type")
    document_number = fields.Integer(string="Required Document Number")
