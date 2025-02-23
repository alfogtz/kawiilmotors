from odoo import models, fields

class LoanApplicationDocumentType(models.Model):
    _name = 'loan.application.document.type'
    _description = 'Loan Application Document Type'

    name = fields.Char(string="Documents", required=True, unique=True)
    #active = fields.Boolean(string="Tags", default=True)
    tag_ids = fields.Many2many(
        'loan.application.tag',  # Reference to the tags model
        string="Tags"
    )
    document_number = fields.Integer(string="Required Document Number")
