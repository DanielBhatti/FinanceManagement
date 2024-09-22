import matplotlib.pyplot as plt
import numpy as np

def calc_minimum_payment(loan_amount: float, monthly_loan_rate: float, loan_term_months: float):
    return (loan_amount * monthly_loan_rate) / (1 - (1 + monthly_loan_rate) ** (-loan_term_months))

class LoanInvestmentSimulator:
    def __init__(self, loan_amount: float, loan_rate: float, loan_term_years: float, monthly_payment: float, starting_cash: float, investment_rate: float):
        self.loan_amount = loan_amount
        self.loan_rate = loan_rate
        self.loan_term_years = loan_term_years
        self.monthly_income = monthly_payment
        self.starting_cash = starting_cash
        self.investment_rate = investment_rate
        self.loan_term_months = loan_term_years * 12
        self.monthly_loan_rate = loan_rate / 12
        self.monthly_investment_rate = (1 + investment_rate) ** (1/12) - 1
        self.minimum_payment = calc_minimum_payment(self.loan_amount, self.loan_rate / 12, self.loan_term_months)

    def simulate(self):
        return self.simulate_scenario_invest(), self.simulate_scenario_payoff()

    def simulate_scenario_invest(self):
        loan_balance = self.loan_amount
        investment_value = self.starting_cash
        net_worth = []
        loan_balances = []
        investment_values = []

        for month in range(self.loan_term_months):
            interest_payment = loan_balance * self.monthly_loan_rate
            principal_payment = min(self.minimum_payment, self.monthly_income) - interest_payment
            loan_balance -= principal_payment

            remaining_cash = self.monthly_income - self.minimum_payment
            if remaining_cash > 0:
                investment_value += investment_value * self.monthly_investment_rate + remaining_cash

            loan_balances.append(loan_balance)
            investment_values.append(investment_value)
            net_worth.append(investment_value - loan_balance)

        return loan_balances, investment_values, net_worth

    def simulate_scenario_payoff(self):
        loan_balance = self.loan_amount
        investment_value = 0
        net_worth = []
        loan_balances = []
        investment_values = []

        # Pay off the loan as soon as possible
        for month in range(self.loan_term_months):
            if loan_balance > 0:
                # Apply monthly income + starting cash if it's the first month
                payment = self.monthly_income + (self.starting_cash if month == 0 else 0)
                interest_payment = loan_balance * self.monthly_loan_rate
                loan_balance -= max(0, payment - interest_payment)
            else:
                # Invest after loan is paid off
                investment_value += investment_value * self.monthly_investment_rate + self.monthly_income

            # Record values
            loan_balances.append(loan_balance)
            investment_values.append(investment_value)
            net_worth.append(investment_value - loan_balance)

        return loan_balances, investment_values, net_worth

    def plot(self, loan_balances_1, investment_values_1, net_worth_1, loan_balances_2, investment_values_2, net_worth_2):
        months = np.arange(1, len(loan_balances_1) + 1)
        
        plt.figure(figsize=(10, 6))
        # Plot Invest
        plt.plot(months, loan_balances_1, label='Loan Balance (Invest)', linestyle='--')
        plt.plot(months, net_worth_1, label='Net Worth (Invest)')
        
        # Plot Payoff Loan
        plt.plot(months, loan_balances_2, label='Loan Balance (Payoff Loan)', linestyle='--')
        plt.plot(months, net_worth_2, label='Net Worth (Payoff Loan)')
        
        plt.xlabel('Months')
        plt.ylabel('Amount ($)')
        plt.title('Loan Balance and Net Worth Over Time')
        plt.legend()
        plt.grid(True)
        plt.show()

    def summary_statistics(self, loan_balances_1, investment_values_1, net_worth_1, loan_balances_2, investment_values_2, net_worth_2):
        print("Invest Scenario:")
        print(f"Final Loan Balance: ${loan_balances_1[-1]:.2f}")
        print(f"Final Investment Value: ${investment_values_1[-1]:.2f}")
        print(f"Final Net Worth: ${net_worth_1[-1]:.2f}\n")

        print("Payoff Loan Scenario:")
        print(f"Final Loan Balance: ${loan_balances_2[-1]:.2f}")
        print(f"Final Investment Value: ${investment_values_2[-1]:.2f}")
        print(f"Final Net Worth: ${net_worth_2[-1]:.2f}\n")


# Parameters for the simulation
loan_amount = 20_338.37  # Loan amount
loan_rate = 0.085  # Annual loan interest rate (8.5%)
loan_term_years = 22  # Loan term in years
monthly_income = 171  # Monthly income
starting_cash = 8000  # Starting cash
investment_rate = 0.10  # Annual investment return (10%)

# Initialize simulator
simulator = LoanInvestmentSimulator(loan_amount, loan_rate, loan_term_years, monthly_income, starting_cash, investment_rate)

# Simulate both scenarios
loan_balances_1, investment_values_1, net_worth_1 = simulator.simulate_scenario_invest()
loan_balances_2, investment_values_2, net_worth_2 = simulator.simulate_scenario_payoff()

print(f"Loan Amount: ${loan_amount}")
print(f"Loan Interest Rate: {loan_rate * 100}% annually")
print(f"Loan Term: {loan_term_years} years")
print(f"Monthly Income: ${monthly_income}")
print(f"Starting Cash: ${starting_cash}")
print(f"Investment Rate: {investment_rate * 100}% annually")

# Plot results
simulator.plot(loan_balances_1, investment_values_1, net_worth_1, loan_balances_2, investment_values_2, net_worth_2)

# Print summary statistics
simulator.summary_statistics(loan_balances_1, investment_values_1, net_worth_1, loan_balances_2, investment_values_2, net_worth_2)
