from odoo import models, fields, api, _

data = []

class InstallmentSale(models.Model):
	_name = 'installment.sale'
	
	@api.onchange('product_category_id')
	def _get_deferred_term(self):
		term_list = []
		result = {}
		for order in self:
			if order.product_category_id:
				term_line = self.env['loan.deferred.term.line'].search(
					[('product_category_id', '=', order.product_category_id.id)])
				for line in term_line:
					result[line.id] = [(6, 0, line.deferred_id.id)]
					term_list.append(line.deferred_id.id)
				result['domain'] = {'purchase_term': [('id', 'in', term_list)]}
			else:
				result['domain'] = {'purchase_term': [('id', 'in', [])]}
		return result
	
		
	name = fields.Char()
	state = fields.Selection([('draft','Quotation'),
		('sale','Sale Order'),
		('lock', 'Locked'),
		('cancel', 'Canceled')], default='draft')

	partner_id = fields.Many2one('res.partner', 'Customer')
	order_date = fields.Date(default=fields.Date.today())
	confirmed_date = fields.Datetime()

	purchase_type = fields.Selection([('install', 'Installment'),('cash', 'Cash')], default='install')
	product_type = fields.Selection([('product', 'Product'), ('service', 'Service'), ('plan', 'Plan')], default='product')
	product_category_id = fields.Many2one('product.category', 'Product Category', domain="[('parent_category', '=', True), ('product_type', '=', product_type)]")
	pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', required=True, readonly=True, states={'draft': [('readonly', False)]})
	currency_id = fields.Many2one("res.currency", related='pricelist_id.currency_id', string="Currency", readonly=True, required=True)
	
	purchase_term = fields.Many2one('loan.deferred.term', domain=[])
	
	product_id = fields.Many2one('product.product', required=True, domain="['&', ('type', '=', product_type), '|', ('categ_id.parent_id', '=', product_category_id), ('categ_id', '=', product_category_id)]")
	lot_id = fields.Many2one('stock.production.lot')
	price_unit = fields.Float(string='Unit Price', track_visibility='always')
	discount = fields.Float()
	price_subtotal = fields.Float(string='Subtotal', track_visibility='always', compute="_price_discount")
	user_id = fields.Many2one('res.users', 'Salesperson', default=lambda self: self.env.user)
	
	amount_untaxed = fields.Monetary(string='Untaxed Amount', compute="_get_amount", store=True, track_visibility='always')
	amount_tax = fields.Monetary(string='Taxes', compute="_get_amount", store=True, track_visibility='always')
	amount_total = fields.Monetary(string='Total', compute="_get_amount", store=True, track_visibility='always')
	
	tax_id = fields.Many2many('account.tax', string='Taxes',
	                          domain=['|', ('active', '=', False), ('active', '=', True)])
	
	adv_term = fields.Selection([('orig', 'Original Adv.'), ('lessed', 'Lessed Adv.'), ('split', 'Deferred Adv.')], default='orig', string='Adv. Payment Term')
	adv_payment = fields.Float('Advance Payment', compute="_get_amount", store=True, track_visibility='always')
	for_amort_balance = fields.Float('Balance w/Interest', compute="_get_amount", store=True, track_visibility='always')
	monthly_amort = fields.Float('Amortization', compute="_get_amount", store=True, track_visibility='always')
	
	pcf = fields.Float(string='PCF', compute="_get_amount", store=True, track_visibility='always')
	total_adv = fields.Float(string='DP', compute="_get_amount", store=True, track_visibility='always')
	
	@api.depends('product_id','price_subtotal', 'purchase_term', 'adv_term')
	def _get_amount(self):
		payment_adv = None
		balance = None
		balance_w_int = None
		amort = None
		total = None
		_adv = None
		pcf = None
		total_adv = None
		untaxed = None
		tax = None
		for order in self:
			term_line = self.env['loan.deferred.term.line'].search(
				[('product_category_id', '=', order.product_category_id.id),
				 ('deferred_id', '=', order.purchase_term.id)])
			if term_line.adv_payment_type == 'perc':
				_adv = term_line.adv_payment / 100
				balance = order.price_subtotal - (order.price_subtotal * _adv)
				if order.adv_term == 'orig':
					payment_adv = order.price_subtotal * _adv
					total_adv = payment_adv
				elif order.adv_term == 'lessed' and order.purchase_term.allow_custom_adv:
					discount = (order.price_subtotal * _adv) * (order.purchase_term.adv_less / 100)
					# payment_adv = (order.price_subtotal * _adv) - discount
					payment_adv = (order.price_subtotal * _adv) * (1 - (order.purchase_term.adv_less or 0.0) / 100.0)
					total_adv = payment_adv
				elif order.adv_term == 'split' and order.purchase_term.allow_split_adv:
					payment_adv = order.price_subtotal * _adv / order.purchase_term.split_adv
					total_adv = payment_adv * order.purchase_term.split_adv
				else:
					payment_adv = 0.00
					total_adv = 0.00
			else:
				_adv = term_line.adv_payment
				balance = order.price_subtotal - _adv
				if order.adv_term == 'orig':
					payment_adv = _adv
					total_adv = payment_adv
				elif order.adv_term == 'lessed' and order.purchase_term.allow_custom_adv:
					payment_adv = _adv * (1 - (order.purchase_term.adv_less or 0.0) / 100.0)
					total_adv = payment_adv
				elif order.adv_term == 'split' and order.purchase_term.allow_split_adv:
					payment_adv = _adv / order.purchase_term.split_adv
					total_adv = payment_adv * order.purchase_term.split_adv
				else:
					payment_adv = 0.00
					total_adv = 0.00
			
			balance_w_int = balance * (1 + (term_line.interest_rate or 0.0) / 100.0)
			amort = 0.00 if not order.purchase_term else (balance_w_int / order.purchase_term.months)
			total = total_adv + balance_w_int
			has_pcf = False
			if order.product_id.categ_id.has_pcf:
				has_pcf = True
				pcf = total * ((order.product_id.categ_id.pcf_perc or 0.0) / 100.0)
			else:
				has_pcf = False
				pcf = 0.0
			
			for taxes in order.tax_id:
				if taxes.amount_type != 'vat':
					continue
				else:
					print taxes.name
					self.ensure_one()
					tax = taxes.amount
			
			untaxed = (total - total_adv - pcf) / (1 + (tax or 0.0) / 100.0)
		
			# order.adv_payment = payment_adv
		
			order.update({
				'adv_payment': payment_adv,
				'for_amort_balance': balance_w_int,
				'monthly_amort': amort,
				'pcf': pcf,
				'total_adv': total_adv,
				'amount_untaxed': untaxed,
				'amount_tax': untaxed * ((tax or 0.0) / 100.0),
				'amount_total': total,
			})
		
	@api.onchange('partner_id')
	def _get_default_pricelist(self):
		for order in self:
			order.pricelist_id = order.partner_id.property_product_pricelist.id
			
	#get price from pricelist
	@api.onchange('pricelist_id','product_id')
	def _from_pricelist(self):
		unit_price = None
		for order in self:
			pricelist_item = self.env['product.pricelist.item']
			product_price = pricelist_item.search([('pricelist_id', '=', self.pricelist_id.id),('applied_on', '=', '0_product_variant'), ('product_id', '=', self.product_id.id)])
			if product_price:
				if product_price[-1].compute_price == 'fixed':
					unit_price = product_price[-1].fixed_price
				elif product_price[-1].compute_price == 'percentage':
					discount = order.product_id.lst_price * (product_price[-1].percent_price / 100)
					unit_price = order.product_id.lst_price - discount
				else:
					unit_price = 0.00
			else:
				unit_price = order.product_id.lst_price
			order.price_unit = unit_price
			
	@api.onchange('product_id')
	def _get_taxes(self):
		for order in self:
			order.tax_id = [(6, 0, order.product_id.taxes_id.ids)]
			
	@api.onchange('price_unit','discount')
	def _price_discount(self):
		for order in self:
			subtotal = None
			if order.price_unit == 0:
				subtotal = 0.00
			else:
				discount = order.price_unit * (order.discount / 100)
				subtotal = order.price_unit - discount
				
			order.price_subtotal = subtotal
			
	@api.onchange('product_category_id')
	def _product_category(self):
		for order in self:
			order.product_id = False
			order.purchase_term = False
	
	# @api.multi
	# @api.onchange('product_type','product_category_id')
	# def product_type_change(self):
	# 	for order in self:
	# 		if not order.product_type or order.product_category_id:
	# 			return {'domain': {'product_id': [('id', '=', False)]}}
	# 		else:
	# 			return {'domain': {'product_id': [('type', '=', order.product_type),('categ_id', '=', order.product_category_id.id)]}}

			
			
		
		
		
		
	