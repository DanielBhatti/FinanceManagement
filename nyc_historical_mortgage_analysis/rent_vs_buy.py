import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def pmt(rate, loan_term, pv):
    """
    Calculate the fixed monthly payment needed to fully amortize a loan.
    
    Parameters:
    rate (float): The monthly interest rate (annual rate proportion / 12).
    loan_term (int): The total number of payments (loan term in months).
    pv (float): The loan principal (present value).
    
    Returns:
    float: The fixed monthly payment.
    """
    return (rate * pv) / (1 - (1 + rate) ** -loan_term)

def simulate_rent_vs_buy(
    monthly_rent,
    annual_rent_increase,
    annual_investment_return,
    downpayment,
    mortgage_length,
    mortgage_interest_rate,
    monthly_maintenance,
    house_appreciation_rate,
    monthly_paycheck,
    annual_raise,
    house_price,
    simulation_years
):
    months = simulation_years * 12
    rent = np.zeros(months)
    rent[0] = monthly_rent
    investment_value_rent = np.zeros(months)
    investment_value_rent[0] = downpayment
    investment_value_buy = np.zeros(months)
    home_value = np.zeros(months)
    home_value[0] = house_price
    mortgage_payment = pmt(mortgage_interest_rate / 12, mortgage_length * 12, house_price - downpayment)
    mortgage_balance = np.zeros(months)
    mortgage_balance[0] = house_price - downpayment
    equity = np.zeros(months)
    net_worth_rent = np.zeros(months)
    net_worth_buy = np.zeros(months)
    paycheck = np.zeros(months)
    paycheck[0] = monthly_paycheck
    extra_investment = np.zeros(months)

    for month in range(1, months):
        rent[month] = rent[month - 1] * (1 + annual_rent_increase / 12)
        investment_value_rent[month] = investment_value_rent[month - 1] * (1 + annual_investment_return / 12) + paycheck[month - 1] - rent[month - 1]

        if month <= mortgage_length * 12:
            interest_payment = mortgage_balance[month - 1] * (mortgage_interest_rate / 12)
            principal_payment = mortgage_payment - interest_payment
            mortgage_balance[month] = mortgage_balance[month - 1] - principal_payment
            equity[month] = home_value[month - 1] - mortgage_balance[month]
            extra_investment[month] = 0
        else:
            equity[month] = home_value[month - 1]
            extra_investment[month] = paycheck[month - 1] - monthly_maintenance
            investment_value_buy[month] = investment_value_buy[month - 1] * (1 + annual_investment_return / 12) + extra_investment[month - 1]
        
        home_value[month] = home_value[month - 1] * (1 + house_appreciation_rate / 12)

        if month % 12 == 0:
            paycheck[month] = paycheck[month - 12] * (1 + annual_raise)
        else:
            paycheck[month] = paycheck[month - 1]

        net_worth_rent[month] = investment_value_rent[month]
        net_worth_buy[month] = equity[month] + investment_value_buy[month]
    
    df = pd.DataFrame({
        'Month': np.arange(1, months + 1),
        'Rent': rent,
        'Investment Value (Rent)': investment_value_rent,
        'Home Value': home_value,
        'Mortgage Balance': mortgage_balance,
        'Equity': equity,
        'Investment Value (Buy)': investment_value_buy,
        'Net Worth (Rent)': net_worth_rent,
        'Net Worth (Buy)': net_worth_buy
    })

    plt.figure(figsize=(12, 8))
    plt.plot(df['Month'] / 12, df['Net Worth (Rent)'], label='Net Worth (Rent)')
    plt.plot(df['Month'] / 12, df['Net Worth (Buy)'], label='Net Worth (Buy)')
    plt.xlabel('Years')
    plt.ylabel('Net Worth')
    plt.title('Net Worth Over Time: Renting vs Buying')
    plt.legend()
    plt.grid(True)
    plt.show()

    return df

monthly_rent = 3000
annual_rent_increase = 0.03
annual_investment_return = 0.07
downpayment = 90000
mortgage_length = 15
mortgage_interest_rate = 0.06
monthly_maintenance = 1000
house_appreciation_rate = 0.04
monthly_paycheck = 3600
annual_raise = 0.03
house_price = 450000
simulation_years = mortgage_length + 30

df = simulate_rent_vs_buy(
    monthly_rent,
    annual_rent_increase,
    annual_investment_return,
    downpayment,
    mortgage_length,
    mortgage_interest_rate,
    monthly_maintenance,
    house_appreciation_rate,
    monthly_paycheck,
    annual_raise,
    house_price,
    simulation_years
)
