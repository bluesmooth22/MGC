from odoo import api, fields, models, _

class AccountTax(models.Model):
    _inherit = 'account.tax'

    amount_type = fields.Selection(selection_add=[('vat', 'VAT')])

    @api.multi
    def _compute_amount(self, base_amount, price_unit, quantity=1.0, product=None, partner=None):
        tax = super(AccountTax, self)._compute_amount(quantity, base_amount)
        if self.amount_type == 'vat':
            return (base_amount / (1 + (self.amount / 100))) * (self.amount / 100)
	return tax
 