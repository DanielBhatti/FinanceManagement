import matplotlib.pyplot as plt
from tabulate import tabulate

class MortgageOption:
    def __init__(self, loan_amount: float, rate: float, points_rate: float, closing_costs: float, loan_term_years: int, name: str):
        self.loan_amount = loan_amount
        self.rate = rate
        self.monthly_rate = self.rate / 12
        self.points_rate = points_rate
        self.points_cost = self.points_rate * self.loan_amount
        self.closing_costs = closing_costs
        self.loan_term_years = loan_term_years
        self.loan_term_months = self.loan_term_years * 12
        self.name = name
        self.upfront_costs = self.loan_amount * self.points_rate + self.closing_costs
        self.monthly_payment = self.loan_amount * self.monthly_rate / (1 - (1 + self.monthly_rate) ** -self.loan_term_months)

investment_return_rate = 0.07
loan_amount = 375_000 * 0.75

options = [
    MortgageOption(loan_amount, 0.065, 0.015, 1461 + 78 + 812 + 60, 30, "Wells Fargo"),
    MortgageOption(loan_amount, 0.06875, 0.00375, 1395 + 765 + 1195 + 15 + 83 + 12 + 81, 30, "Valley Bank"),
    MortgageOption(loan_amount, 0.06625 - 0.00125, 0.0025, 950 + 570 + 60 + 5, 30, "TD Bank"),
    MortgageOption(loan_amount, 0.065 - 0.00125, 0.01, 950 + 570 + 60 + 5, 30, "TD Bank 2"),
    #MortgageOption(loan_amount, 0.065 - 0.00125 * 2, 0.00125, 950 + 570 + 60 + 5, 30, "TD Bank Mod"),
    #MortgageOption(loan_amount, 0.065 - 0.00125 * 2, 0.01, 950 + 570 + 60 + 5, 30, "TD Bank 2 Mod"),
    #MortgageOption(loan_amount, 0.065 - 0.00125, 0.01, 950 + 570 + 60 + 5, 30, "TD Bank 2 Mod"),
    #MortgageOption(loan_amount, 0.06750 - 0.00125, 0.0025, 630 + 41.76 + 7 + 695 + 500, 30, "Citizens"),
    MortgageOption(loan_amount, 0.06750 - 0.00125, 0.0025, 630 + 41.76 + 7 + 695 + 500 - 500, 30, "Citizens Deal"),
    #MortgageOption(loan_amount, 0.06625, 0.0025, 630 + 41.76 + 7 + 695 + 500 - 500, 30, "Citizens Deal Mod"),
    MortgageOption(loan_amount, 0.06625, 0.00875, 175 + 915 + 644 + 79 + 6 + 1200, 30, "Citi"),
]
time_horizon_years = max([o.loan_term_years for o in options])
time_periods = time_horizon_years * 12
starting_cash = max([o.upfront_costs for o in options])
monthly_income = max([o.monthly_payment for o in options])
net_worth_data: dict[str, list[float]] = {}

table_data = []
for option in options:
    table_data.append([
        option.name,
        f"{option.rate:.3%}",
        f"${option.points_cost:,.2f}",
        f"${option.closing_costs:,.2f}",
        f"${option.upfront_costs:,.2f}",
        f"${option.monthly_payment:,.2f}"
    ])

print(tabulate(table_data, headers=["Name", "Rate", "Points Cost", "Closing Costs", "Upfront Costs", "Monthly Payment"], tablefmt="grid"))

for option in options:
    rate = option.rate
    invested_balance = starting_cash - option.upfront_costs
    if invested_balance < 0:
        raise Exception("Negative starting invested balance")
    net_worth: list[float] = []

    for month in range(1, time_periods + 1):
        excess_income = monthly_income - (option.monthly_payment if month <= option.loan_term_months else 0)
        if excess_income < 0:
            raise Exception("Negative excess income")
        invested_balance += excess_income
        invested_balance *= (1 + investment_return_rate / 12)
        net_worth.append(invested_balance)
    net_worth_data[option.name] = net_worth

plt.figure(figsize=(10, 6))
for key in net_worth_data:
    plt.plot(range(1, time_periods + 1), net_worth_data[key], label=key)

plt.title("Net Worth Over Time for Each Mortgage Option")
plt.xlabel("Months")
plt.ylabel("Net Worth ($)")
plt.legend()
plt.grid()
plt.show()
