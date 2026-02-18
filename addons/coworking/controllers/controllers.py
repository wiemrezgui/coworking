# -*- coding: utf-8 -*-
# from odoo import http


# class Coworking(http.Controller):
#     @http.route('/coworking/coworking', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/coworking/coworking/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('coworking.listing', {
#             'root': '/coworking/coworking',
#             'objects': http.request.env['coworking.coworking'].search([]),
#         })

#     @http.route('/coworking/coworking/objects/<model("coworking.coworking"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('coworking.object', {
#             'object': obj
#         })

