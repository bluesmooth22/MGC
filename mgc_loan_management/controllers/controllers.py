# -*- coding: utf-8 -*-
from odoo import http

# class MgcLoanManagement(http.Controller):
#     @http.route('/mgc_loan_management/mgc_loan_management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mgc_loan_management/mgc_loan_management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mgc_loan_management.listing', {
#             'root': '/mgc_loan_management/mgc_loan_management',
#             'objects': http.request.env['mgc_loan_management.mgc_loan_management'].search([]),
#         })

#     @http.route('/mgc_loan_management/mgc_loan_management/objects/<model("mgc_loan_management.mgc_loan_management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mgc_loan_management.object', {
#             'object': obj
#         })