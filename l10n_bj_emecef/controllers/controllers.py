# -*- coding: utf-8 -*-
# from odoo import http


# class L10nBjEmecef(http.Controller):
#     @http.route('/l10n_bj_emecef/l10n_bj_emecef', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/l10n_bj_emecef/l10n_bj_emecef/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('l10n_bj_emecef.listing', {
#             'root': '/l10n_bj_emecef/l10n_bj_emecef',
#             'objects': http.request.env['l10n_bj_emecef.l10n_bj_emecef'].search([]),
#         })

#     @http.route('/l10n_bj_emecef/l10n_bj_emecef/objects/<model("l10n_bj_emecef.l10n_bj_emecef"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('l10n_bj_emecef.object', {
#             'object': obj
#         })

