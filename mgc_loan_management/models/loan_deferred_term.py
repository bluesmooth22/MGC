from odoo import api, fields, models, _

class LoanDeferredTerm(models.Model):
	_name = 'loan.deferred.term'
	
	name = fields.Char()
	months = fields.Integer()
	
	deferred_line_ids = fields.One2many(comodel_name="loan.deferred.term.line", inverse_name="deferred_id", string="Deferred Term Line", required=False, )
	straight_monthly = fields.Boolean(default=False)
	
	allow_custom_adv = fields.Boolean(default=False)
	adv_less = fields.Float('Discount for Adv.')
	allow_split_adv = fields.Boolean(default=False)
	split_adv = fields.Integer('Adv. Split')
	
	@api.onchange('straight_monthly')
	def _straight_monthly(self):
		pass
	
class LoanDeferredTermLine(models.Model):
	_name = 'loan.deferred.term.line'
	
	deferred_id = fields.Many2one('loan.deferred.term')
	
	# straight_monthly = fields.Boolean(compute="_straight_monthly")
	product_category_id = fields.Many2one('product.category', 'Product Category', domain=[('parent_category', '=', True)], required=True)
	adv_payment_type = fields.Selection([('perc', 'Percentage'), ('fixed', 'Fixed')], default='perc')
	adv_payment = fields.Float('Adv. Payment')
	interest_rate = fields.Float('Interest Rate (%)')
	
	# @api.multi
	# @api.onchange('deferred_id.straight_monthly')
	# def _straight_monthly(self):
	# 	for term in self:
	# 		active_id = self.env['loan.deferred.term'].browse(self._context.get('active_ids', []))
	# 		parent = self.env['loan.deferred.term'].search([('id', '=', active_id.id)])
	# 		# term.straight_monthly = parent.straight_monthly
	# 		print parent.straight_monthly
	# 		boolean = parent.straight_monthly
	# 		return {'readonly': {'adv_payment_type': [(boolean, '=', True)]}}
			
	