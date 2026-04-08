import requests
from odoo import models, fields, _
from odoo.exceptions import UserError

class EmecefConfirmWizard(models.TransientModel):
    _name = 'emecef.confirm.wizard'
    _description = "Confirmation des totaux e-MECeF"

    move_id = fields.Many2one('account.move', string="Facture", required=True)

    # Tous les groupes de taxation
    tax_a = fields.Integer(string="Montant total pour le groupe A", readonly=True)
    tax_b = fields.Integer(string="Montant total pour le groupe B", readonly=True)
    tax_c = fields.Integer(string="Montant total pour le groupe C", readonly=True)
    tax_d = fields.Integer(string="Montant total pour le groupe D", readonly=True)
    tax_e = fields.Integer(string="Montant total pour le groupe E", readonly=True)
    tax_f = fields.Integer(string="Montant total pour le groupe F", readonly=True)
    aib = fields.Integer(string="Montant de l'AIB", readonly=True)

    total_general = fields.Integer(string="Montant total sur la facture", readonly=True)

    def action_confirm_api(self):
        self.ensure_one()
        move = self.move_id
        company = move.company_id

        # URL pour la demande de finalisation (PUT)
        base_url = "https://sygmef.impots.bj/emcf/api/invoice" if company.emecef_env == 'prod' else "https://developper.impots.bj/sygmef-emcf/api/invoice"
        url = f"{base_url}/{move.emecef_uid}/confirm"

        headers = {
            'Authorization': f'Bearer {company.emecef_token}',
            'Content-Type': 'application/json',
            'accept': 'application/json'
        }

        try:
            response = requests.put(url, headers=headers, timeout=15)
            data = response.json()

            if data.get('errorCode'):
                raise UserError(f"Erreur DGI lors de la confirmation : {data.get('errorDesc')}")

            # Succès : On met à jour la facture avec les Éléments de Sécurité
            move.write({
                'emecef_code': data.get('codeMECeFDGI'),
                'emecef_qr_code': data.get('qrCode'),
                'emecef_counters': data.get('counters'),
                'emecef_datetime': fields.Datetime.now(),
                'is_normalized': True
            })

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '✅ Facture Normalisée !',
                    'message': f"Le code MECeF a été généré : {data.get('codeMECeFDGI')}",
                    'type': 'success',
                    'sticky': False,
                    'next': {'type': 'ir.actions.client', 'tag': 'reload'},
                }
            }

        except requests.exceptions.RequestException as e:
            raise UserError(f"Erreur de communication avec la DGI : {e}")