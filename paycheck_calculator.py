from enum import Enum
from tax_bracket import FEDERAL_TAX_BRACKETS_INDIVIDUAL, STATE_TAX_BRACKETS_INDIVIDUAL, NYC_TAX_BRACKETS_INDIVIDUAL, NY_PFL_RATE, SOCIAL_SECURITY_MAX_TAXABLE_EARNINGS
from contribution_limit import LIMITS_401k_INDIVIDUAL_PRETAX, LIMITS_401k_INDIVIDUAL_TOTAL, LIMITS_401k_INDIVIDUAL_CATCHUP, LIMITS_HSA_INDIVIDUAL

class PaymentFrequency(Enum):
    WEEKLY = 52
    BIWEEKLY = 26
    BIMONTHLY = 24
    MONTHLY = 12
    YEARLY = 1

class BenefitDeduction:
    name: str
    is_pre_tax: bool
    amount: float

def calculate_income_taxes(income: float, tax_brackets: list[tuple[float, float]]):
    taxes = 0
    for limit, rate in tax_brackets:
        if income > limit:
            taxes += (limit * rate)
            income -= limit
        else:
            taxes += (income * rate)
            break
    return taxes

SOCIAL_SECURITY_TAX_RATE = 0.062
def calculate_social_security_tax(year: int, magi: float): return min(magi, SOCIAL_SECURITY_MAX_TAXABLE_EARNINGS[year]) * SOCIAL_SECURITY_TAX_RATE

MEDICARE_TAX_RATE = 0.0145
def calculate_medicare_tax(magi: float): return magi * MEDICARE_TAX_RATE + max(0.0, (magi-200_000)*0.009)

def calculate_niit_tax(agi: float, investment_income: float): return max(0.0, min(agi - 200_000, investment_income) * 0.038)

def calculate_ny_paid_family_leave_tax(year: int, magi: float): return min(magi * NY_PFL_RATE[year][0], NY_PFL_RATE[year][1])

def calculate_ny_disability_employee_tax(magi: float): return min(magi * 0.005, 0.60*52)

def calculate_paycheck_breakdown(payment_frequency: PaymentFrequency, year: int, salary_income: float, investment_income: float, pre_tax_401k: float, after_tax_401k: float, pre_tax_hsa: float, pre_tax_commuter: float, employer_max_match_rate: float, is_in_nyc: bool, additional_deductions: list[BenefitDeduction] = []) -> dict[str, float]:
    total_pre_tax_deductions = pre_tax_401k + pre_tax_hsa + pre_tax_commuter
    adjusted_income = salary_income + investment_income - total_pre_tax_deductions
    medicare_income = salary_income + investment_income - pre_tax_hsa - pre_tax_commuter

    federal_taxes = calculate_income_taxes(adjusted_income, FEDERAL_TAX_BRACKETS_INDIVIDUAL[year])
    state_taxes = calculate_income_taxes(adjusted_income, STATE_TAX_BRACKETS_INDIVIDUAL[year])
    ny_pfl_taxes = calculate_ny_paid_family_leave_tax(year, adjusted_income)
    ny_sdi_taxes = calculate_ny_disability_employee_tax(adjusted_income)
    nyc_taxes = calculate_income_taxes(adjusted_income, NYC_TAX_BRACKETS_INDIVIDUAL[year] if is_in_nyc else [])

    social_security_tax = calculate_social_security_tax(year, adjusted_income)
    medicare_tax = calculate_medicare_tax(medicare_income)
    niit_tax = calculate_niit_tax(medicare_income, investment_income)
    total_taxes = (federal_taxes + state_taxes + nyc_taxes + social_security_tax + 
                   medicare_tax + ny_pfl_taxes + ny_sdi_taxes + niit_tax)

    net_income_after_tax = adjusted_income - total_taxes
    net_income_after_tax_contributions = net_income_after_tax - after_tax_401k
    gross_income_per_period = (salary_income + investment_income) / payment_frequency.value
    net_income_per_period_after_tax = net_income_after_tax / payment_frequency.value
    net_income_per_period_after_tax_contributions = net_income_after_tax_contributions / payment_frequency.value
    employer_match_401k = salary_income * min(employer_max_match_rate, (pre_tax_401k + after_tax_401k) / salary_income) / payment_frequency.value

    return {
        "Gross Income Per Period": gross_income_per_period,
        "Net Income Per Period (Gross - Pretax)": net_income_per_period_after_tax,
        "Net Income Per Period (Gross - Pretax - Contributions)": net_income_per_period_after_tax_contributions,
        "Federal Tax": federal_taxes / payment_frequency.value,
        "State Tax": state_taxes / payment_frequency.value,
        "NY PFL Tax": ny_pfl_taxes / payment_frequency.value,
        "NY SDI Tax": ny_sdi_taxes / payment_frequency.value,
        "NYC Tax": nyc_taxes / payment_frequency.value,
        "Social Security Tax": social_security_tax / payment_frequency.value,
        "Medicare Tax": medicare_tax / payment_frequency.value,
        "NIIT Tax:": niit_tax / payment_frequency.value,
        "Pre-Tax 401k": pre_tax_401k / payment_frequency.value,
        "Roth/After-Tax 401k": after_tax_401k / payment_frequency.value,
        "Employer Match 401k": employer_match_401k,
        "Pre-Tax HSA": pre_tax_hsa / payment_frequency.value,
        "Pre-Tax Commuter": pre_tax_commuter / payment_frequency.value
    }


# def calculate_paycheck_breakdown_with_bonus(payment_frequency: PaymentFrequency, year: int, salary_income: float, bonus_income: float, investment_income: float, pre_tax_401k: float, roth_401k: float, pre_tax_hsa: float, pre_tax_commuter: float, employer_match_rate: float, is_in_nyc: bool):
#     paycheck_per_period, deductions = calculate_paycheck_breakdown(payment_frequency, year, salary_income + bonus_income, investment_income, pre_tax_401k, roth_401k, pre_tax_hsa, pre_tax_commuter, employer_match_rate, is_in_nyc)
    
#     return paycheck_per_period  / payment_frequency.value, deductions

year = 2024
payment_frequency = PaymentFrequency.MONTHLY
salary_income = 225_000
employer_max_match_rate = 0.03
investment_income = 0.0
pre_tax_401k = LIMITS_401k_INDIVIDUAL_PRETAX[year] + LIMITS_401k_INDIVIDUAL_CATCHUP[year]
after_tax_401k = 0#LIMITS_401k_INDIVIDUAL_TOTAL[year] - LIMITS_401k_INDIVIDUAL_PRETAX[year] - employer_max_match_rate * salary_income
pre_tax_hsa = LIMITS_HSA_INDIVIDUAL[year] - 850
pre_tax_commuter = 0
is_in_nyc = True

breakdown = calculate_paycheck_breakdown(
    payment_frequency,
    year,
    salary_income,
    investment_income,
    pre_tax_401k,
    after_tax_401k,
    pre_tax_hsa,
    pre_tax_commuter,
    employer_max_match_rate,
    is_in_nyc=is_in_nyc
)

print(f"Payment Frequency: {payment_frequency}")
for breakdown, amount in breakdown.items():
    print(f"{breakdown}: ${amount:.2f}")