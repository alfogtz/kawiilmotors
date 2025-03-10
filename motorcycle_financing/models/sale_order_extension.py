from odoo import models, fields, api, exceptions


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    loan_application_id = fields.One2many('loan.application', 'sale_order_id', string="Loan Application")
    state = fields.Selection(selection_add=[
        ('loan_applied', 'Applied for Loan')
    ], ondelete={'loan_applied': 'set default'})

    loan_application_ids = fields.One2many(
        'loan.application',  # Related model
        'sale_order_id',  # Field in loan.application that links to sale.order
        string="Loan Applications"
    )

    is_financed = fields.Boolean(string="Financing?", default=False)

    def action_create_loan_application(self):
        """Opens the loan application form pre-filled with sale order data."""
        self.ensure_one()  # Ensure only one sale order is processed at a time

        # Validate motorcycle presence and uniqueness
        motorcycle_product = self._get_motorcycle_product()

        # Prepare context with default values
        context = self._prepare_loan_application_context(motorcycle_product)

        # Change state to "Applied for Loan"
        self.write({'state': 'loan_applied'})

        return {
            'name': "Loan Application",
            'type': 'ir.actions.act_window',
            'res_model': 'loan.application',
            'view_mode': 'form',
            'view_id': self.env.ref('motorcycle_financing.loan_application_form_view').id,  # Ensure this exists
            'target': 'current',
            'context': context,
        }

    def _prepare_loan_application_context(self, motorcycle_product):
        """Prepara los valores por defecto para la solicitud de préstamo."""
        self.ensure_one()

        return {
            'default_sale_order_id': self.id,
            # Eliminamos 'default_product_id' para evitar duplicaciones
            'default_name': f"{self.partner_id.name} - {motorcycle_product.name}",
            'default_currency_id': self.currency_id.id,
            'default_loan_amount': self.amount_total,
        }

    def _get_motorcycle_product(self):
        """Retrieves the actual motorcycle product record from the sale order lines."""
        self.ensure_one()

        # Filter sale.order.line to find products in the "Motorcycles" category
        motorcycle_lines = self.order_line.filtered(lambda line: line.product_id.categ_id.name == "Motorcycles")

        if not motorcycle_lines:
            raise exceptions.UserError("A motorcycle must be included in the order to apply for a loan.")

        if len(motorcycle_lines) > 1:
            raise exceptions.UserError("Only one motorcycle can be included per loan application.")

        return motorcycle_lines.product_id.product_tmpl_id