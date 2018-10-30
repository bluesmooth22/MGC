from odoo import models, fields, api, _

class InstallmentSale(models.Model):
	_name = 'installment.sale'
 
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
	product_category_id = fields.Many2one('product.category', 'Product Category', domain=[('parent_category', '=', True)])
	pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', required=True, readonly=True, states={'draft': [('readonly', False)]})
	currency_id = fields.Many2one("res.currency", related='pricelist_id.currency_id', string="Currency", readonly=True, required=True)

	purchase_term = fields.Many2one('loan.deferred.term')

	product_id = fields.Many2one('product.product', required=True, domain="[('type', '=', product_type),('categ_id', '=', product_category_id)]")
	lot_id = fields.Many2one('stock.production.lot')
	price_unit = fields.Float(string='Unit Price', track_visibility='always')
	discount = fields.Float()
	price_subtotal = fields.Float(string='Subtotal', track_visibility='always', compute="_price_discount")
	user_id = fields.Many2one('res.users', 'Salesperson', default=lambda self: self.env.user)
	
	amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, track_visibility='always')
	amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, track_visibility='always')
	amount_total = fields.Monetary(string='Total', store=True, readonly=True, track_visibility='always')
	
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
	
	# @api.multi
	# @api.onchange('product_type','product_category_id')
	# def product_type_change(self):
	# 	for order in self:
	# 		if not order.product_type or order.product_category_id:
	# 			return {'domain': {'product_id': [('id', '=', False)]}}
	# 		else:
	# 			return {'domain': {'product_id': [('type', '=', order.product_type),('categ_id', '=', order.product_category_id.id)]}}

			
			
		
		
		
		
	