# -*- coding: utf-8 -*-
{
    'name': "mgc_loan_management",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'product', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/loan_sale.xml',
        'views/product_category.xml',
        'views/loan_deferred_term.xml',
        'views/account_tax.xml',
        # 'static/resources.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}