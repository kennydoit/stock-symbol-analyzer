# Import necessary libraries
import yfinance as yf
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to check availability of stock symbols
def check_symbol_availability(symbols):
    available_symbols = []
    unavailable_symbols = []
    
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            # Fetching the ticker info
            info = ticker.info
            
            # Check if the symbol is valid by checking if 'symbol' is in the info
            if 'symbol' in info:
                available_symbols.append(symbol)
                logger.info(f"Symbol available: {symbol}")
            else:
                unavailable_symbols.append(symbol)
                logger.warning(f"Symbol unavailable: {symbol}")
        except Exception as e:
            unavailable_symbols.append(symbol)
            logger.error(f"Error checking symbol {symbol}: {e}")
    
    return available_symbols, unavailable_symbols

# Sample list of stock symbols to check
sample_symbols = ['AAPL', 'GOOGL', 'MSFT', 'INVALID', 'TSLA']

# Check availability
available, unavailable = check_symbol_availability(sample_symbols)

# Display results
print(f"Available Symbols: {available}")
print(f"Unavailable Symbols: {unavailable}")

# Optionally, save results to a CSV file
results_df = pd.DataFrame({
    'Available Symbols': pd.Series(available),
    'Unavailable Symbols': pd.Series(unavailable)
})

results_df.to_csv('symbol_availability_results.csv', index=False)
print("Results saved to symbol_availability_results.csv")