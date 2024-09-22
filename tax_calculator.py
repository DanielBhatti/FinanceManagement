def calculate_federal_tax(income: float):
    standard_deduction = 13850
    taxable_income = max(income - standard_deduction, 0)
    
    # 2023 Tax Brackets for Single Filers
    brackets = [
        (10_825, 0.10),
        (10_825, 0.10),
        (43_900, 0.12),
        (90_800, 0.22),
        (172_750, 0.24),
        (218_950, 0.32),
        (549_400, 0.35),
        (float('inf'), 0.37),
    ]
    
    tax = 0
    for limit, rate in brackets:
        if taxable_income > limit:
            tax += (limit * rate)
            taxable_income -= limit
        else:
            tax += (taxable_income * rate)
            break

    return tax

def calculate_medicare_tax(income):
    base_rate = 0.0145
    additional_rate = 0.009
    threshold = 200000
    medicare_tax = income * base_rate
    if income > threshold:
        medicare_tax += (income - threshold) * additional_rate
    return medicare_tax

def calculate_social_security_tax(income):
    rate = 0.062
    wage_base_limit = 160200
    social_security_tax = min(income, wage_base_limit) * rate
    return social_security_tax

def calculate_ny_state_tax(income):
    # Simplified tax brackets for NY as of 2023
    brackets = [
        (20_000, 0.04),
        (100_000, 0.045),
        (100_000, 0.0525),
        (200_000, 0.059),
        (500_000, 0.0645),
        (1_000_000, 0.068),
        (float('inf'), 0.07),
    ]
    
    standard_deduction = 8000
    taxable_income = max(income - standard_deduction, 0)
    
    tax = 0
    for limit, rate in brackets:
        if taxable_income > limit:
            tax += (limit * rate)
            taxable_income -= limit
        else:
            tax += (taxable_income * rate)
            break

    return tax

def calculate_total_taxes(income):
    federal_tax = calculate_federal_tax(income)
    medicare_tax = calculate_medicare_tax(income)
    social_security_tax = calculate_social_security_tax(income)
    ny_state_tax = calculate_ny_state_tax(income)
    total_tax = federal_tax + medicare_tax + social_security_tax + ny_state_tax
    return total_tax, federal_tax, medicare_tax, social_security_tax, ny_state_tax

# Example income
income = 148_000

total_tax, federal_tax, medicare_tax, social_security_tax, ny_state_tax = calculate_total_taxes(income)
print(f"Total Tax: ${total_tax:.2f}")
print(f"Federal Tax: ${federal_tax:.2f}")
print(f"Medicare Tax: ${medicare_tax:.2f}")
print(f"Social Security Tax: ${social_security_tax:.2f}")
print(f"NY State Tax: ${ny_state_tax:.2f}")
