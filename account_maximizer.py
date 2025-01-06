from contribution_limit import LIMITS_401k_INDIVIDUAL_PRETAX, LIMITS_401k_INDIVIDUAL_TOTAL

def calculate_401k_contributions(
    annual_salary: float,
    desired_pretax_401k: float,
    desired_roth_401k: float,
    max_employee_pretax_limit: float, # Example: employee pretax limit
    max_total_401k_limit: float, # Example: total (employer + employee)
    employer_match_rate: float, # Employer match percentage of employee contributions (usually 0.5 or 1.0)
    employer_match_cap: float # Employer match capped at percentage of salary (usually 0.03 to 0.06)
) -> dict:
    pretax_contribution = min(desired_pretax_401k, max_employee_pretax_limit)
    employee_total_401k = pretax_contribution + desired_roth_401k
    
    matchable_amount = min(employee_total_401k, employer_match_cap * annual_salary)
    employer_contribution = matchable_amount * employer_match_rate
    
    total_contribution = employee_total_401k + employer_contribution
    if total_contribution > max_total_401k_limit:
        overage = total_contribution - max_total_401k_limit
        
        if desired_roth_401k >= overage:
            desired_roth_401k -= overage
            overage = 0
        else:
            overage -= desired_roth_401k
            desired_roth_401k = 0
            pretax_contribution = max(0, pretax_contribution - overage)
        
        employee_total_401k = pretax_contribution + desired_roth_401k
        matchable_amount = min(employee_total_401k, employer_match_cap * annual_salary)
        employer_contribution = matchable_amount * employer_match_rate
        total_contribution = employee_total_401k + employer_contribution

    employee_pretax_percent = (pretax_contribution / annual_salary) * 100 if annual_salary > 0 else 0
    employee_roth_percent = (desired_roth_401k / annual_salary) * 100 if annual_salary > 0 else 0
    employer_percent = (employer_contribution / annual_salary) * 100 if annual_salary > 0 else 0
    
    return {
        "employee_pretax_401k": pretax_contribution,
        "employee_roth_401k": desired_roth_401k,
        "employer_401k_match": employer_contribution,
        "total_401k_contribution": total_contribution,
        "employee_pretax_percent": employee_pretax_percent,
        "employee_roth_percent": employee_roth_percent,
        "employer_net_percent": employer_percent,
    }

if __name__ == "__main__":
    year = 2025
    result = calculate_401k_contributions(
        annual_salary=225_000,
        desired_pretax_401k=LIMITS_401k_INDIVIDUAL_PRETAX[year],
        desired_roth_401k=LIMITS_401k_INDIVIDUAL_TOTAL[year] - LIMITS_401k_INDIVIDUAL_PRETAX[year],
        max_employee_pretax_limit=LIMITS_401k_INDIVIDUAL_PRETAX[year],
        max_total_401k_limit=LIMITS_401k_INDIVIDUAL_TOTAL[year],
        employer_match_rate=0.5,
        employer_match_cap=0.06
    )
    for k, v in result.items():
        print(f"{k}: {v:_}")
