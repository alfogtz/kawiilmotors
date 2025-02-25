from odoo import models, fields, api

class LoanApplication(models.Model):
    _name = 'loan.application'
    _description = 'Loan Application'

    name = fields.Char(string="Application Number", required=True)
    currency_id = fields.Many2one(related="sale_order_id.currency_id", readonly=True, store=True)
    date_application = fields.Date(string="Application Date", readonly=True, copy=False)
    date_approval = fields.Date(string="Approval Date", readonly=True, copy=False)
    date_rejection = fields.Date(string="Rejection Date", readonly=True, copy=False)
    date_signed = fields.Datetime(string="Signed On", readonly=True, copy=False)
    down_payment = fields.Monetary(string="Down Payment", required=True, currency_field='currency_id')
    interest_rate = fields.Float(string="Interest Rate (%)", required=True, digits=(5, 2))
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
    document_ids = fields.One2many('loan.application.document','application_id',string='Documents')
    tag_ids = fields.Many2many('loan.application.tag',string='Tags')
    partner_id = fields.Many2one(related="sale_order_id.partner_id", readonly=True, store=True)
    sale_order_id = fields.Many2one('sale.order',string='Related Sale Order')
    user_id = fields.Many2one(related="sale_order_id.user_id", readonly=True, store=True)
    product_template_id = fields.Many2one('product.template', string='Product')
    sale_order_total = fields.Float(related="sale_order_id.amount_total", readonly=True, store=True)

    @api.depends("sale_order_total", "down_payment")
    def _loan_amount(self):
        for loan in self:
            loan.loan_amount = loan.sale_order_total - loan.down_payment

    loan_amount = fields.Monetary(string="Loan Amount", compute="_loan_amount_computation",
                                  store=True, currency_field='currency_id'
                                  )

    @api.depends("document_ids")
    def _compute_document_count(self):
        for record in self:
            record.document_count = len(record.document_ids)

    document_count = fields.Integer(string="Document Count", compute="_compute_document_count", store=True)

    @api.depends("document_ids", "document_ids.state")
    def _compute_document_count_approved(self):
        for record in self:
            record.document_count_approved = len(record.document_ids.filtered(lambda d: d.state == "approved"))

    document_count_approved = fields.Integer(string="Approved Documents", compute="_compute_document_count_approved",
                                             store=True)
