from odoo import fields, models

class LoanApplicationTag(models.Model):
    _name = "loan.application.tag"
    _description = "Loan application tag"

    name = fields.Char(string="Tag name", required = True)
    color = fields.Integer(string="Color")
    _sql_constraints = [('unique_tag_name', 'unique(name)', 'Tags must be unique')
    ]