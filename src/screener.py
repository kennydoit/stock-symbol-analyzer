import yfinance as yf
import pandas as pd
import yaml
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import os
import time

class StockScreener:
    def __init__(self):
        self.results = {}
    
    def momentum_screen(self, symbols: List[Dict], min_return_3m: float = 0.15, min_volume_ratio: float = 1.5) -> List[Dict]:
        """
        Screen for momentum stocks based on price performance and volume
        
        Args:
            symbols: List of validated symbol dictionaries
            min_return_3m: Minimum 3-month return (0.15 = 15%)
            min_volume_ratio: Minimum volume ratio vs average (1.5 = 50% above average)
        
        Returns:
            List of stocks meeting momentum criteria
        """
        print(f"Screening {len(symbols)} symbols for momentum...")
        momentum_stocks = []
        
        for i, symbol_data in enumerate(symbols, 1):
            symbol = symbol_data['symbol']
            print(f"Screening {symbol} ({i}/{len(symbols)})")
            
            try:
                ticker = yf.Ticker(symbol)
                
                # Get 6 months of data for momentum analysis
                hist = ticker.history(period="6mo")
                
                if len(hist) < 60:  # Need at least ~3 months of data
                    print(f"  ✗ {symbol}: Insufficient data for momentum analysis")
                    continue
                
                # Calculate 3-month return (more reliable calculation)
                if len(hist) >= 63:  # ~3 months of trading days
                    current_price = hist['Close'].iloc[-1]
                    three_month_price = hist['Close'].iloc[-63]
                    three_month_return = (current_price - three_month_price) / three_month_price
                else:
                    # Use available data if less than 3 months
                    current_price = hist['Close'].iloc[-1]
                    start_price = hist['Close'].iloc[0]
                    three_month_return = (current_price - start_price) / start_price
                
                # Fix volume calculation - compare recent vs longer-term average
                if len(hist) >= 20:
                    recent_volume = hist['Volume'].tail(5).mean()  # Last 5 days average
                    longer_term_volume = hist['Volume'].iloc[:-10].mean()  # Exclude last 10 days for comparison
                    
                    if longer_term_volume > 0:
                        volume_ratio = recent_volume / longer_term_volume
                    else:
                        volume_ratio = 1.0  # Neutral if no historical data
                else:
                    volume_ratio = 1.0  # Not enough data for volume comparison
                
                # Apply screening criteria
                passes_return = three_month_return >= min_return_3m
                passes_volume = volume_ratio >= min_volume_ratio
                
                print(f"  📊 {symbol}: Return {three_month_return:.1%}, Volume ratio {volume_ratio:.2f}x")
                
                if passes_return and passes_volume:
                    momentum_stock = {
                        'symbol': symbol,
                        'sector': symbol_data.get('sector', 'Unknown'),
                        'industry': symbol_data.get('industry', 'Unknown'),
                        'current_price': float(current_price),
                        'market_cap': symbol_data.get('market_cap', 0),
                        'three_month_return': float(three_month_return),
                        'volume_ratio': float(volume_ratio),
                        'recent_volume': float(recent_volume) if len(hist) >= 20 else 0,
                        'avg_volume': float(longer_term_volume) if len(hist) >= 20 else 0,
                        'screen_date': datetime.now().strftime('%Y-%m-%d')
                    }
                    momentum_stocks.append(momentum_stock)
                    print(f"  ✓ {symbol}: PASSED momentum screen")
                else:
                    reasons = []
                    if not passes_return:
                        reasons.append(f"Return {three_month_return:.1%} < {min_return_3m:.1%}")
                    if not passes_volume:
                        reasons.append(f"Volume {volume_ratio:.2f}x < {min_volume_ratio:.1f}x")
                    print(f"  ✗ {symbol}: {', '.join(reasons)}")
                
            except Exception as e:
                print(f"  ✗ {symbol}: Error - {str(e)}")
                continue
            
            # Rate limiting
            time.sleep(0.05)
        
        print(f"\nMomentum screening complete: {len(momentum_stocks)} stocks found")
        return momentum_stocks
    
    def relaxed_momentum_screen(self, symbols: List[Dict], min_return_3m: float = 0.05, min_volume_ratio: float = 0.8) -> List[Dict]:
        """
        More relaxed momentum screen for testing
        """
        print(f"Running relaxed momentum screen on {len(symbols)} symbols...")
        return self.momentum_screen(symbols, min_return_3m, min_volume_ratio)
    
    def value_screen(self, symbols: List[Dict], max_pe: float = 25, min_dividend_yield: float = 0.01) -> List[Dict]:
        """
        Screen for value stocks based on P/E ratio and dividend yield
        Made more relaxed for S&P 500 stocks
        """
        print(f"Screening {len(symbols)} symbols for value...")
        value_stocks = []
        
        for i, symbol_data in enumerate(symbols, 1):
            symbol = symbol_data['symbol']
            print(f"Screening {symbol} ({i}/{len(symbols)})")
            
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                pe_ratio = info.get('trailingPE', None)
                dividend_yield = info.get('dividendYield', 0) or 0
                
                if pe_ratio is None or pe_ratio <= 0:
                    print(f"  ✗ {symbol}: No valid P/E ratio")
                    continue
                
                passes_pe = pe_ratio <= max_pe
                passes_dividend = dividend_yield >= min_dividend_yield
                
                print(f"  📊 {symbol}: P/E {pe_ratio:.1f}, Dividend {dividend_yield:.1%}")
                
                if passes_pe and passes_dividend:
                    value_stock = {
                        'symbol': symbol,
                        'sector': symbol_data.get('sector', 'Unknown'),
                        'industry': symbol_data.get('industry', 'Unknown'),
                        'current_price': symbol_data.get('current_price', 0),
                        'market_cap': symbol_data.get('market_cap', 0),
                        'pe_ratio': float(pe_ratio),
                        'dividend_yield': float(dividend_yield),
                        'screen_date': datetime.now().strftime('%Y-%m-%d')
                    }
                    value_stocks.append(value_stock)
                    print(f"  ✓ {symbol}: PASSED value screen")
                else:
                    reasons = []
                    if not passes_pe:
                        reasons.append(f"P/E {pe_ratio:.1f} > {max_pe}")
                    if not passes_dividend:
                        reasons.append(f"Dividend {dividend_yield:.1%} < {min_dividend_yield:.1%}")
                    print(f"  ✗ {symbol}: {', '.join(reasons)}")
                
            except Exception as e:
                print(f"  ✗ {symbol}: Error - {str(e)}")
                continue
            
            # Rate limiting
            time.sleep(0.05)
        
        print(f"\nValue screening complete: {len(value_stocks)} stocks found")
        return value_stocks
    
    def realistic_value_screen(self, symbols: List[Dict]) -> List[Dict]:
        """
        More realistic value screen for S&P 500 stocks
        """
        print(f"Running realistic value screen on {len(symbols)} symbols...")
        value_stocks = []
        
        # Track statistics
        pe_ratios = []
        dividend_yields = []
        
        for i, symbol_data in enumerate(symbols, 1):
            symbol = symbol_data['symbol']
            print(f"Screening {symbol} ({i}/{len(symbols)})")
            
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                pe_ratio = info.get('trailingPE', None)
                dividend_yield = info.get('dividendYield', 0) or 0
                
                # Collect statistics
                if pe_ratio is not None and pe_ratio > 0:
                    pe_ratios.append(pe_ratio)
                if dividend_yield > 0:
                    dividend_yields.append(dividend_yield)
                
                # Very inclusive criteria - just need valid data
                has_valid_pe = pe_ratio is not None and pe_ratio > 0 and pe_ratio < 100  # Exclude extreme outliers
                has_some_dividend = dividend_yield >= 0.005  # 0.5% minimum (very low)
                
                print(f"  📊 {symbol}: P/E {pe_ratio}, Dividend {dividend_yield:.1%}")
                
                if has_valid_pe and has_some_dividend:
                    value_stock = {
                        'symbol': symbol,
                        'sector': symbol_data.get('sector', 'Unknown'),
                        'industry': symbol_data.get('industry', 'Unknown'),
                        'current_price': symbol_data.get('current_price', 0),
                        'market_cap': symbol_data.get('market_cap', 0),
                        'pe_ratio': float(pe_ratio),
                        'dividend_yield': float(dividend_yield),
                        'screen_date': datetime.now().strftime('%Y-%m-%d')
                    }
                    value_stocks.append(value_stock)
                    print(f"  ✓ {symbol}: PASSED realistic value screen")
                else:
                    reasons = []
                    if not has_valid_pe:
                        reasons.append(f"Invalid P/E: {pe_ratio}")
                    if not has_some_dividend:
                        reasons.append(f"Low dividend: {dividend_yield:.1%}")
                    print(f"  ✗ {symbol}: {', '.join(reasons)}")
                
            except Exception as e:
                print(f"  ✗ {symbol}: Error - {str(e)}")
                continue
            
            time.sleep(0.02)  # Faster rate limiting
        
        # Print statistics
        if pe_ratios:
            print(f"\nP/E Statistics: Mean={sum(pe_ratios)/len(pe_ratios):.1f}, Median={sorted(pe_ratios)[len(pe_ratios)//2]:.1f}")
        if dividend_yields:
            print(f"Dividend Statistics: Mean={sum(dividend_yields)/len(dividend_yields):.1%}, Median={sorted(dividend_yields)[len(dividend_yields)//2]:.1%}")
        
        print(f"\nRealistic value screening complete: {len(value_stocks)} stocks found")
        return value_stocks
    
    def save_results(self, results: List[Dict], screen_name: str, output_dir: str = '../data') -> str:
        """Save screening results to YAML file"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{screen_name}_{timestamp}.yaml"
        filepath = os.path.join(output_dir, filename)
        
        output_data = {
            'screen_name': screen_name,
            'screen_date': datetime.now().isoformat(),
            'total_results': len(results),
            'results': results
        }
        
        with open(filepath, 'w') as f:
            yaml.dump(output_data, f, default_flow_style=False, sort_keys=False)
        
        print(f"Results saved to {filepath}")
        return filepath

if __name__ == "__main__":
    # Test with a few known symbols
    test_symbols = [
        {'symbol': 'AAPL', 'sector': 'Technology', 'market_cap': 3000000000000},
        {'symbol': 'MSFT', 'sector': 'Technology', 'market_cap': 2800000000000}
    ]
    
    screener = StockScreener()
    # Test with relaxed criteria
    momentum_results = screener.relaxed_momentum_screen(test_symbols)
    screener.save_results(momentum_results, 'test_momentum')