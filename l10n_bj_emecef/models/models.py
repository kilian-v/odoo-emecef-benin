import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    emecef_uid = fields.Char(string="UID e-MECeF", readonly=True, copy=False)
    emecef_code = fields.Char(string="Code MECeF/DGI", readonly=True, copy=False)
    emecef_qr_code = fields.Char(string="QR Code e-MECeF", readonly=True, copy=False)
    emecef_counters = fields.Char(string="Compteurs MECeF", readonly=True, copy=False)
    emecef_datetime = fields.Datetime(string="Date/Heure de Normalisation", readonly=True, copy=False)
    is_normalized = fields.Boolean(string="Est normalisée", default=False, copy=False)

    def action_send_emecef(self):
        self.ensure_one()
        company = self.company_id

        # 1. Vérifications de base
        if not company.emecef_token or not company.emecef_ifu:
            raise UserError(_("Veuillez configurer les identifiants e-MECeF de la société."))
        if self.state != 'posted':
            raise UserError(_("La facture doit être confirmée (Comptabilisée) avant d'être normalisée."))

        # 2. Déterminer le type de facture (FV pour Vente, FA pour Avoir)
        invoice_type = 'FV' if self.move_type == 'out_invoice' else 'FA'

        # 3. Préparer les articles (Lignes de facture)
        items = []
        for line in self.invoice_line_ids.filtered(lambda l: l.display_type not in ('line_section', 'line_note')):
            tax_group = 'A'
            if line.tax_ids and line.tax_ids[0].emecef_tax_group:
                tax_group = line.tax_ids[0].emecef_tax_group

            items.append({
                "name": line.name[:50] if line.name else 'Article',
                "price": int(round(line.price_unit)),
                "quantity": line.quantity,
                "taxGroup": tax_group
            })

        if not items:
            raise UserError(_("La facture doit contenir au moins un article."))

        # 4. Construire le payload JSON de base
        payload = {
            "ifu": company.emecef_ifu,
            "type": invoice_type,
            "items": items,
            "operator": {
                "name": self.env.user.name
            }
        }

        # --- NOUVEAUTÉ : GESTION DES AVOIRS (FA) ---
        if invoice_type == 'FA':
            # On vérifie qu'Odoo connaît bien la facture d'origine
            if not self.reversed_entry_id:
                raise UserError(_("Impossible de normaliser : Cet avoir n'est lié à aucune facture d'origine dans Odoo."))

            # On vérifie que la facture d'origine a bien été normalisée
            if not self.reversed_entry_id.emecef_code:
                raise UserError(_("La facture d'origine doit d'abord être normalisée pour pouvoir normaliser son avoir."))

            # L'API exige les 24 premiers caractères du code MECeF de la facture annulée
            original_code = self.reversed_entry_id.emecef_code.replace('-', '')
            payload["reference"] = original_code[:24]
        # -------------------------------------------

        # Ajouter les infos du client
        if self.partner_id:
            payload["client"] = {"name": self.partner_id.name}
            if self.partner_id.vat:
                payload["client"]["ifu"] = self.partner_id.vat

        # 5. Envoi à l'API
        url = "https://sygmef.impots.bj/emcf/api/invoice" if company.emecef_env == 'prod' else "https://developper.impots.bj/sygmef-emcf/api/invoice"
        headers = {
            'Authorization': f'Bearer {company.emecef_token}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            data = response.json()

            if data.get('errorCode'):
                raise UserError(f"Erreur DGI : {data.get('errorDesc')}")

            # 6. Succès : On sauvegarde l'UID retourné par la DGI
            self.emecef_uid = data.get('uid')

            # 7. On prépare les données pour le Pop-up (Wizard)
            wizard_vals = {
                'move_id': self.id,
                'tax_a': data.get('taa', 0),
                'tax_b': data.get('tab', 0),
                'tax_c': data.get('tac', 0),
                'tax_d': data.get('tad', 0),
                'tax_e': data.get('tae', 0),
                'tax_f': data.get('taf', 0),
                'aib': data.get('aib', 0),
                'total_general': data.get('total', 0),
            }
            wizard = self.env['emecef.confirm.wizard'].create(wizard_vals)

            return {
                'name': _("Confirmation des totaux e-MECeF"),
                'type': 'ir.actions.act_window',
                'res_model': 'emecef.confirm.wizard',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new',
            }

        except requests.exceptions.RequestException as e:
            raise UserError(f"Erreur de communication avec la DGI : {e}")