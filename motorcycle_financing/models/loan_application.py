from odoo import models, fields, api, exceptions
from datetime import date


class LoanApplication(models.Model):
    _name = 'loan.application'
    _description = 'Loan Application'
    _order = 'date_application desc'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(compute="_compute_display_name")
    currency_id = fields.Many2one('res.currency', related="sale_order_id.currency_id", readonly=True, store=True)
    date_application = fields.Date(string="Application Date", readonly=True, copy=False)
    date_approval = fields.Date(string="Approval Date", readonly=True, copy=False)
    date_rejection = fields.Date(string="Rejection Date", readonly=True, copy=False)
    date_signed = fields.Datetime(string="Signed On", readonly=True, copy=False)
    date_sent = fields.Date(string="Date Sent", readonly=True, copy=False)
    down_payment = fields.Monetary(string="Down Payment", required=True, currency_field='currency_id')
    interest_rate = fields.Float(string="Interest Rate (%)", required=True, digits=(5, 2))
    loan_term = fields.Integer(string="Loan Term (Months)", required=True, default=36)
    rejection_reason = fields.Text(string="Rejection Reason", copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        # ('review', 'Credit Check'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        # ('signed', 'Signed'),
        ('cancel', 'Canceled'),
    ], string="Status", default='draft', copy=False)
    notes = fields.Html(string="Notes", copy=False)
    document_ids = fields.One2many('loan.application.document', 'application_id', string='Documents')
    tag_ids = fields.Many2many('loan.application.tag', string='Tags')
    partner_id = fields.Many2one(related="sale_order_id.partner_id", readonly=True, store=True)
    partner_name = fields.Char(related="partner_id.name", readonly=True, store=True)
    sale_order_id = fields.Many2one('sale.order', string='Related Sale Order')
    user_id = fields.Many2one(related="sale_order_id.user_id", readonly=True, store=True)
    product_id = fields.Many2one('product.template', string='Motorcycle')
    sale_order_total = fields.Monetary(related="sale_order_id.amount_total", readonly=True, store=True)

    _sql_constraints = [
        ('check_down_payment', 'CHECK(down_payment >= 0)', 'Down payment cannot be negative.'),
        ('check_loan_amount', 'CHECK(loan_amount >= 0)', 'Loan amount cannot be negative.')
    ]

    @api.depends("sale_order_total", "down_payment")
    def _loan_amount_computation(self):
        for loan in self:
            loan.loan_amount = loan.sale_order_total - loan.down_payment

    loan_amount = fields.Monetary(string="Loan Amount", compute="_loan_amount_computation",
                                  store=True, currency_field='currency_id'
                                  )

    @api.constrains('down_payment', 'sale_order_total')
    def _check_down_payment(self):
        for record in self:
            if record.down_payment > record.sale_order_total:
                raise exceptions.ValidationError(
                    "Down payment cannot exceed the sales order total."
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

    # Sends app for approval but checking if documents are attached
    def action_send_for_approval(self):
        for loan in self:
            if not loan.document_ids:
                raise exceptions.ValidationError(
                    "It seems that some documents are missing, you can not send to approval without documents attached."
                )

            if any(doc.state != 'approved' for doc in loan.document_ids):
                raise exceptions.ValidationError(
                    "All documents must be in 'Approved' state before sending the loan for approval."
                )

            loan.write({
                'state': 'sent',
                'date_application': date.today()
            })

    # Loan approval
    def action_approve_loan(self):
        self.write({
            'state': 'approved',
            'date_approval': date.today()
        })

    # Loan rejection
    # def action_reject_loan(self, rejection_reason=False):
    #     if not rejection_reason:
    #         raise exceptions.ValidationError("Please provide a reason for rejection.")
    #
    #     self.write({
    #         'state': 'rejected',
    #         'date_rejection': date.today(),
    #         'rejection_reason': rejection_reason
    #     })

    # Loan rejection without requiring a reason
    def action_reject_loan(self):
        """ Change the loan application state to 'rejected' without requiring a reason """
        self.write({
            'state': 'rejected',
            'date_rejection': date.today()
        })

    # @api.depends("partner_id", "product_id")
    # def _compute_display_name(self):
    #     """Override Odoo's _compute_display_name to assign custom display names."""
    #     super(LoanApplication, self)._compute_display_name()  # Call base method

    #     for application in self:
    #         # If there's a sales order, use its partner and product name
    #         if application.partner_id and application.product_id:
    #             application.display_name = f"{application.partner_id.name} - {application.product_id.name}"
    #         else:
    #             application.display_name = self._assign_default_name(application)

    @api.depends("partner_id", "product_id", "sale_order_id.order_line.product_id")
    def _compute_display_name(self):
        """Compute display_name dynamically while ensuring a default value is always set."""
        res = super(LoanApplication, self)._compute_display_name()
        for application in self:
            customer_name = application.partner_id.name if application.partner_id else "Unknown Customer"
            motorcycle_name = application._get_product_name()
            application.name = f"{customer_name} - {motorcycle_name}"
            application.display_name = f"{customer_name} - {motorcycle_name}"

    def _get_product_name(self):
        """Retrieve the product name from the Sale Order based on category 'Motorcycles'."""
        if self.sale_order_id and self.sale_order_id.order_line:
            for line in self.sale_order_id.order_line:
                if line.product_id.categ_id and line.product_id.categ_id.name == "Motorcycles":
                    return line.product_id.name  # Regresa el primer producto que cumpla la condición

        return "Unknown Product"

    @api.model_create_multi
    def create(self, vals_list):
        #auto-generates required documents
        applications = super().create(vals_list)

        document_types = self.env['loan.application.document.type'].search([('active', '=', True)])

        documents_to_create = []
        for application in applications:
            for doc_type in document_types:
                documents_to_create.append({
                    'application_id': application.id,
                    'type_id': doc_type.id,
                    'name': f"{doc_type.name} - {application.name}",
                })

        if documents_to_create:
            self.env['loan.application.document'].create(documents_to_create)

        return applications