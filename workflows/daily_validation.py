"""Daily symbol validation workflow"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from symbol_validator import SymbolValidator
from data_analyzer import DataAnalyzer
from report_generator import ReportGenerator

def main():
    """Run daily validation workflow"""
    print("Starting daily symbol validation...")
    
    # Step 1: Validate symbols
    validator = SymbolValidator('../config/symbols_config.yaml')
    universe = validator.build_symbol_universe()
    
    # Step 2: Analyze data
    analyzer = DataAnalyzer(universe)
    analysis_results = analyzer.run_analysis()
    
    # Step 3: Generate reports
    reporter = ReportGenerator()
    reporter.generate_daily_report(universe, analysis_results)
    
    print("Daily validation complete!")

if __name__ == "__main__":
    main()