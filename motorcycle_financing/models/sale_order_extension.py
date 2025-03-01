from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    loan_application_id = fields.Many2one('loan.application', string="Loan Application")
    state = fields.Selection(selection_add=[
        ('loan_applied', 'Applied for Loan')
    ], ondelete={'loan_applied': 'set default'})

    loan_application_ids = fields.One2many(
        'loan.application',  # Related model
        'sale_order_id',  # Field in loan.application that links to sale.order
        string="Loan Applications"
    )

    def action_create_loan_application(self):
        """Creates a loan application pre-filled with sale order data and redirects to it."""
        self.ensure_one()  # Ensures only one sale order is selected

        # Create the loan application record with pre-filled values
        loan_application = self.env['loan.application'].create({
            'sale_order_id': self.id,  # Link to the current sale order
            'partner_id': self.partner_id.id,  # Customer
            'product_id': False,  # Not needed, will be computed dynamically
            'name': False,  # Not needed, _compute_display_name will generate it
            'loan_amount': self.amount_total,  # Total loan amount = order total - down payment
            'currency_id': self.currency_id.id,  # Currency from sale order
        })

        # Redirect to the newly created loan application form view
        return {
            'name': "Loan Application",
            'type': 'ir.actions.act_window',
            'res_model': 'loan.application',
            'res_id': loan_application.id,
            'view_mode': 'form',
            'view_id': self.env.ref('motorcycle_financing.loan_application_form_view').id,  # Ensure this exists
            'target': 'current',
        }