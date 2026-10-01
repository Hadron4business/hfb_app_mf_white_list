# -*- coding: utf-8 -*-
# vim: tabstop=4 softtabstop=0 shiftwidth=4 smarttab expandtab fileformat=unix
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
{
    'name': "Polish VAT White List (Biała Lista MF)",
    'summary': "Verify vendor bank accounts against the Polish Ministry of Finance White List",
    'description': """
Polish VAT White List (Biała Lista MF)
=======================================

Adds a "Verify on White List" button to vendor bills and vendor refunds. One
click asks the Polish Ministry of Finance API whether the vendor's bank
account is registered for the vendor's tax ID (NIP) on the bill date.

Every check is logged on the bill together with the MF request ID - the
official proof that the verification was performed - and the latest result
is shown as a badge right next to the recipient bank account.
""",
    'version': "20.0.1.0.0",
    'author': "Hadron for Business sp. z o.o.",
    'website': "http://hadronforbusiness.com",
    'license': "OPL-1",
    'category': "Accounting/Accounting",
    'depends': [
        'account',
    ],
    'data': [
        'security/ir.access.csv',
        'views/mf_white_list_check_views.xml',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
}
