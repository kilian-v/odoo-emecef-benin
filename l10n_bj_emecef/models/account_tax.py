from odoo import models, fields

class AccountTax(models.Model):
    _inherit = 'account.tax'

    # Mapping pour les groupes de taxation standards
    emecef_tax_group = fields.Selection([
        ('A', 'Groupe A (0%)'),
        ('B', 'Groupe B (18%)'),
        ('C', 'Groupe C (Exonéré)'),
        ('D', 'Groupe D (18% TVA)'),
        ('E', 'Groupe E (Régime TPS)'),
        ('F', 'Groupe F (Exportation)')
    ], string="Groupe de taxation e-MECeF", help="Lettre correspondante selon l'API de la DGI Bénin")

    # Mapping pour l'AIB (Acompte sur Impôt sur les Bénéfices)
    emecef_aib_group = fields.Selection([
        ('A', 'AIB 1% (Groupe A)'),
        ('B', 'AIB 5% (Groupe B)')
    ], string="Groupe AIB e-MECeF", help="Utilisé uniquement si cette taxe est une retenue AIB")