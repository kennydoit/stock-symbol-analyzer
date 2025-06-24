import yaml
import os
from datetime import datetime
from typing import List, Dict

from pathlib import Path

# Get the directory of the current script
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"

class SymbolListGenerator:
    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = data_dir
    
    def load_screening_results(self, filename: str) -> Dict:
        """Load screening results from YAML file"""
        filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return {}
        
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)
    
    def find_latest_screen_file(self, screen_type: str) -> str:
        """Find the most recent screening file for a given type"""
        files = os.listdir(self.data_dir)
        matching_files = [f for f in files if f.startswith(screen_type) and f.endswith('.yaml')]
        
        if not matching_files:
            return None
        
        # Sort by filename (which includes timestamp) and get the latest
        matching_files.sort(reverse=True)
        return matching_files[0]
    
    def extract_symbol_list(self, screening_data: Dict) -> List[str]:
        """Extract just the symbol names from screening results"""
        if 'results' not in screening_data:
            return []
        
        return [result['symbol'] for result in screening_data['results']]
    
    def create_detailed_symbol_list(self, screening_data: Dict, screen_name: str) -> Dict:
        """Create a detailed symbol list with key metrics"""
        if 'results' not in screening_data:
            return {}
        
        symbol_list = {
            'screen_name': screen_name,
            'created_date': datetime.now().isoformat(),
            'total_symbols': len(screening_data['results']),
            'symbols': []
        }
        
        for result in screening_data['results']:
            symbol_info = {
                'symbol': result['symbol'],
                'sector': result.get('sector', 'Unknown'),
                'market_cap': result.get('market_cap', 0),
                'current_price': result.get('current_price', 0)
            }
            
            # Add screen-specific metrics
            if 'three_month_return' in result:
                symbol_info['three_month_return'] = result['three_month_return']
                symbol_info['volume_ratio'] = result.get('volume_ratio', 0)
            
            if 'pe_ratio' in result:
                symbol_info['pe_ratio'] = result['pe_ratio']
                symbol_info['dividend_yield'] = result.get('dividend_yield', 0)
            
            symbol_list['symbols'].append(symbol_info)
        
        return symbol_list
    
    def generate_all_symbol_lists(self):
        """Generate symbol lists for all screening types"""
        screen_types = {
            'momentum_screen': 'Momentum Stocks',
            'realistic_value_screen': 'Realistic Value Stocks', 
            'traditional_value_screen': 'Traditional Value Stocks'
        }
        
        results = {}
        
        for screen_type, display_name in screen_types.items():
            print(f"\nProcessing {display_name}...")
            
            # Find latest file for this screen type
            latest_file = self.find_latest_screen_file(screen_type)
            
            if not latest_file:
                print(f"  No files found for {screen_type}")
                continue
            
            print(f"  Using file: {latest_file}")
            
            # Load the data
            screening_data = self.load_screening_results(latest_file)
            
            if not screening_data:
                print(f"  Failed to load data from {latest_file}")
                continue
            
            # Extract simple symbol list
            symbols = self.extract_symbol_list(screening_data)
            print(f"  Found {len(symbols)} symbols")
            
            # Create detailed list
            detailed_list = self.create_detailed_symbol_list(screening_data, display_name)
            
            # Save simple symbol list
            simple_filename = f"{screen_type}_symbols.txt"
            simple_filepath = os.path.join(self.data_dir, simple_filename)
            with open(simple_filepath, 'w') as f:
                f.write(f"# {display_name} - {len(symbols)} symbols\n")
                f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                for symbol in symbols:
                    f.write(f"{symbol}\n")
            
            print(f"  Saved simple list: {simple_filename}")
            
            # Save detailed symbol list
            detailed_filename = f"{screen_type}_detailed.yaml"
            detailed_filepath = os.path.join(self.data_dir, detailed_filename)
            with open(detailed_filepath, 'w') as f:
                yaml.dump(detailed_list, f, default_flow_style=False, sort_keys=False)
            
            print(f"  Saved detailed list: {detailed_filename}")
            
            results[screen_type] = {
                'symbols': symbols,
                'count': len(symbols),
                'detailed': detailed_list
            }
        
        return results
    
    def create_combined_summary(self, results: Dict):
        """Create a summary showing overlap between different screens"""
        if len(results) < 2:
            return
        
        print(f"\n" + "="*50)
        print("SCREENING SUMMARY")
        print("="*50)
        
        # Get symbol sets
        momentum_symbols = set(results.get('momentum_screen', {}).get('symbols', []))
        realistic_value_symbols = set(results.get('realistic_value_screen', {}).get('symbols', []))
        traditional_value_symbols = set(results.get('traditional_value_screen', {}).get('symbols', []))
        
        print(f"Momentum stocks: {len(momentum_symbols)}")
        print(f"Realistic value stocks: {len(realistic_value_symbols)}")
        print(f"Traditional value stocks: {len(traditional_value_symbols)}")
        
        # Find overlaps
        if momentum_symbols and realistic_value_symbols:
            momentum_value_overlap = momentum_symbols & realistic_value_symbols
            print(f"\nMomentum + Realistic Value overlap: {len(momentum_value_overlap)}")
            if momentum_value_overlap:
                print(f"  Overlapping symbols: {sorted(list(momentum_value_overlap))[:10]}...")
        
        if realistic_value_symbols and traditional_value_symbols:
            value_overlap = realistic_value_symbols & traditional_value_symbols
            print(f"Realistic + Traditional Value overlap: {len(value_overlap)}")
        
        if momentum_symbols and traditional_value_symbols:
            momentum_traditional_overlap = momentum_symbols & traditional_value_symbols
            print(f"Momentum + Traditional Value overlap: {len(momentum_traditional_overlap)}")
        
        # All three overlap
        if momentum_symbols and realistic_value_symbols and traditional_value_symbols:
            all_three_overlap = momentum_symbols & realistic_value_symbols & traditional_value_symbols
            print(f"\nAll three strategies overlap: {len(all_three_overlap)}")
            if all_three_overlap:
                print(f"  High-conviction symbols: {sorted(list(all_three_overlap))}")

def main():
    generator = SymbolListGenerator()
    results = generator.generate_all_symbol_lists()
    generator.create_combined_summary(results)
    
    print(f"\n" + "="*50)
    print("FILES GENERATED:")
    print("="*50)
    print("Simple symbol lists (for easy import):")
    print("  - momentum_screen_symbols.txt")
    print("  - realistic_value_screen_symbols.txt") 
    print("  - traditional_value_screen_symbols.txt")
    print("\nDetailed lists with metrics:")
    print("  - momentum_screen_detailed.yaml")
    print("  - realistic_value_screen_detailed.yaml")
    print("  - traditional_value_screen_detailed.yaml")

if __name__ == "__main__":
    main()