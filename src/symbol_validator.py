import yfinance as yf
import pandas as pd
import yaml
from typing import List, Dict, Set
import time
from datetime import datetime, timedelta
import os

class SymbolValidator:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
    
    def get_sp500_symbols(self) -> List[str]:
        """Fetch S&P 500 symbols from Wikipedia"""
        try:
            tables = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
            sp500_table = tables[0]
            return sp500_table['Symbol'].tolist()
        except Exception as e:
            print(f"Error fetching S&P 500 symbols: {e}")
            return []
    
    def validate_symbol(self, symbol: str) -> Dict:
        """Validate a single symbol against criteria"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get basic info
            try:
                info = ticker.info
            except:
                info = {}
            
            # Get historical data - use a longer period to ensure we have enough data
            # Using period instead of start/end dates for more reliable data fetching
            hist = ticker.history(period="2y")  # Get 2 years of data
            
            if hist.empty:
                return {'symbol': symbol, 'valid': False, 'reason': 'No historical data available'}
            
            # Validation checks
            validation_result = {
                'symbol': symbol,
                'valid': True,
                'reasons': [],
                'market_cap': info.get('marketCap', 0),
                'avg_volume': float(hist['Volume'].mean()) if len(hist) > 0 else 0,
                'current_price': float(hist['Close'].iloc[-1]) if len(hist) > 0 else 0,
                'data_points': len(hist),
                'data_start': hist.index[0].strftime('%Y-%m-%d') if len(hist) > 0 else None,
                'data_end': hist.index[-1].strftime('%Y-%m-%d') if len(hist) > 0 else None,
                # Add sector and industry information
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'country': info.get('country', 'Unknown'),
                'exchange': info.get('exchange', 'Unknown'),
                'currency': info.get('currency', 'USD')
            }
            
            # Market cap check (if available)
            min_market_cap = self.config['validation']['min_market_cap']
            if validation_result['market_cap'] > 0 and validation_result['market_cap'] < min_market_cap:
                validation_result['valid'] = False
                validation_result['reasons'].append(f"Market cap too low: ${validation_result['market_cap']:,}")
            
            # Volume check
            min_volume = self.config['validation']['min_avg_volume']
            if validation_result['avg_volume'] < min_volume:
                validation_result['valid'] = False
                validation_result['reasons'].append(f"Average volume too low: {validation_result['avg_volume']:,.0f}")
            
            # Price checks
            min_price = self.config['validation']['min_price_threshold']
            if min_price and validation_result['current_price'] < min_price:
                validation_result['valid'] = False
                validation_result['reasons'].append(f"Price too low: ${validation_result['current_price']:.2f}")
            
            # Data history check - require at least 200 trading days (about 8-9 months)
            min_data_points = 200
            if validation_result['data_points'] < min_data_points:
                validation_result['valid'] = False
                validation_result['reasons'].append(f"Insufficient data history: {validation_result['data_points']} days")
            
            # Check for required fields in the data
            required_fields = self.config['data_requirements']['required_fields']
            missing_fields = [field for field in required_fields if field not in hist.columns]
            if missing_fields:
                validation_result['valid'] = False
                validation_result['reasons'].append(f"Missing required data fields: {missing_fields}")
            
            return validation_result
            
        except Exception as e:
            return {
                'symbol': symbol, 
                'valid': False, 
                'reason': f'Error validating {symbol}: {str(e)}',
                'data_points': 0
            }
    
    def build_symbol_universe(self) -> Dict:
        """Build and validate complete symbol universe"""
        all_symbols = set()
        
        # Add S&P 500 if enabled
        if self.config['symbol_sources']['sp500']:
            sp500_symbols = self.get_sp500_symbols()
            all_symbols.update(sp500_symbols)
            print(f"Added {len(sp500_symbols)} S&P 500 symbols")
        
        # Add custom symbols
        custom_symbols = self.config['symbol_sources']['custom_symbols']
        all_symbols.update(custom_symbols)
        print(f"Added {len(custom_symbols)} custom symbols")
        
        print(f"Total symbols to validate: {len(all_symbols)}")
        
        # Validate each symbol
        valid_symbols = []
        invalid_symbols = []
        
        for i, symbol in enumerate(sorted(all_symbols), 1):
            print(f"Validating {symbol} ({i}/{len(all_symbols)})")
            
            result = self.validate_symbol(symbol)
            
            if result['valid']:
                valid_symbols.append(result)
                sector = result.get('sector', 'Unknown')
                print(f"  ✓ Valid - {result['data_points']} days, {sector}")
            else:
                invalid_symbols.append(result)
                # Handle both single reason and multiple reasons
                if 'reasons' in result and result['reasons']:
                    reasons_str = '; '.join(result['reasons'])
                elif 'reason' in result:
                    reasons_str = result['reason']
                else:
                    reasons_str = 'Unknown error'
                print(f"  ✗ Invalid - {reasons_str}")
            
            # Rate limiting - be nice to yfinance
            time.sleep(0.1)
        
        return {
            'valid_symbols': valid_symbols,
            'invalid_symbols': invalid_symbols,
            'summary': {
                'total_tested': len(all_symbols),
                'valid_count': len(valid_symbols),
                'invalid_count': len(invalid_symbols),
                'validation_date': datetime.now().isoformat()
            }
        }

def main():
    validator = SymbolValidator('../config/symbols_config.yaml')
    universe = validator.build_symbol_universe()
    
    print(f"\nValidation Summary:")
    print(f"Valid symbols: {universe['summary']['valid_count']}")
    print(f"Invalid symbols: {universe['summary']['invalid_count']}")
    
    # Show some examples of valid symbols with sector info
    if universe['valid_symbols']:
        print(f"\nExample valid symbols:")
        for symbol in universe['valid_symbols'][:5]:
            sector = symbol.get('sector', 'Unknown')
            print(f"  {symbol['symbol']}: {symbol['data_points']} days, ${symbol['current_price']:.2f}, {sector}")
    
    # Show invalid symbols if any
    if universe['invalid_symbols']:
        print(f"\nInvalid symbols:")
        for symbol in universe['invalid_symbols']:
            if 'reasons' in symbol and symbol['reasons']:
                reasons_str = '; '.join(symbol['reasons'])
            elif 'reason' in symbol:
                reasons_str = symbol['reason']
            else:
                reasons_str = 'Unknown error'
            data_points = symbol.get('data_points', 0)
            print(f"  {symbol['symbol']}: {reasons_str} ({data_points} data points)")
    
    # Show sector distribution
    if universe['valid_symbols']:
        sector_counts = {}
        for symbol in universe['valid_symbols']:
            sector = symbol.get('sector', 'Unknown')
            sector_counts[sector] = sector_counts.get(sector, 0) + 1
        
        print(f"\nSector Distribution:")
        for sector, count in sorted(sector_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {sector}: {count} stocks")
    
    # Create data directory if it doesn't exist
    data_dir = '../data'
    os.makedirs(data_dir, exist_ok=True)
    
    # Save results with cleaner format (convert numpy types to Python native types)
    output_file = os.path.join(data_dir, 'validated_symbols.yaml')
    
    # Clean the data before saving to avoid numpy serialization issues
    cleaned_universe = {
        'valid_symbols': [
            {
                'symbol': s['symbol'],
                'market_cap': int(s['market_cap']) if s['market_cap'] > 0 else 0,
                'avg_volume': float(s['avg_volume']),
                'current_price': float(s['current_price']),
                'data_points': int(s['data_points']),
                'data_start': s.get('data_start'),
                'data_end': s.get('data_end'),
                'sector': s.get('sector', 'Unknown'),
                'industry': s.get('industry', 'Unknown'),
                'country': s.get('country', 'Unknown'),
                'exchange': s.get('exchange', 'Unknown'),
                'currency': s.get('currency', 'USD')
            }
            for s in universe['valid_symbols']
        ],
        'invalid_symbols': [
            {
                'symbol': s['symbol'],
                'reasons': s.get('reasons') if s.get('reasons') else [s.get('reason', 'Unknown error')],
                'data_points': int(s.get('data_points', 0))
            }
            for s in universe['invalid_symbols']
        ],
        'summary': universe['summary']
    }
    
    with open(output_file, 'w') as f:
        yaml.dump(cleaned_universe, f, default_flow_style=False, sort_keys=False)
    
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    main()