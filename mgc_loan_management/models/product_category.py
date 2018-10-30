from odoo import api, fields, models, _

class ProductCategory(models.Model):
	_inherit = 'product.category'
	
	parent_category = fields.Boolean(default=False)
	product_type = fields.Selection([('product', 'Product'), ('service', 'Service'), ('plan', 'Plan')],
	                                default='product')
	
	@api.onchange('parent_category')
	def _parent_category(self):
		for s in self:
			s.parent_id = False
			