from odoo import models, fields, api

class LoanApplication(models.Model):
    _name = 'loan.application'
    _description = 'Loan Application'

    name = fields.Char(string="Application Number", required=True)
    currency_id = fields.Many2one(
        'res.currency', string="Currency",
        default=lambda self: self.env.company.currency_id.id)
    date_application = fields.Date(string="Application Date", readonly=True, copy=False)
    date_approval = fields.Date(string="Approval Date", readonly=True, copy=False)
    date_rejection = fields.Date(string="Rejection Date", readonly=True, copy=False)
    date_signed = fields.Datetime(string="Signed On", readonly=True, copy=False)
    down_payment = fields.Monetary(string="Down Payment", required=True, currency_field='currency_id')
    interest_rate = fields.Float(string="Interest Rate (%)", required=True, digits=(5, 2))
    loan_amount = fields.Monetary(string="Loan Amount", required=True, currency_field='currency_id')
    loan_term = fields.Integer(string="Loan Term (Months)", required=True, default=36)
    rejection_reason = fields.Text(string="Rejection Reason", copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('review', 'Credit Check'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('signed', 'Signed'),
        ('cancel', 'Canceled'),
    ], string="Status", default='draft', copy=False)
    notes = fields.Html(string="Notes", copy=False)

    document_ids = fields.One2many(
        'loan.application.document',
        #'loan_id',
        string='Documents'
    )

    # Tags relation (Many2many)
    tag_ids = fields.Many2many(
        'loan.application.tag',
        #'loan_application_tag_rel',
        #'loan_id',
        #'tag_id',
        string='Tags'
    )

    # Relation with customers (Many2one)
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer'
    )

    # Relación con Ordenes de Venta (Many2one)
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Related Sale Order'
    )

    # Relación con Vendedores (Many2one)
    user_id = fields.Many2one(
        'res.users',
        string='Salesperson'
    )

    # Relación con Productos (Many2one)
    product_template_id = fields.Many2one(
        'product.template',
        string='Product'
    )

