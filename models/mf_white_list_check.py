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
	One record per verification of a vendor's bank account against the
	Polish Ministry of Finance VAT taxpayer register ("Biala Lista"). Kept
	as an audit trail: the MF request ID is the official proof that the
	check was performed.
"""
from odoo import fields, models

CHECK_RESULTS = [
    ('assigned', 'On the White List'),
    ('not_assigned', 'Not on the White List'),
    ('error', 'Verification Error'),
]


class MfWhiteListCheck(models.Model):
    _name = 'hfb.mf.white.list.check'
    _description = 'MF White List Verification'
    _order = 'id desc'
    _rec_name = 'request_id'

    move_id = fields.Many2one(
        'account.move', string='Bill', required=True, index=True,
        ondelete='cascade', readonly=True)
    company_id = fields.Many2one(
        related='move_id.company_id', store=True, index=True)
    check_date = fields.Date(
        string='Checked For Date', readonly=True,
        help="The date the MF register was queried for (the bill date).")
    vat = fields.Char(string='Tax ID (NIP)', readonly=True)
    account_number = fields.Char(string='Bank Account', readonly=True)
    result = fields.Selection(
        CHECK_RESULTS, string='Result', required=True, readonly=True)
    request_id = fields.Char(
        string='MF Request ID', readonly=True,
        help="Identifier returned by the MF API. It confirms which tax ID "
             "and account were checked, for which date and when the query "
             "was made - keep it as proof of verification.")
    message = fields.Char(string='Message', readonly=True)
    response = fields.Text(string='API Response', readonly=True)

#EoF
