"""Stock screening workflow"""
import sys
import os
import yaml
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from screener import StockScreener

def load_validated_symbols():
    """Load previously validated symbols from file"""
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'validated_symbols.yaml')
    
    if not os.path.exists(data_path):
        print(f"Error: Validated symbols file not found at {data_path}")
        print("Please run symbol validation first: python src/symbol_validator.py")
        return []
    
    with open(data_path, 'r') as f:
        data = yaml.safe_load(f)
    
    return data.get('valid_symbols', [])

def run_momentum_screen():
    """Run momentum-based screening with realistic criteria"""
    print("Loading validated symbols...")
    symbols = load_validated_symbols()
    
    if not symbols:
        print("No validated symbols found. Exiting.")
        return []
    
    print(f"Loaded {len(symbols)} validated symbols")
    
    screener = StockScreener()
    # Use realistic criteria for S&P 500
    momentum_stocks = screener.momentum_screen(
        symbols,
        min_return_3m=0.05,  # 5% minimum 3-month return
        min_volume_ratio=0.8  # Recent volume at least 80% of historical average
    )
    
    screener.save_results(momentum_stocks, 'momentum_screen')
    return momentum_stocks

def run_realistic_value_screen():
    """Run realistic value-based screening"""
    print("Loading validated symbols...")
    symbols = load_validated_symbols()
    
    if not symbols:
        print("No validated symbols found. Exiting.")
        return []
    
    print(f"Loaded {len(symbols)} validated symbols")
    
    screener = StockScreener()
    # Use the realistic value screen method
    value_stocks = screener.realistic_value_screen(symbols)
    
    screener.save_results(value_stocks, 'realistic_value_screen')
    return value_stocks

def run_value_screen():
    """Run traditional value-based screening (more restrictive)"""
    print("Loading validated symbols...")
    symbols = load_validated_symbols()
    
    if not symbols:
        print("No validated symbols found. Exiting.")
        return []
    
    print(f"Loaded {len(symbols)} validated symbols")
    
    screener = StockScreener()
    # Traditional value criteria (more restrictive)
    value_stocks = screener.value_screen(
        symbols,
        max_pe=20,           # P/E ratio <= 20
        min_dividend_yield=0.02  # Dividend yield >= 2%
    )
    
    screener.save_results(value_stocks, 'traditional_value_screen')
    return value_stocks

if __name__ == "__main__":
    print("Stock Screening Workflow")
    print("=" * 40)
    
    # Run momentum screening
    print("\n1. Running Momentum Screen...")
    momentum_results = run_momentum_screen()
    print(f"Found {len(momentum_results)} momentum stocks")
    
    # Run realistic value screening
    print("\n2. Running Realistic Value Screen...")
    realistic_value_results = run_realistic_value_screen()
    print(f"Found {len(realistic_value_results)} realistic value stocks")
    
    # Run traditional value screening for comparison
    print("\n3. Running Traditional Value Screen...")
    traditional_value_results = run_value_screen()
    print(f"Found {len(traditional_value_results)} traditional value stocks")
    
    print("\nScreening workflow completed!")
    print(f"Total screens run: 3")
    print(f"Results saved to ../data/ directory")