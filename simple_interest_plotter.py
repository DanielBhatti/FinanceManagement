import matplotlib.pyplot as plt

def calculate_monthly_payment(principal, annual_interest_rate, loan_term_years):
    monthly_interest_rate = annual_interest_rate / 12
    total_months = loan_term_years * 12
    monthly_payment = (principal * monthly_interest_rate) / (1 - (1 + monthly_interest_rate) ** -total_months)
    return monthly_payment

def simulate_loan_repayment(principal, annual_interest_rate, loan_term_years):
    monthly_payment = calculate_monthly_payment(principal, annual_interest_rate, loan_term_years)
    monthly_interest_rate = annual_interest_rate / 12
    total_months = loan_term_years * 12
    
    months = []
    remaining_principal = []
    total_interest_paid = []
    total_amount_paid = []

    current_principal = principal
    current_total_interest_paid = 0
    current_total_amount_paid = 0
    
    for month in range(1, total_months + 1):
        interest_payment = current_principal * monthly_interest_rate
        principal_payment = monthly_payment - interest_payment

        if current_principal - principal_payment < 0:
            principal_payment = current_principal
            monthly_payment = principal_payment + interest_payment
        
        current_principal -= principal_payment
        current_total_interest_paid += interest_payment
        current_total_amount_paid += monthly_payment

        months.append(month)
        remaining_principal.append(current_principal)
        total_interest_paid.append(current_total_interest_paid)
        total_amount_paid.append(current_total_amount_paid)

        if current_principal <= 0:
            break

    return months, remaining_principal, total_interest_paid, total_amount_paid, monthly_payment, current_total_interest_paid, current_total_amount_paid

principal = 42_755
annual_interest_rate = 0.0699
loan_term_years = 4

months, remaining_principal, total_interest_paid, total_amount_paid, monthly_payment, final_total_interest_paid, final_total_amount_paid = simulate_loan_repayment(
    principal, annual_interest_rate, loan_term_years)

print(f"Monthly Payment: ${monthly_payment:.2f}")
print(f"Total Interest Paid: ${final_total_interest_paid:.2f}")
print(f"Total Amount Paid: ${final_total_amount_paid:.2f}")

plt.figure(figsize=(12, 8))

plt.subplot(2, 2, 1)
plt.plot(months, remaining_principal, label='Remaining Principal')
plt.xlabel('Month')
plt.ylabel('Amount ($)')
plt.title('Remaining Principal Over Time')
plt.legend()

plt.subplot(2, 2, 2)
plt.plot(months, total_interest_paid, label='Total Interest Paid', color='orange')
plt.xlabel('Month')
plt.ylabel('Amount ($)')
plt.title('Total Interest Paid Over Time')
plt.legend()

plt.subplot(2, 2, 3)
plt.plot(months, total_amount_paid, label='Total Amount Paid', color='green')
plt.xlabel('Month')
plt.ylabel('Amount ($)')
plt.title('Total Amount Paid Over Time')
plt.legend()

plt.subplot(2, 2, 4)
plt.plot(months, total_amount_paid, label='Total Amount Paid', color='green')
plt.plot(months, total_interest_paid, label='Total Interest Paid', color='orange')
plt.plot(months, remaining_principal, label='Remaining Principal', color='blue')
plt.xlabel('Month')
plt.ylabel('Amount ($)')
plt.title('Loan Repayment Overview')
plt.legend()

plt.tight_layout()
plt.show()
