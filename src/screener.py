import pandas as pd
import yaml
import os
from typing import List, Dict, Optional
from datetime import datetime
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
    
    def get_custom_symbols_only(self, symbols: List[Dict]) -> List[Dict]:
        """Return only the custom symbols from the validated universe (no data leakage)"""
        print(f"Extracting custom symbols from {len(symbols)} validated symbols...")
        
        custom_stocks = []
        custom_symbol_names = set(self.custom_symbols)
        
        for symbol_data in symbols:
            symbol = symbol_data['symbol']
            
            if symbol in custom_symbol_names:
                print(f"  ★ {symbol}: INCLUDED (custom symbol)")
                custom_stock = {
                    'symbol': symbol,
                    'sector': symbol_data.get('sector', 'Unknown'),
                    'industry': symbol_data.get('industry', 'Unknown'),
                    'current_price': symbol_data.get('current_price', 0),
                    'market_cap': symbol_data.get('market_cap', 0),
                    'screen_date': datetime.now().strftime('%Y-%m-%d'),
                    'inclusion_reason': 'custom_symbol'
                }
                custom_stocks.append(custom_stock)
        
        print(f"\nCustom symbol extraction complete: {len(custom_stocks)} symbols found")
        return custom_stocks
    

    

    
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
    # Test the custom symbol extraction
    test_symbols = [
        {'symbol': 'AAPL', 'sector': 'Technology', 'market_cap': 3000000000000},
        {'symbol': 'MSFT', 'sector': 'Technology', 'market_cap': 2800000000000},
        {'symbol': 'GOOGL', 'sector': 'Technology', 'market_cap': 1500000000000}
    ]
    
    screener = StockScreener()
    custom_stocks = screener.get_custom_symbols_only(test_symbols)
    
    if custom_stocks:
        screener.save_results(custom_stocks, 'custom_symbols_test')
