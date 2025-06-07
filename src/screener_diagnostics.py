import yfinance as yf
import pandas as pd
import yaml
from typing import List, Dict
import os

def analyze_screening_issues():
    """Analyze why so few stocks are passing the screens"""
    
    # Load validated symbols
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'validated_symbols.yaml')
    with open(data_path, 'r') as f:
        data = yaml.safe_load(f)
    
    symbols = data.get('valid_symbols', [])
    
    print(f"Analyzing {len(symbols)} validated symbols...")
    
    # Sample 50 symbols for detailed analysis
    sample_symbols = symbols[:50]
    
    pe_ratios = []
    dividend_yields = []
    no_pe_count = 0
    no_dividend_count = 0
    
    for i, symbol_data in enumerate(sample_symbols, 1):
        symbol = symbol_data['symbol']
        print(f"Analyzing {symbol} ({i}/{len(sample_symbols)})")
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            pe_ratio = info.get('trailingPE', None)
            dividend_yield = info.get('dividendYield', 0) or 0
            
            print(f"  {symbol}: P/E = {pe_ratio}, Dividend = {dividend_yield:.1%}")
            
            if pe_ratio is not None and pe_ratio > 0:
                pe_ratios.append(pe_ratio)
            else:
                no_pe_count += 1
                print(f"    No valid P/E ratio")
            
            if dividend_yield > 0:
                dividend_yields.append(dividend_yield)
            else:
                no_dividend_count += 1
                print(f"    No dividend")
                
        except Exception as e:
            print(f"  Error with {symbol}: {e}")
    
    # Statistics
    if pe_ratios:
        pe_df = pd.Series(pe_ratios)
        print(f"\nP/E Ratio Statistics (from {len(pe_ratios)} stocks):")
        print(f"  Mean: {pe_df.mean():.1f}")
        print(f"  Median: {pe_df.median():.1f}")
        print(f"  Min: {pe_df.min():.1f}")
        print(f"  Max: {pe_df.max():.1f}")
        print(f"  25th percentile: {pe_df.quantile(0.25):.1f}")
        print(f"  75th percentile: {pe_df.quantile(0.75):.1f}")
        print(f"  Stocks with P/E <= 15: {sum(1 for pe in pe_ratios if pe <= 15)}")
        print(f"  Stocks with P/E <= 20: {sum(1 for pe in pe_ratios if pe <= 20)}")
        print(f"  Stocks with P/E <= 25: {sum(1 for pe in pe_ratios if pe <= 25)}")
    
    if dividend_yields:
        div_df = pd.Series(dividend_yields)
        print(f"\nDividend Yield Statistics (from {len(dividend_yields)} stocks):")
        print(f"  Mean: {div_df.mean():.1%}")
        print(f"  Median: {div_df.median():.1%}")
        print(f"  Min: {div_df.min():.1%}")
        print(f"  Max: {div_df.max():.1%}")
        print(f"  Stocks with dividend >= 1%: {sum(1 for div in dividend_yields if div >= 0.01)}")
        print(f"  Stocks with dividend >= 2%: {sum(1 for div in dividend_yields if div >= 0.02)}")
        print(f"  Stocks with dividend >= 3%: {sum(1 for div in dividend_yields if div >= 0.03)}")
    
    print(f"\nSymbols without valid P/E: {no_pe_count}")
    print(f"Symbols without dividends: {no_dividend_count}")

def test_relaxed_criteria():
    """Test with very relaxed criteria to see potential"""
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'validated_symbols.yaml')
    with open(data_path, 'r') as f:
        data = yaml.safe_load(f)
    
    symbols = data.get('valid_symbols', [])
    
    # Very relaxed criteria
    max_pe = 50
    min_dividend = 0.005  # 0.5%
    
    passed_count = 0
    
    for symbol_data in symbols[:100]:  # Test first 100
        symbol = symbol_data['symbol']
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            pe_ratio = info.get('trailingPE', None)
            dividend_yield = info.get('dividendYield', 0) or 0
            
            if pe_ratio is not None and pe_ratio > 0 and pe_ratio <= max_pe and dividend_yield >= min_dividend:
                passed_count += 1
                
        except:
            continue
    
    print(f"\nWith relaxed criteria (P/E <= {max_pe}, Dividend >= {min_dividend:.1%}):")
    print(f"Passed: {passed_count} out of 100 tested stocks")

if __name__ == "__main__":
    analyze_screening_issues()
    test_relaxed_criteria()