import math
import matplotlib.pyplot as plt

class MortgageEvent:
    """
    Defines a mortgage "event" (e.g., refinance) at a specific month.
      - new_mortgage_type: 'fixed' or 'arm'
      - new_margin
      - new_term_years (the new total length from this event forward)
      - new_principal (if None, keep old balance)
      - fees (closing costs, etc.) -> added to the balance
      - name (for logging)
    """
    def __init__(
        self, 
        month,
        new_mortgage_type=None,
        new_margin=None,
        new_term_years=None,
        new_principal=None,
        fees=0.0,
        name=None
    ):
        self.month = month
        self.new_mortgage_type = new_mortgage_type
        self.new_margin = new_margin
        self.new_term_years = new_term_years
        self.new_principal = new_principal
        self.fees = fees
        self.name = name or f"Event@{month}"

class Mortgage:
    """
    Handles:
      - Fixed or ARM interest rate
      - Hybrid ARM schedules (e.g. "5/1", "7/2", etc.)
      - ARM caps (e.g. "2/2/5")
      - Refinance events
      - Fed rate history
      - Fees
    """

    def __init__(
        self,
        principal,
        fed_rates,
        margin,
        term_years=30,
        mortgage_type='fixed',
        arm_schedule=None,       
        arm_caps=None,           
        events=None
    ):
        """
        principal   : Starting loan amount
        fed_rates   : List of monthly Fed rates (decimals, length >= term)
        margin      : Extra interest above Fed rate (e.g. 0.02 => 2%)
        term_years  : Initial total mortgage term in years
        mortgage_type : 'fixed' or 'arm'
        arm_schedule  : e.g. "5/1" => 5 yrs fixed, then adjusts every 1 yr
        arm_caps      : e.g. "2/2/5" => initial/periodic/lifetime caps
        events      : list of MortgageEvent for refinances, etc.
        """
        import re
        self.initial_principal = principal
        self.fed_rates = fed_rates
        self.margin = margin
        self.term_months = term_years * 12
        self.mortgage_type = mortgage_type
        self.events = sorted(events, key=lambda e: e.month) if events else []

        # Parse ARM schedule if needed
        self.arm_fixed_years = 0
        self.arm_adjust_period_years = 0
        if arm_schedule and mortgage_type == 'arm':
            fixed_str, adjust_str = arm_schedule.split('/')
            self.arm_fixed_years = int(fixed_str.strip())
            self.arm_adjust_period_years = int(adjust_str.strip())

        # Parse ARM caps if needed, e.g. "2/2/5"
        self.arm_initial_cap = None
        self.arm_periodic_cap = None
        self.arm_lifetime_cap = None
        if arm_caps and mortgage_type == 'arm':
            init_str, sub_str, life_str = arm_caps.split('/')
            # Convert strings to float. If something like '2' => 0.02, but if user typed '0.02' => 0.02
            self.arm_initial_cap = float(init_str.strip())/100.0 if float(init_str) > 1 else float(init_str)
            self.arm_periodic_cap = float(sub_str.strip())/100.0 if float(sub_str) > 1 else float(sub_str)
            self.arm_lifetime_cap = float(life_str.strip())/100.0 if float(life_str) > 1 else float(life_str)

        # Internal
        self.balance = principal
        self.results = []
        self.locked_fed_rate = None
        self.initial_arm_rate = None
        self.current_month = 0
        self.monthly_payment = 0.0
        self._locked_chunk_rates = {}

    def get_annual_interest_rate(self, month_idx):
        # Fixed => locked fed rate
        if self.mortgage_type == 'fixed':
            if self.locked_fed_rate is None:
                self.locked_fed_rate = self.fed_rates[0] if self.fed_rates else 0.0
            return self.locked_fed_rate + self.margin

        # ARM => either a schedule or just pick month_idx + margin
        if self.arm_fixed_years>0 and self.arm_adjust_period_years>0:
            base_rate = self._get_custom_arm_rate(month_idx)
        else:
            # If no schedule, treat it as a generic immediate ARM
            base_rate = (self.fed_rates[month_idx] + self.margin
                         if month_idx < len(self.fed_rates)
                         else self.fed_rates[-1] + self.margin)
        return self._apply_arm_caps(month_idx, base_rate)

    def _get_custom_arm_rate(self, month_idx):
        if month_idx < 0:
            month_idx = 0
        total_fed_len = len(self.fed_rates)

        # initial fixed
        fixed_months = self.arm_fixed_years*12
        adjust_months = self.arm_adjust_period_years*12

        if month_idx < fixed_months:
            # in initial fixed
            if self.locked_fed_rate is None:
                self.locked_fed_rate = self.fed_rates[0] if total_fed_len>0 else 0.0
            return self.locked_fed_rate + self.margin

        # beyond initial fixed
        months_into_adjust = month_idx - fixed_months
        chunk_idx = months_into_adjust // adjust_months
        chunk_key = f"chunk_{chunk_idx}"
        if chunk_key not in self._locked_chunk_rates:
            start_m = fixed_months + chunk_idx*adjust_months
            if start_m >= total_fed_len:
                rate_to_lock = self.fed_rates[-1] if total_fed_len>0 else 0.0
            else:
                rate_to_lock = self.fed_rates[start_m]
            self._locked_chunk_rates[chunk_key] = rate_to_lock
        locked_chunk_rate = self._locked_chunk_rates[chunk_key]
        return locked_chunk_rate + self.margin

    def _apply_arm_caps(self, month_idx, new_rate):
        # if no caps, return
        if not all([self.arm_initial_cap, self.arm_periodic_cap, self.arm_lifetime_cap]):
            return new_rate

        if not self.results:  
            # first month => set initial_arm_rate
            self.initial_arm_rate = new_rate
            return new_rate

        old_rate = self.results[-1]['annual_interest_rate']
        if self.initial_arm_rate is None:
            self.initial_arm_rate = old_rate

        max_lifetime = self.initial_arm_rate + self.arm_lifetime_cap

        # track if we've done first adjustment
        if not hasattr(self, '_did_first_arm_adjust'):
            self._did_first_arm_adjust = False

        # did rate actually change
        changed = abs(new_rate - old_rate)>1e-9
        if changed and not self._did_first_arm_adjust:
            self._did_first_arm_adjust = True
            # clamp by initial cap
            capped = min(new_rate, old_rate + self.arm_initial_cap)
        elif changed:
            # subsequent adjustments
            capped = min(new_rate, old_rate + self.arm_periodic_cap)
        else:
            capped = new_rate

        # apply lifetime
        capped = min(capped, max_lifetime)
        return capped

    def calculate_monthly_payment(self, annual_rate, balance, remaining_months):
        r = annual_rate/12
        if r<=0:
            return balance/remaining_months
        return (balance*r)/(1-(1+r)**(-remaining_months))

    def simulate(self):
        event_idx = 0
        num_events = len(self.events)

        # If we start fixed
        if self.mortgage_type=='fixed' and self.locked_fed_rate is None:
            self.locked_fed_rate = self.fed_rates[0] if self.fed_rates else 0.0

        # initial payment
        annual_rate_now = self.get_annual_interest_rate(0)
        self.monthly_payment = self.calculate_monthly_payment(
            annual_rate_now, self.balance, self.term_months
        )

        for month in range(1, self.term_months+1):
            self.current_month = month

            # process events
            while event_idx < num_events and self.events[event_idx].month == month:
                ev = self.events[event_idx]
                event_idx+=1
                if ev.new_principal is not None:
                    self.balance = ev.new_principal
                self.balance += ev.fees

                if ev.new_mortgage_type:
                    self.mortgage_type = ev.new_mortgage_type
                    if self.mortgage_type=='fixed':
                        idx = min(month-1, len(self.fed_rates)-1)
                        self.locked_fed_rate = self.fed_rates[idx]

                if ev.new_margin is not None:
                    self.margin = ev.new_margin

                if ev.new_term_years is not None:
                    new_full = (month-1)+ev.new_term_years*12
                    self.term_months = new_full

                annual_rate_now = self.get_annual_interest_rate(month-1)
                rem = self.term_months-(month-1)
                if rem<=0:
                    break
                self.monthly_payment = self.calculate_monthly_payment(
                    annual_rate_now, self.balance, rem
                )

            if month>self.term_months or self.balance<=0:
                break

            if self.mortgage_type=='arm':
                annual_rate_now = self.get_annual_interest_rate(month-1)
                rem = self.term_months-(month-1)
                if rem<=0:
                    break
                self.monthly_payment = self.calculate_monthly_payment(
                    annual_rate_now, self.balance, rem
                )

            # interest/principal
            r = annual_rate_now/12
            interest_paid = self.balance*r
            principal_paid = self.monthly_payment-interest_paid
            if principal_paid>self.balance:
                principal_paid = self.balance
                self.monthly_payment = interest_paid+principal_paid
            self.balance -= principal_paid

            self.results.append({
                'month': month,
                'annual_interest_rate': annual_rate_now,
                'interest_paid': interest_paid,
                'principal_paid': principal_paid,
                'remaining_balance': self.balance
            })

            if self.balance<=0:
                break

        return self.results


#
# PLOTTING
#

def plot_fed_rate_history(fed_rates):
    """
    Creates a Figure for Fed rate history and returns it.
    Does not call plt.show().
    """
    fig = plt.figure(figsize=(8,4))
    ax = fig.add_subplot(111)
    months = range(1, len(fed_rates)+1)
    ax.plot(months, fed_rates, label="Fed Rate")
    ax.set_title("Fed Rate History")
    ax.set_xlabel("Month")
    ax.set_ylabel("Fed Rate (decimal)")
    ax.legend()
    fig.tight_layout()
    return fig

def plot_mortgages_3x2(mortgage_results_dict, title="Mortgage Comparison 3x2"):
    """
    Creates a 3x2 plot for multiple mortgage scenarios, returning a Figure.
    Subplots:
      (0,0) => Monthly Interest
      (0,1) => Monthly Principal
      (1,0) => Monthly Payment (interest + principal)
      (1,1) => Total Amount Paid (cumulative sum)
      (2,0) => Remaining Balance
      (2,1) => Annual Interest Rate
    """
    import numpy as np

    fig, axs = plt.subplots(3, 2, figsize=(12, 12))

    ax_interest     = axs[0][0]
    ax_principal    = axs[0][1]
    ax_monthly_pay  = axs[1][0]
    ax_total_paid   = axs[1][1]
    ax_balance      = axs[2][0]
    ax_rate         = axs[2][1]

    for label, results in mortgage_results_dict.items():
        months    = [r['month'] for r in results]
        interests = [r['interest_paid'] for r in results]
        principals= [r['principal_paid'] for r in results]
        balances  = [r['remaining_balance'] for r in results]
        rates     = [r['annual_interest_rate'] for r in results]

        # monthly payment
        payments = [i + p for i,p in zip(interests, principals)]

        # cumulative sum of monthly payments
        total_paid = np.cumsum(payments)

        # Plot each subplot
        ax_interest.plot(months, interests, label=f"{label} Interest")
        ax_principal.plot(months, principals, label=f"{label} Principal")
        ax_monthly_pay.plot(months, payments, label=f"{label} Payment")
        ax_total_paid.plot(months, total_paid, label=f"{label} Total Paid")
        ax_balance.plot(months, balances, label=f"{label} Balance")
        ax_rate.plot(months, rates, label=f"{label} Rate")

    # Labeling
    ax_interest.set_title("Monthly Interest")
    ax_interest.set_ylabel("Dollars")
    ax_interest.legend()

    ax_principal.set_title("Monthly Principal")
    ax_principal.set_ylabel("Dollars")
    ax_principal.legend()

    ax_monthly_pay.set_title("Monthly Payment")
    ax_monthly_pay.set_ylabel("Dollars")
    ax_monthly_pay.legend()

    ax_total_paid.set_title("Total Amount Paid")
    ax_total_paid.set_ylabel("Dollars")
    ax_total_paid.legend()

    ax_balance.set_title("Remaining Balance")
    ax_balance.set_ylabel("Dollars")
    ax_balance.set_xlabel("Month")
    ax_balance.legend()

    ax_rate.set_title("Annual Interest Rate")
    ax_rate.set_ylabel("Decimal (e.g., 0.04=4%)")
    ax_rate.set_xlabel("Month")
    ax_rate.legend()

    fig.suptitle(title)
    fig.tight_layout()
    return fig

#
# EXAMPLE USAGE
#

def example_usage():
    import random
    random.seed(42)

    # 1) Create a Fed rate history for ~30 years (360 months).
    fed_rates = []
    current_rate = 0.0433
    for _ in range(360):
        delta = random.uniform(-0.001, 0.0013)
        current_rate = max(0.0, current_rate + delta)
        fed_rates.append(current_rate)

    # 2) Plot Fed rate (first window)
    fig_fed = plot_fed_rate_history(fed_rates)

    # 3) Create some mortgage examples
    principal = 400000

    # a) 30-year Fixed
    mortgage_fixed = Mortgage(
        principal=principal,
        fed_rates=fed_rates,
        margin=0.03,
        term_years=30,
        mortgage_type='fixed'
    )
    fixed_results = mortgage_fixed.simulate()

    # b) 5/1 ARM with 2/2/5 caps
    mortgage_arm_5_1 = Mortgage(
        principal=principal,
        fed_rates=fed_rates,
        margin=0.015,
        term_years=30,
        mortgage_type='arm',
        arm_schedule="5/1",  # 5 yrs fixed, then adjusts yearly
        arm_caps="2/2/5"
    )
    arm_5_1_results = mortgage_arm_5_1.simulate()

    # c) 7/2 ARM with 2/2/5 caps
    mortgage_arm_7_2 = Mortgage(
        principal=principal,
        fed_rates=fed_rates,
        margin=0.015,
        term_years=30,
        mortgage_type='arm',
        arm_schedule="7/2",
        arm_caps="2/2/5"
    )
    arm_7_2_results = mortgage_arm_7_2.simulate()

    # d) Refinance Example:
    #    Start as a 5/1 ARM, then at month 60 (after 5 years), switch to fixed
    #    with some fees ($2,000) rolled in, keep the old principal (None).
    events_refi = [
        MortgageEvent(
            month=60,
            new_mortgage_type='fixed',
            new_margin=0.03,       # suppose after 5 years, we fix at fed_rate + 3%
            new_term_years=25,     # new 25-year term from that point
            fees=2000.0,
            name="RefiToFixed@Month60"
        )
    ]
    mortgage_refi = Mortgage(
        principal=principal,
        fed_rates=fed_rates,
        margin=0.02,
        term_years=30,
        mortgage_type='arm',
        arm_schedule="5/1",
        arm_caps="2/2/5",
        events=events_refi
    )
    refi_results = mortgage_refi.simulate()

    # 4) Plot the mortgages in a 3x2 grid (second window)
    results_dict = {
        "Fixed30": fixed_results,
        "5/1 ARM": arm_5_1_results,
        #"7/2 ARM": arm_7_2_results,
        "Refi (5/1->Fixed)": refi_results
    }
    fig_compare = plot_mortgages_3x2(results_dict, title="Mortgage Comparison (3x2): Interest, Principal, Payment, etc.")

    # 5) Finally, show both figures
    plt.show()

if __name__ == "__main__":
    example_usage()
