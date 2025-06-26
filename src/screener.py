import yfinance as yf
import pandas as pd
import yaml
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import time

from pathlib import Path

class StockScreener:
    def __init__(self, config_path: str = None):
        if config_path is None:
            # Always resolve relative to project root
            config_path = str(Path(__file__).resolve().parent.parent / "config.yaml")
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self.custom_symbols = self.config['symbol_sources']['custom_symbols']
        self.results = {}
    
    def get_custom_symbol_data(self, validated_symbols: List[Dict]) -> List[Dict]:
        """Get data for custom symbols from the validated universe"""
        custom_data = []
        validated_symbol_map = {s['symbol']: s for s in validated_symbols}
        
        for symbol in self.custom_symbols:
            if symbol in validated_symbol_map:
                custom_data.append(validated_symbol_map[symbol])
            else:
                print(f"Warning: Custom symbol {symbol} not found in validated universe")
        
        return custom_data
    
    def momentum_screen(self, symbols: List[Dict], min_return_3m: float = 0.15, min_volume_ratio: float = 1.5) -> List[Dict]:
        """Screen for momentum stocks + force-include custom symbols"""
        print(f"Screening {len(symbols)} symbols for momentum...")
        
        # Run normal momentum screening
        momentum_stocks = []
        custom_symbol_names = set(self.custom_symbols)
        
        for i, symbol_data in enumerate(symbols, 1):
            symbol = symbol_data['symbol']
            print(f"Screening {symbol} ({i}/{len(symbols)})")
            
            # Force include custom symbols
            if symbol in custom_symbol_names:
                print(f"  ★ {symbol}: FORCE INCLUDED (custom symbol)")
                momentum_stock = {
                    'symbol': symbol,
                    'sector': symbol_data.get('sector', 'Unknown'),
                    'industry': symbol_data.get('industry', 'Unknown'),
                    'current_price': symbol_data.get('current_price', 0),
                    'market_cap': symbol_data.get('market_cap', 0),
                    'screen_date': datetime.now().strftime('%Y-%m-%d'),
                    'inclusion_reason': 'custom_symbol'
                }
                momentum_stocks.append(momentum_stock)
                continue
            
            # Regular momentum screening logic for non-custom symbols
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="6mo")
                
                if len(hist) < 60:
                    print(f"  ✗ {symbol}: Insufficient data for momentum analysis")
                    continue
                
                # Calculate returns and volume ratios (existing logic)
                if len(hist) >= 63:
                    current_price = hist['Close'].iloc[-1]
                    three_month_price = hist['Close'].iloc[-63]
                    three_month_return = (current_price - three_month_price) / three_month_price
                else:
                    current_price = hist['Close'].iloc[-1]
                    start_price = hist['Close'].iloc[0]
                    three_month_return = (current_price - start_price) / start_price
                
                if len(hist) >= 20:
                    recent_volume = hist['Volume'].tail(5).mean()
                    longer_term_volume = hist['Volume'].iloc[:-10].mean()
                    volume_ratio = recent_volume / longer_term_volume if longer_term_volume > 0 else 1.0
                else:
                    volume_ratio = 1.0
                
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
                        'screen_date': datetime.now().strftime('%Y-%m-%d'),
                        'inclusion_reason': 'passed_momentum_screen'
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
            
            time.sleep(0.05)
        
        # Count custom vs screened
        custom_count = sum(1 for s in momentum_stocks if s.get('inclusion_reason') == 'custom_symbol')
        screened_count = len(momentum_stocks) - custom_count
        
        print(f"\nMomentum screening complete:")
        print(f"  Passed screening: {screened_count} stocks")
        print(f"  Force-included custom: {custom_count} stocks")
        print(f"  Total: {len(momentum_stocks)} stocks")
        
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
        """Realistic value screen + force-include custom symbols"""
        print(f"Running realistic value screen on {len(symbols)} symbols...")
        value_stocks = []
        custom_symbol_names = set(self.custom_symbols)
        
        for i, symbol_data in enumerate(symbols, 1):
            symbol = symbol_data['symbol']
            print(f"Screening {symbol} ({i}/{len(symbols)})")
            
            # Force include custom symbols
            if symbol in custom_symbol_names:
                print(f"  ★ {symbol}: FORCE INCLUDED (custom symbol)")
                value_stock = {
                    'symbol': symbol,
                    'sector': symbol_data.get('sector', 'Unknown'),
                    'industry': symbol_data.get('industry', 'Unknown'),
                    'current_price': symbol_data.get('current_price', 0),
                    'market_cap': symbol_data.get('market_cap', 0),
                    'screen_date': datetime.now().strftime('%Y-%m-%d'),
                    'inclusion_reason': 'custom_symbol'
                }
                value_stocks.append(value_stock)
                continue
            
            # Regular value screening logic (existing code)
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                pe_ratio = info.get('trailingPE', None)
                dividend_yield = info.get('dividendYield', 0) or 0
                
                has_valid_pe = pe_ratio is not None and pe_ratio > 0 and pe_ratio < 100
                has_some_dividend = dividend_yield >= 0.005
                
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
                        'screen_date': datetime.now().strftime('%Y-%m-%d'),
                        'inclusion_reason': 'passed_value_screen'
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
            
            time.sleep(0.02)
        
        # Count custom vs screened
        custom_count = sum(1 for s in value_stocks if s.get('inclusion_reason') == 'custom_symbol')
        screened_count = len(value_stocks) - custom_count
        
        print(f"\nRealistic value screening complete:")
        print(f"  Passed screening: {screened_count} stocks")
        print(f"  Force-included custom: {custom_count} stocks") 
        print(f"  Total: {len(value_stocks)} stocks")
        
        return value_stocks
    
    def save_results(self, results: List[Dict], screen_name: str, output_dir: str = None) -> str:
        """Save screening results to YAML file"""
        # Always resolve data directory relative to this script
        script_dir = Path(__file__).resolve().parent
        data_dir = script_dir.parent / "data"
        data_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{screen_name}_{timestamp}.yaml"
        filepath = data_dir / filename

        output_data = {
            'screen_name': screen_name,
            'screen_date': datetime.now().isoformat(),
            'total_results': len(results),
            'results': results
        }

        with open(filepath, 'w') as f:
            yaml.dump(output_data, f, default_flow_style=False, sort_keys=False)

        print(f"Results saved to {filepath}")
        return str(filepath)

if __name__ == "__main__":
    # Test with a few known symbols
    test_symbols = [
        {'symbol': 'AAPL', 'sector': 'Technology', 'market_cap': 3000000000000},
        {'symbol': 'MSFT', 'sector': 'Technology', 'market_cap': 2800000000000}
    ]
