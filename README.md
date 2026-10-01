# Polish VAT White List (Biała Lista MF)

Verifies vendor bank accounts against the Polish Ministry of Finance VAT
taxpayer register ("Biała Lista"), straight from the vendor bill.

## How it works

- A **Verify on White List** button on vendor bills and vendor refunds
  (`in_invoice`, `in_refund`) calls the public MF API
  (`GET https://wl-api.mf.gov.pl/api/check/nip/{nip}/bank-account/{account}?date={bill date}`).
- The vendor's NIP comes from the commercial partner's tax ID (any `PL`
  prefix, spaces and dashes are stripped; must be 10 digits). The account
  comes from the bill's Recipient Bank (must be a 26-digit Polish account).
- Every answer is stored as an `hfb.mf.white.list.check` record on the bill
  (result, MF request ID, raw response, who checked and when) - the MF
  request ID is the official proof the check was done.
- The latest result for the account currently on the bill is shown as a
  badge next to Recipient Bank. Changing the account clears the badge until
  the new account is checked.
- A negative or failed check never blocks anything - it is logged and shown
  as a sticky notification.

## Configuration

None required. To point at the MF test environment, set the system
parameter `hfb_app_mf_white_list.api_url` (e.g. `https://wl-test.mf.gov.pl`).

## Technical

- `models/mf_white_list_check.py` - the check log model.
- `models/account_move.py` - button, API call, status badge compute.
- Access: readonly auditors can read, invoicing users can read and create
  checks (via the button), only accounting managers can edit/delete.
  Multi-company record rule on `company_id`.
- Depends on: `account`.

## Status

Rewritten from the client module `hfb_mf_white_list` (bannerstop-dev).
Missing `static/description/icon.png` and a `*_screenshot.png` banner before
it can be submitted to Odoo Apps.
