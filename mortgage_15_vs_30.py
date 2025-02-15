import numpy as np
import matplotlib.pyplot as plt

def mortgage_payment(principal, annual_rate, years):
    """Calculate fixed monthly mortgage payment."""
    monthly_rate = annual_rate / 12
    num_payments = years * 12
    return principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)

def simulate_stock_market(investment, years, monthly_return):
    """Simulate stock market growth assuming fixed monthly investment and return."""
    balance = 0
    balances = []
    for _ in range(years * 12):
        balance = (balance + investment) * (1 + monthly_return)
        balances.append(balance)
    return balances

# Inputs
home_price = 375000  # Home price
down_payment = home_price * 0.25  # Down payment
loan_amount = home_price - down_payment

# Interest rates (modify as needed)
rate_15_year = 0.06
rate_30_year = rate_15_year + 0.005

# Expected stock market return (same for both scenarios)
annual_stock_return = 0.07  # 7% expected annual return
monthly_stock_return = (1 + annual_stock_return) ** (1/12) - 1

# Mortgage calculations
payment_15 = mortgage_payment(loan_amount, rate_15_year, 15)
payment_30 = mortgage_payment(loan_amount, rate_30_year, 30)
extra_investment = payment_15 - payment_30  # Amount available to invest if taking 30-year mortgage

# Simulate investment growth (only for the 30-year mortgage scenario)
investment_growth = simulate_stock_market(extra_investment, 30, monthly_stock_return)

# Wealth calculations
home_equity_15 = home_price  # Home is fully owned after 15 years
home_equity_30 = home_price  # Home is fully owned after 30 years

# Scenario 1: 15-Year Mortgage (Home paid off at Year 15, investing after)
investment_after_15 = simulate_stock_market(payment_15, 15, monthly_stock_return)
total_wealth_15 = home_equity_15 + investment_after_15[-1]  # Home + investments after 30 years

# Scenario 2: 30-Year Mortgage (Investing from the start)
total_wealth_30 = home_equity_30 + investment_growth[-1]  # Home + investment balance

# Results
print(f"15-Year Mortgage Payment: ${payment_15:.2f}")
print(f"30-Year Mortgage Payment: ${payment_30:.2f}")
print(f"Extra invested per month (30-year scenario): ${extra_investment:.2f}")
print(f"Total Wealth with 15-Year Mortgage (after 30 years): ${total_wealth_15:,.2f}")
print(f"Total Wealth with 30-Year Mortgage + Investments (after 30 years): ${total_wealth_30:,.2f}")

# Plot investment growth
plt.figure(figsize=(10, 5))
plt.plot(range(15 * 12, 30 * 12), investment_after_15, label="15-Year Mortgage: Investments After Payoff", linestyle="--")
plt.plot(range(30 * 12), investment_growth, label="30-Year Mortgage: Investing Difference", linestyle="-")
plt.xlabel("Months")
plt.ylabel("Investment Value ($)")
plt.title("Investment Growth Over 30 Years")
plt.legend()
plt.grid()
plt.show()
