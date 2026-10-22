# Student Finance Manager

A beginner portfolio project built with Python and Flet to help students record income and expenses, track category budgets, and monitor savings goals.

## Implemented features

- Dashboard with income, expenses, balance, savings-goal count and recent transactions.
- Separate Dashboard, Transactions, Budgets, Savings goals and About sections.
- Object-oriented data models (`Transaction`, `Budget`, `SavingsGoal`) and a `FinanceStore` class.
- Local JSON persistence using `finance_data.json`.
- Input validation, transaction deletion, budget tracking and savings progress updates.

## Requirements

- Python 3.10 or newer
- Flet (listed in `requirements.txt`)

## Run in VS Code on Windows

1. Open this folder in VS Code.
2. Choose **Terminal → New Terminal**.
3. Install dependencies:

   ```powershell
   py -m pip install -r requirements.txt
   ```

4. Start the app using the installed Flet command:

   ```powershell
   flet run main.py
   ```

   If Windows reports that `flet` is not recognized, run the file directly:

   ```powershell
   py main.py
   ```

## Data and privacy

The app stores its records in `finance_data.json` beside `main.py`. The file is created when the app saves data. For submission, use only fictional test data and do not include private financial records.

## Testing

See `TESTING.md`. Run each test and fill in the actual result and status based on what you observe. Do not claim that tests or peer review were completed before doing them.

## Current limitations / planned improvements

- The application stores data locally and does not sync between users or devices.
- It does not connect to bank accounts or process payments.
- Potential future work: export reports, add automated tests, and collect structured peer feedback.
