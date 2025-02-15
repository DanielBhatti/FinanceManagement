import csv

class OptionPosition:
    def __init__(
        self, 
        symbol: str, 
        purchase_date: str,
        option_price_purchase: float, 
        underlying_price_purchase: float,
        dividend_yield: float,
        strike_price: float,
        current_option_price: float, 
        current_underlying_price: float
    ):
        self.symbol = symbol
        self.purchase_date = purchase_date
        self.option_price_purchase = option_price_purchase
        self.underlying_price_purchase = underlying_price_purchase
        self.dividend_yield = dividend_yield
        self.strike_price = strike_price
        self.current_option_price = current_option_price
        self.current_underlying_price = current_underlying_price

    def actual_option_pnl(self) -> float:
        return self.current_option_price - self.option_price_purchase
    
    def shares_with_option_cost(self) -> float:
        return self.option_price_purchase / self.underlying_price_purchase
    
    def final_value_of_shares(self) -> float:
        return self.shares_with_option_cost() * (self.current_underlying_price + self.dividend_yield)
    
    def stock_pnl(self) -> float:
        return self.final_value_of_shares() - self.option_price_purchase
    
    def pnl_proportion(self) -> float:
        return (self.actual_option_pnl() - self.stock_pnl()) / abs(self.stock_pnl())
        
    def breakeven(self) -> float:
        return self.strike_price + self.option_price_purchase / 100.0

    def initial_moneyness(self) -> float:
        return self.underlying_price_purchase / self.strike_price

    def final_moneyness(self) -> float:
        return self.current_underlying_price / self.strike_price

def read_options_from_csv(csv_filename: str) -> list[OptionPosition]:
    option_positions: list[OptionPosition] = []
    with open(csv_filename, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            pos = OptionPosition(
                symbol = row['symbol'],
                purchase_date = row['purchase_date'],
                option_price_purchase = float(row['option_price_purchase']),
                underlying_price_purchase = float(row['underlying_price_purchase']),
                dividend_yield = float(row['dividend_yield']),
                strike_price = float(row['strike_price']),
                current_option_price = float(row['current_option_price']),
                current_underlying_price = float(row['current_underlying_price'])
            )
            option_positions.append(pos)
    return option_positions

def compare_options(option_positions: list[OptionPosition]) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for pos in option_positions:
        results.append({
            'symbol': pos.symbol,
            'purchase_date': pos.purchase_date,
            'option_cost': pos.option_price_purchase,
            'stock_cost': pos.underlying_price_purchase,
            'current_option_price': pos.current_option_price,
            'current_stock_price': pos.current_underlying_price,
            'option_PnL': pos.actual_option_pnl(),
            'stock_PnL': pos.stock_pnl(),
            'PnL_ratio': pos.pnl_proportion(),
            "breakeven": pos.breakeven(),
            "initial_moneyness": pos.initial_moneyness(),
            "final_moneyness": pos.final_moneyness(),
        })
    return results

def print_tabular(dict_list: list[dict[str, object]]):
    if not dict_list:
        print("No data to display.")
        return
    
    headers = list(dict_list[0].keys())
    
    col_widths = {}
    for h in headers:
        max_val_len = max(len(str(row[h])) for row in dict_list)
        col_widths[h] = max(len(h), max_val_len)
    
    header_line = "  ".join(f"{h:{col_widths[h]}}" for h in headers)
    print(header_line)
    
    separator_line = "  ".join("-" * col_widths[h] for h in headers)
    print(separator_line)
    
    for row in dict_list:
        row_line = "  ".join(f"{str(row[h]):{col_widths[h]}}" for h in headers)
        print(row_line)


if __name__ == "__main__":
    positions = [
        OptionPosition("TQQQ", "2024-06-21", 5150.68, 74.90, 1.00, 25.00, 5990.00, 83.14), # 2025-01-19
        OptionPosition("TQQQ", "2024-07-29", 4300.68, 66.27, 1.00, 25.00, 5990.00, 83.14), # 2025-01-19
        OptionPosition("TQQQ", "2024-08-07", 3470.68, 57.57, 1.00, 25.00, 5990.00, 83.14), # 2025-01-19
        OptionPosition("TQQQ", "2024-11-27", 7181.35/2, 79.29, 0.25, 60.00, 7948.00/2, 83.14), # 2025-01-19
        OptionPosition("TQQQ", "2024-09-18", 5101.36/2, 67.02, 0.25, 60.00, 7948.00/2, 83.14), # 2025-01-19

        OptionPosition("TQQQ", "2024-06-21", 5150.68, 74.90, 1.00, 25.00, 6150.00, 87.80), # 2025-01-22
        OptionPosition("TQQQ", "2024-07-29", 4300.68, 66.27, 1.00, 25.00, 6150.00, 87.80), # 2025-01-22
        OptionPosition("TQQQ", "2024-08-07", 3470.68, 57.57, 1.00, 25.00, 6150.00, 87.80), # 2025-01-22
        OptionPosition("TQQQ", "2024-11-27", 7181.35/2, 79.29, 0.25, 60.00, 4000, 87.80), # 2025-01-22
        OptionPosition("TQQQ", "2024-09-18", 5101.36/2, 67.02, 0.25, 60.00, 4000, 87.80), # 2025-01-22
    ]
    
    comparison = compare_options(positions)
    
    print_tabular(comparison)