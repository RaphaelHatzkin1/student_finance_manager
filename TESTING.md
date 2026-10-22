# Testing and Refinement Record

Complete the **Actual result** and **Pass/Needs fixing** columns only after you run each test. Do not report a test as passed unless you observed the result.

| Test | Steps | Expected result | Actual result | Status |
|---|---|---|---|---|
| Launch app | Run `flet run main.py` or `py main.py` | App opens without a traceback | To be completed | Not tested here |
| Add income | Open Transactions; add an Income transaction with a valid description, category, amount and date | Transaction appears and income/balance totals update | To be completed | Not tested here |
| Add expense | Add an Expense transaction with a valid amount | Transaction appears and expense/balance totals update | To be completed | Not tested here |
| Reject invalid amount | Try a blank, non-numeric or zero amount | Helpful validation message appears; invalid transaction is not saved | To be completed | Not tested here |
| Delete transaction | Delete a test transaction | Transaction disappears and totals recalculate | To be completed | Not tested here |
| Save budget | Open Budgets and create a category budget | Budget appears with spent/remaining amount | To be completed | Not tested here |
| Savings goal | Create a goal, then update its saved amount | Progress and remaining amount update | To be completed | Not tested here |
| Persistence | Add test data, close app, reopen app | Records remain available | To be completed | Not tested here |
| Navigation | Open Dashboard, Transactions, Budgets, Savings goals and About | Each section opens correctly | To be completed | Not tested here |

## Refinement / peer feedback

- Reviewer and date: To be completed
- Feedback received: To be completed
- Change made in response: To be completed

## Known limitations

- Data is saved to a local JSON file; it is not synchronized across devices.
- This app does not connect to a bank or process real payments.
- Do not store banking passwords or sensitive credentials in this app.
