import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def action_fetch_ifu_data(self):
        # On boucle au cas où (sécurité standard Odoo), mais il n'y aura qu'un seul contact
        for partner in self:
            if not partner.vat:
                raise UserError(_("Veuillez d'abord saisir un numéro IFU pour lancer la recherche."))

            # On nettoie les espaces éventuels
            ifu = partner.vat.strip()

            # L'URL de l'API publique
            url = f"https://ifubackend.impots.bj/api/default/searchByIFU/{ifu}"

            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status() # Gère les erreurs 404, 500, etc.
                data = response.json()

                # Vérification du statut retourné par l'API (success: true/false)
                if data.get('success'):
                    obj = data.get('object', {})
                    update_vals = {}

                    # --- NOUVEAUTÉ : GESTION DU PRÉNOM ET NOM ---
                    nom = obj.get('nom')
                    prenom = obj.get('prenom')

                    # On combine les deux s'ils existent, sinon on prend ce qui est disponible
                    if prenom and nom:
                        update_vals['name'] = f"{prenom} {nom}"
                    elif nom:
                        update_vals['name'] = nom
                    elif prenom:
                        update_vals['name'] = prenom
                    # --------------------------------------------

                    if obj.get('email'):
                        update_vals['email'] = obj.get('email')
                    if obj.get('telephone'):
                        update_vals['phone'] = obj.get('telephone')

                    # On met à jour la fiche client
                    if update_vals:
                        partner.write(update_vals)

                    # On affiche une jolie notification pour dire que c'est bon !
                    nom_affiche = update_vals.get('name', 'le client')
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': '✅ Client Trouvé',
                            'message': f"Les informations de {nom_affiche} ont été mises à jour.",
                            'type': 'success',
                            'sticky': False,
                            'next': {'type': 'ir.actions.client', 'tag': 'reload'},
                        }
                    }

            except requests.exceptions.RequestException as e:
                raise UserError(_("Erreur de communication avec l'API IFU publique :\n%s") % str(e))