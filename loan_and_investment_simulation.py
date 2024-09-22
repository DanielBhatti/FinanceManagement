import numpy as np
import matplotlib.pyplot as plt

class Scenario:
    def __init__(self, invest_return_rate, starting_cash, salary_appreciation_rate):
        self.invest_return_rate = invest_return_rate  # Investment return rate
        self.starting_cash = starting_cash  # Starting cash (equal to downpayment amount)
        self.salary_appreciation_rate = salary_appreciation_rate  # Salary appreciation rate

    def __str__(self):
        raise NotImplementedError

    def simulate_net_worth(self, yearly_income, years):
        raise NotImplementedError

class LoanScenario(Scenario):
    def __init__(self, term, rate, invest_return_rate, downpayment_percentage, home_appreciation_rate, starting_cash, salary_appreciation_rate, property_tax_rate, monthly_maintenance_fees):
        super().__init__(invest_return_rate, starting_cash, salary_appreciation_rate)
        self.term = term          # Loan term in months
        self.rate = rate          # Loan interest rate
        self.downpayment_percentage = downpayment_percentage  # Downpayment as a percentage of principal
        self.home_appreciation_rate = home_appreciation_rate  # Home appreciation rate
        self.property_tax_rate = property_tax_rate  # Annual property tax as a percentage of home value
        self.monthly_maintenance_fees = monthly_maintenance_fees  # Monthly maintenance fees

    def __str__(self):
        return f"Loan: {self.term} months @ {self.rate*100:.2f}% with {self.downpayment_percentage*100:.2f}% down payment\nHome appreciation: {self.home_appreciation_rate*100:.2f}%\nInvestment return: {self.invest_return_rate*100:.2f}%\nSalary appreciation: {self.salary_appreciation_rate*100:.2f}%\nProperty tax: {self.property_tax_rate*100:.2f}%\nMaintenance fees: ${self.monthly_maintenance_fees}"

    def monthly_payment(self, principal):
        """Calculate monthly loan payment using the loan amortization formula."""
        loan_amount = principal * (1 - self.downpayment_percentage)
        monthly_rate = self.rate / 12
        return (loan_amount * monthly_rate) / (1 - (1 + monthly_rate) ** -self.term)

    def simulate_net_worth(self, principal, yearly_income, years):
        """Simulate net worth over time for a loan scenario with monthly compounding, home appreciation, salary increase, property tax, and down payment."""
        monthly_income = yearly_income / 12
        home_value = principal  # Starting home value
        loan_amount = principal * (1 - self.downpayment_percentage)  # Initial loan amount
        monthly_return_rate = (1 + self.invest_return_rate) ** (1/12) - 1  # Monthly compounding rate
        monthly_payment_amount = self.monthly_payment(principal)
        property_tax = home_value * (self.property_tax_rate / 12)  # Monthly property tax
        
        print(f"Simulating {self}")
        print(f"Monthly Monthly Payment (starting): {monthly_payment_amount}")
        print(f"Monthly Property Tax (starting): {property_tax}")
        print(f"Monthly Maintenance Fee (starting): {self.monthly_maintenance_fees}")

        net_worth_over_time = []
        cash = self.starting_cash - self.downpayment_percentage * principal   # Initialize with starting cash (downpayment)
        investment_worth = 0  # Start with no investments

        for month in range(1, years * 12 + 1):
            # Annual increases in salary and home value
            if month % 12 == 1 and month > 1:
                monthly_income *= (1 + self.salary_appreciation_rate)  # Increase income
                home_value *= (1 + self.home_appreciation_rate)  # Increase home value

            # Loan repayment and loan balance reduction
            if month <= self.term:
                interest_payment = loan_amount * (self.rate / 12)
                principal_payment = monthly_payment_amount - interest_payment
                loan_amount -= principal_payment  # Reduce the remaining loan amount
                surplus = monthly_income - monthly_payment_amount  # Income minus mortgage payment
            else:
                surplus = monthly_income  # Full income is available after loan is paid off

            # Deduct property tax and maintenance fees
            property_tax = home_value * (self.property_tax_rate / 12)  # Monthly property tax
            surplus -= property_tax
            surplus -= self.monthly_maintenance_fees

            # Add surplus to cash or investments
            if cash < 0:
                cash += surplus
            if cash >= 0:
                surplus += cash
                cash = 0
            investment_worth = (investment_worth + surplus) * (1 + monthly_return_rate)

            # Net worth: home value - remaining loan + cash + investment
            net_worth = home_value - loan_amount + cash + investment_worth
            net_worth_over_time.append(net_worth)

        return net_worth_over_time

class RentalScenario(Scenario):
    def __init__(self, monthly_rent, invest_return_rate, rent_appreciation_rate, starting_cash, salary_appreciation_rate):
        super().__init__(invest_return_rate, starting_cash, salary_appreciation_rate)
        self.monthly_rent = monthly_rent  # Monthly rent payment
        self.rent_appreciation_rate = rent_appreciation_rate  # Rent appreciation rate

    def __str__(self):
        return f"Rent: ${self.monthly_rent} per month\nRent appreciation: {self.rent_appreciation_rate*100:.2f}%\nInvestment return: {self.invest_return_rate*100:.2f}%\nSalary appreciation: {self.salary_appreciation_rate*100:.2f}%"

    def simulate_net_worth(self, yearly_income, years):
        """Simulate net worth over time for a rental scenario with rent and salary appreciation and monthly compounding."""
        monthly_income = yearly_income / 12
        monthly_return_rate = (1 + self.invest_return_rate) ** (1/12) - 1  # Monthly compounding rate

        print(f"Simulating {self}")

        net_worth_over_time = []
        cash = self.starting_cash  # Initialize net worth with starting cash (equal to downpayment amount)
        investment_worth = 0  # Start with no investments

        for month in range(1, years * 12 + 1):
            # Annual increases in salary and rent
            if month % 12 == 1 and month > 1:
                monthly_income *= (1 + self.salary_appreciation_rate)  # Increase income
                self.monthly_rent *= (1 + self.rent_appreciation_rate)  # Increase rent

            surplus = monthly_income - self.monthly_rent  # Income minus rent
            if cash < 0:
                cash += surplus
            if cash >= 0:
                surplus += cash
                cash = 0
            investment_worth = (investment_worth + surplus) * (1 + monthly_return_rate)

            # Net worth: cash + investment worth
            net_worth = cash + investment_worth
            net_worth_over_time.append(net_worth)

        return net_worth_over_time

# Parameters for the simulation
loan_principal = 450000  # Example loan amount in dollars
years_to_simulate = 30   # Simulate over 30 years
yearly_income = 80000    # Fixed yearly income
monthly_rent = 2000      # Example rent
downpayment_percentage = 0.20  # Example downpayment percentage (20%)
starting_cash = loan_principal * downpayment_percentage  # Set starting cash equal to the downpayment amount

# Appreciation rates
home_appreciation_rate = 0.03  # Example home appreciation rate (3% annually)
rent_appreciation_rate = 0.03  # Example rent appreciation rate (2% annually)
salary_appreciation_rate = 0.03  # Example salary appreciation rate (3% annually)
property_tax_rate = 0.0135  # Property tax rate (1% annually)
monthly_maintenance_fees = 200  # Monthly maintenance fees in dollars
invest_return_rate = 0.1

# Organizing scenarios into instances of Scenario class
scenarios = [
    LoanScenario(term=360, rate=0.065, invest_return_rate=invest_return_rate, downpayment_percentage=downpayment_percentage, home_appreciation_rate=home_appreciation_rate, starting_cash=starting_cash, salary_appreciation_rate=salary_appreciation_rate, property_tax_rate=property_tax_rate, monthly_maintenance_fees=monthly_maintenance_fees),  # Long-term loan with 20% down payment
    LoanScenario(term=180, rate=0.06, invest_return_rate=invest_return_rate, downpayment_percentage=downpayment_percentage, home_appreciation_rate=home_appreciation_rate, starting_cash=starting_cash, salary_appreciation_rate=salary_appreciation_rate, property_tax_rate=property_tax_rate, monthly_maintenance_fees=monthly_maintenance_fees),   # Short-term loan with 20% down payment
    RentalScenario(monthly_rent=monthly_rent, invest_return_rate=invest_return_rate, rent_appreciation_rate=rent_appreciation_rate, starting_cash=starting_cash, salary_appreciation_rate=salary_appreciation_rate),  # Rent scenario with same starting cash
]

# Run simulations for each scenario
net_worth_results = []
for scenario in scenarios:
    if isinstance(scenario, LoanScenario):
        net_worth = scenario.simulate_net_worth(loan_principal, yearly_income, years_to_simulate)
    elif isinstance(scenario, RentalScenario):
        net_worth = scenario.simulate_net_worth(yearly_income, years_to_simulate)  # Rental scenarios don't need 'loan_principal'
    net_worth_results.append(net_worth)

# Plot net worth over time
plt.figure(figsize=(10, 6))

for i, scenario in enumerate(scenarios):
    months = np.arange(1, years_to_simulate * 12 + 1)
    plt.plot(months / 12, net_worth_results[i], label=f"Scenario {i + 1}: {scenario}")
    
plt.xlabel("Years")
plt.ylabel("Net Worth")
plt.title("Net Worth Growth Over Time with Loan and Rental Scenarios")
plt.legend()
plt.tight_layout()
plt.grid(True, axis='y', linestyle='--', alpha=0.7)
plt.show()
