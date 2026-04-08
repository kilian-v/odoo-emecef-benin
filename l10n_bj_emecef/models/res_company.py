import requests
from odoo import models, fields, _
from odoo.exceptions import UserError

class ResCompany(models.Model):
    _inherit = 'res.company'

    emecef_ifu = fields.Char(string="IFU e-MECeF")
    emecef_nim = fields.Char(string="NIM e-MECeF")
    emecef_token = fields.Char(string="Jeton de sécurité")
    emecef_env = fields.Selection([
        ('test', 'Test'),
        ('prod', 'Production')
    ], string="Environnement", default='test')

    def action_check_emecef_connection(self):
        # ensure_one() s'assure qu'on agit sur une seule société à la fois
        self.ensure_one()

        if not self.emecef_token:
            raise UserError(_("Veuillez d'abord renseigner votre jeton de sécurité."))

        # Choix de l'URL selon l'environnement (Test ou Prod)
        if self.emecef_env == 'prod':
            url = "https://sygmef.impots.bj/emcf/api/info/status"
        else:
            url = "https://developper.impots.bj/sygmef-emcf/api/info/status"

        # Préparation des en-têtes avec le jeton (Bearer token)
        headers = {
            'Authorization': f'Bearer {self.emecef_token}',
            'accept': 'application/json'
        }

        try:
            # Appel à l'API de la DGI
            response = requests.get(url, headers=headers, timeout=10)

            # Si le jeton est invalide, l'API renvoie 401 Unauthorized
            if response.status_code == 401:
                raise UserError(_("Erreur 401 : Non autorisé. Votre jeton est invalide ou expiré."))

            # Si la requête a échoué pour une autre raison (ex: 500)
            response.raise_for_status()

            # On extrait les données JSON de la réponse
            data = response.json()

            # --- NOUVEAUTÉ : AUTO-REMPLISSAGE ---
            # On met à jour les champs de la société avec les infos de la DGI
            self.emecef_ifu = data.get('ifu')
            self.emecef_nim = data.get('nim')

            # On formate le message de succès
            message = (
                f"Version API : {data.get('version')}\n"
                f"IFU DGI : {data.get('ifu')}\n"
                f"NIM DGI : {data.get('nim')}\n"
                f"Validité du jeton : {data.get('tokenValid')}"
            )

            # On renvoie une action client Odoo pour afficher une notification ET recharger la page
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '✅ Connexion e-MECeF Réussie',
                    'message': message,
                    'type': 'success',
                    'sticky': False,
                    # NOUVEAUTÉ : On demande à Odoo de recharger la vue actuelle
                    'next': {'type': 'ir.actions.client', 'tag': 'reload'},
                }
            }

        except requests.exceptions.RequestException as e:
            raise UserError(_("Erreur de connexion au serveur de la DGI :\n%s") % str(e))