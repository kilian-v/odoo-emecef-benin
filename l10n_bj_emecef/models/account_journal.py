from odoo import models, fields

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    emecef_payment_type = fields.Selection([
        ('ESPECES', 'Espèces'),
        ('VIREMENT', 'Virement'),
        ('CARTEBANCAIRE', 'Carte Bancaire'),
        ('MOBILEMONEY', 'Mobile Money'),
        ('CHEQUES', 'Chèques'),
        ('CREDIT', 'Crédit'),
        ('AUTRE', 'Autre')
    ], string="Type de paiement e-MECeF", help="Sera envoyé à la DGI lors de la normalisation de la facture.")