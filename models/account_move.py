# -*- coding: utf-8 -*-
#################################################################################
#
# Odoo, Open Source Management Solution
# Copyright (C) 2017-2026 Hadron for Business sp. z o.o. (http://hadronforbusiness.com)
#
# This program is proprietary software, licensed under the Odoo Proprietary
# License v1.0 (OPL-1). Its use is governed by the Odoo Apps terms available
# at https://www.odoo.com/documentation/user/legal/licenses.html and the
# license agreement accepted at purchase / installation.
#
# It is forbidden to publish, distribute, sublicense, or sell copies of the
# Software or modified copies of the Software.
#
# The above copyright notice and this permission notice must be included in
# all copies or substantial portions of the Software.
#
#################################################################################
""" @version	20.0.1.0.0
	@owner  Hadron for Business
	@author Hadron for Business sp. z o.o.
	@date   2026.10.01

	MF White List Verification
	Adds a "Verify on White List" button to vendor bills and refunds. It
	asks the Polish Ministry of Finance API whether the vendor's bank
	account is registered for the vendor's tax ID (NIP) on the bill date,
	logs every answer on the bill and shows the latest result next to the
	recipient bank account.
"""
import re

import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from .mf_white_list_check import CHECK_RESULTS

DEFAULT_API_URL = 'https://wl-api.mf.gov.pl'
API_URL_PARAM = 'hfb_app_mf_white_list.api_url'
API_TIMEOUT = 15
PURCHASE_TYPES = ('in_invoice', 'in_refund')


def _normalize_vat(vat):
    return re.sub(r'\D', '', vat or '')


def _normalize_account(acc_number):
    account = re.sub(r'[\s-]', '', acc_number or '').upper()
    if account.startswith('PL'):
        account = account[2:]
    return account


class AccountMove(models.Model):
    _inherit = 'account.move'

    mf_white_list_check_ids = fields.One2many(
        'hfb.mf.white.list.check', 'move_id', string='White List Checks')
    mf_white_list_result = fields.Selection(
        CHECK_RESULTS, string='White List Status',
        compute='_compute_mf_white_list_result', store=True,
        help="Result of the latest White List check of the bank account "
             "currently set on the bill. Empty if this account has not "
             "been checked yet.")

    @api.depends('partner_bank_id.acc_number', 'mf_white_list_check_ids.result')
    def _compute_mf_white_list_result(self):
        for move in self:
            account = _normalize_account(move.partner_bank_id.acc_number)
            checks = move.mf_white_list_check_ids.filtered(
                lambda c: account and c.account_number == account)
            move.mf_white_list_result = checks.sorted('id', reverse=True)[:1].result

    def _mf_white_list_prepare_query(self):
        self.ensure_one()
        if self.move_type not in PURCHASE_TYPES:
            raise UserError(_("The White List check is only available on vendor bills and refunds."))
        if not self.invoice_date:
            raise UserError(_("Set the bill date first - the White List is checked for that date."))
        vat = _normalize_vat(self.commercial_partner_id.vat)
        if len(vat) != 10:
            raise UserError(_("The vendor has no valid Polish tax ID (NIP, 10 digits)."))
        if not self.partner_bank_id:
            raise UserError(_("Set the vendor's bank account (Recipient Bank) first."))
        account = _normalize_account(self.partner_bank_id.acc_number)
        if not re.fullmatch(r'\d{26}', account):
            raise UserError(_(
                "The bank account %s is not a Polish account number (26 digits).",
                self.partner_bank_id.acc_number))
        return vat, account

    def _mf_white_list_call_api(self, vat, account):
        base_url = self.env['ir.config_parameter'].sudo().get_param(API_URL_PARAM) or DEFAULT_API_URL
        url = '%s/api/check/nip/%s/bank-account/%s' % (base_url.rstrip('/'), vat, account)
        vals = {'result': 'error'}
        try:
            response = requests.get(
                url, params={'date': fields.Date.to_string(self.invoice_date)},
                headers={'Accept': 'application/json'}, timeout=API_TIMEOUT)
        except requests.RequestException as error:
            vals['message'] = _("The MF API could not be reached: %s", error)
            return vals
        vals['response'] = response.text
        try:
            payload = response.json()
        except ValueError:
            vals['message'] = _("The MF API returned an unexpected response (HTTP %s).", response.status_code)
            return vals
        if not isinstance(payload, dict):
            payload = {}
        result = payload.get('result') or {}
        if result.get('accountAssigned') in ('TAK', 'NIE'):
            vals['result'] = 'assigned' if result['accountAssigned'] == 'TAK' else 'not_assigned'
            vals['request_id'] = result.get('requestId')
        else:
            error = ' '.join(filter(None, [payload.get('code'), payload.get('message')]))
            vals['message'] = error or _("Unknown MF API error (HTTP %s).", response.status_code)
        return vals

    def action_mf_white_list_check(self):
        self.ensure_one()
        vat, account = self._mf_white_list_prepare_query()
        vals = self._mf_white_list_call_api(vat, account)
        check = self.env['hfb.mf.white.list.check'].create(dict(
            vals, move_id=self.id, check_date=self.invoice_date,
            vat=vat, account_number=account))

        if check.result == 'assigned':
            notif_type, sticky = 'success', False
            title = _("Account is on the White List")
            message = _("Request ID: %s", check.request_id)
        elif check.result == 'not_assigned':
            notif_type, sticky = 'danger', True
            title = _("Account is NOT on the White List")
            message = _(
                "Account %(account)s is not registered for NIP %(vat)s on %(date)s (request ID: %(request)s).",
                account=account, vat=vat, date=check.check_date, request=check.request_id)
        else:
            notif_type, sticky = 'warning', True
            title = _("White List check failed")
            message = check.message
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': message,
                'type': notif_type,
                'sticky': sticky,
                'next': {'type': 'ir.actions.client', 'tag': 'soft_reload'},
            },
        }

#EoF
