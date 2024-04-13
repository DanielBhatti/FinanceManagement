import numpy as np
import matplotlib.pyplot as plt

FEDERAL_TAX_RATE = 0.24
STATE_TAX_RATE = 0.0649
FICA_TAX_RATE = 0.0765

THP_YEARLY_PREMIUM_IN = 97.62 * (1 - FEDERAL_TAX_RATE - STATE_TAX_RATE - FICA_TAX_RATE) * 12
THP_DEDUCTIBLE_IN = 1000
THP_MAX_OUT_POCKET_IN = 2000
THP_COINSURANCE_IN = 0.10

THP_YEARLY_PREMIUM_OUT = 120 * 12
THP_DEDUCTIBLE_OUT = 2000
THP_MAX_OUT_POCKET_OUT = 3000
THP_COINSURANCE_OUT = 0.30

HDHP_YEARLY_PREMIUM_IN = 0
HDHP_DEDUCTIBLE_IN = 2000
HDHP_MAX_OUT_POCKET_IN = 5000
HDHP_COINSURANCE_IN = 0.10

HDHP_YEARLY_PREMIUM_OUT = 0
HDHP_DEDUCTIBLE_OUT = 4000
HDHP_MAX_OUT_POCKET_OUT = 12000
HDHP_COINSURANCE_OUT = 0.30

EMPLOYER_HSA_CONTRIBUTION = 1500
EMPLOYEE_HSA_CONTRIBUTION = 2650

def calculate_thp_cost(qhe: float, in_network: bool = True):
    if in_network:
        deductible = THP_DEDUCTIBLE_IN
        max_out_pocket = THP_MAX_OUT_POCKET_IN
        coinsurance = THP_COINSURANCE_IN
        yearly_premium = THP_YEARLY_PREMIUM_IN
    else:
        deductible = THP_DEDUCTIBLE_OUT
        max_out_pocket = THP_MAX_OUT_POCKET_OUT
        coinsurance = THP_COINSURANCE_OUT
        yearly_premium = THP_YEARLY_PREMIUM_OUT
        
    if qhe <= deductible:
        cost = qhe
    else:
        cost = min(deductible + coinsurance * (qhe - deductible), max_out_pocket)
        
    return yearly_premium + cost

def calculate_hdhp_cost(qhe: float, in_network: bool = True):
    if in_network:
        deductible = HDHP_DEDUCTIBLE_IN
        max_out_pocket = HDHP_MAX_OUT_POCKET_IN
        coinsurance = HDHP_COINSURANCE_IN
        yearly_premium = HDHP_YEARLY_PREMIUM_IN
    else:
        deductible = HDHP_DEDUCTIBLE_OUT
        max_out_pocket = HDHP_MAX_OUT_POCKET_OUT
        coinsurance = HDHP_COINSURANCE_OUT
        yearly_premium = HDHP_YEARLY_PREMIUM_OUT
    if qhe <= deductible:
        cost = qhe
    else:
        cost = min(deductible + coinsurance * (qhe - deductible), max_out_pocket)
    
    return cost + yearly_premium - EMPLOYER_HSA_CONTRIBUTION - EMPLOYEE_HSA_CONTRIBUTION * (FEDERAL_TAX_RATE + STATE_TAX_RATE + FICA_TAX_RATE)

qhe_values = np.linspace(0, 50000, 500)

thp_costs_in = [calculate_thp_cost(qhe) for qhe in qhe_values]
thp_costs_out = [calculate_thp_cost(qhe, in_network=False) for qhe in qhe_values]
hdhp_costs_in = [calculate_hdhp_cost(qhe) for qhe in qhe_values]
hdhp_costs_out = [calculate_hdhp_cost(qhe, in_network=False) for qhe in qhe_values]

plt.figure(figsize=(10, 6))

plt.plot(qhe_values, thp_costs_in, label='Traditional Health Plan (In-Network)')
#plt.plot(qhe_values, thp_costs_out, label='Traditional Health Plan (Out-of-Network)')
plt.plot(qhe_values, hdhp_costs_in, label='High Deductible Health Plan (In-Network)')
#plt.plot(qhe_values, hdhp_costs_out, label='High Deductible Health Plan (Out-of-Network)')

plt.title('Qualified Health Expenses vs Effective Cost')
plt.xlabel('Qualified Health Expenses ($)')
plt.ylabel('Effective Cost ($)')
plt.legend()
plt.grid(True)
plt.show()
