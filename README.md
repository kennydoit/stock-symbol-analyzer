# Stock Symbol Screener - Clean Workflow

A stock symbol validation and database preparation system designed to avoid data leakage and minimize API calls for robust financial analysis.

## 🎯 Overview

This system provides a clean, bias-free workflow for preparing stock symbol universes:

1. **Symbol Validation**: Validates S&P 500 stocks against basic quality criteria
2. **Database Storage**: Stores validated symbols in a structured database
3. **Custom Symbol Extraction**: Extracts predefined custom symbols without market data screening

**Key Features:**
- ✅ No forward-looking bias or data leakage
- ✅ Minimal API requests (only for validation)
- ✅ Reproducible symbol universes
- ✅ Database-ready output

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Create virtual environment with uv
uv sync
# Activate based on your shell
.venv\Scripts\activate  # Windows PowerShell
# .venv\bin\activate    # Linux/Mac
```

### 2. Run Clean Workflow

```bash
# Step 1: Validate symbols (makes API calls for validation only)
python scripts\symbol_validator.py

# Step 2: Write validated symbols to database  
python scripts\write_symbols_to_db.py

# Step 3: Extract custom symbols (no API calls, no data leakage)
python scripts\clean_workflow.py
```

## 📋 What Changed

### Removed (Data Leakage Sources)
- ❌ `stock_screener.py` - Used recent returns and volume ratios
- ❌ Momentum screening methods - Forward-looking price data
- ❌ Value screening methods - Current P/E and dividend data
- ❌ Multiple API calls for real-time market data

### Kept (Clean Components)  
- ✅ Symbol validation with basic quality checks
- ✅ Database writing functionality
- ✅ Custom symbol list management
- ✅ Configuration-based symbol selection
   ```

2. **Validate Symbol Universe**
   ```bash
python .\scripts\symbol_validator.py
   ```
   
   **Output**: `data/validated_symbols.yaml` with ~500 validated S&P 500 symbols

3. **Run Screening Strategies**
   ```bash
python .\scripts\stock_screener.py
   ```
   
   **Output**: Three screening result files in `data/`:
   - `momentum_screen_YYYYMMDD_HHMMSS.yaml`
   - `realistic_value_screen_YYYYMMDD_HHMMSS.yaml` 
   - `traditional_value_screen_YYYYMMDD_HHMMSS.yaml`

4. **Generate Clean Symbol Lists**
   ```bash
   cd scripts
   python symbol_list_generator.py
   ```
   
   **Output**: Ready-to-use symbol lists in `data/`:
   - `momentum_screen_symbols.txt` (simple list)
   - `realistic_value_screen_symbols.txt` 
   - `traditional_value_screen_symbols.txt`
   - `*_detailed.yaml` (with full metrics)

## 🎛️ Configuration Options

### Screening Criteria

Edit `src/screener.py` or use the workflow parameters:

**Momentum Screen:**
```python
momentum_stocks = screener.momentum_screen(
    symbols,
    min_return_3m=0.05,      # 5% minimum 3-month return
    min_volume_ratio=0.8     # Recent volume vs historical average
)
```

**Value Screens:**
```python
# Realistic value (inclusive)
realistic_stocks = screener.realistic_value_screen(symbols)
# P/E < 100, dividend >= 0.5%

# Traditional value (strict)  
value_stocks = screener.value_screen(
    symbols,
    max_pe=25,               # P/E ratio <= 25
    min_dividend_yield=0.02  # Dividend yield >= 2%
)
```

### Custom Symbols

Add symbols that bypass all screening criteria:

```yaml
# config/symbols_config.yaml
symbol_sources:
  custom_symbols:
    - "AAPL"  # Always included regardless of screening results
    - "MSFT"
    - "GOOGL"
```

## 📊 Expected Results

| Strategy | Typical Count | Description |
|----------|---------------|-------------|
| **Momentum** | ~90 stocks | High 3-month returns + volume activity |
| **Realistic Value** | ~390 stocks | Broad value universe (P/E < 100) |
| **Traditional Value** | ~70 stocks | Classic value (P/E ≤ 25, dividend ≥ 2%) |

## 🔄 Regular Updates

### Weekly/Monthly Refresh

```bash
# Update symbol validation
validate.bat

# Re-run screening with latest data
screen.bat

# Generate fresh symbol lists
generate_lists.bat
```

### Custom Analysis

```bash
# Analyze screening effectiveness
cd src
python screener_diagnostics.py

# Test different criteria
python screener.py  # Modify parameters in __main__
```

## 📁 Output Files Explained

### Core Data Files
- `validated_symbols.yaml` - Complete S&P 500 validation results
- `momentum_screen_TIMESTAMP.yaml` - Full momentum screening results
- `realistic_value_screen_TIMESTAMP.yaml` - Realistic value results
- `traditional_value_screen_TIMESTAMP.yaml` - Strict value results

### Ready-to-Use Lists
- `momentum_screen_symbols.txt` - Simple symbol list for momentum strategy
- `realistic_value_screen_symbols.txt` - Simple symbol list for value strategy
- `*_detailed.yaml` - Symbol lists with complete metrics (P/E, returns, etc.)

### Example Symbol List Format
```
# Momentum Stocks - 89 symbols
# Generated: 2025-06-07 10:30:15

ABNB
AAPL
ADBE
...
```

## 🔗 Integration with ML Systems

### Import Symbols into Database
```python
# Load validated symbols
with open('data/realistic_value_screen_symbols.txt', 'r') as f:
    symbols = [line.strip() for line in f 
               if line.strip() and not line.startswith('#')]

# Use in your ML pipeline
for symbol in symbols:
    # Fetch data, train models, etc.
```

### Load Detailed Metrics
```python
import yaml

with open('data/realistic_value_screen_detailed.yaml', 'r') as f:
    data = yaml.safe_load(f)

symbols_with_metrics = data['symbols']
# Each symbol includes: sector, market_cap, pe_ratio, dividend_yield, etc.
```

## 🛠️ Troubleshooting

### Common Issues

**1. "No module named 'screener'"**
```bash
# Make sure you're in the right directory
cd workflows
python screening_workflow.py
```

**2. "Validated symbols file not found"**
```bash
# Run symbol validation first
cd src  
python symbol_validator.py
```

**3. "Rate limiting errors"**
```python
# Increase sleep time in screener.py
time.sleep(0.1)  # Increase from 0.05
```

**4. "Few symbols passing screens"**
```bash
# Check criteria effectiveness
cd src
python screener_diagnostics.py
```

### Performance Tips

- **First run**: Takes ~30-45 minutes for full S&P 500 validation
- **Subsequent runs**: Use existing `validated_symbols.yaml` 
- **Rate limiting**: Built-in delays prevent API throttling
- **Parallel processing**: Not recommended due to API limits

## 📈 Customization Examples

### Create Custom Screen
```python
# Add to screener.py
def growth_screen(self, symbols, min_revenue_growth=0.15):
    """Screen for high revenue growth stocks"""
    # Implementation here
```

### Modify Validation Criteria
```yaml
# config/symbols_config.yaml
validation:
  min_market_cap: 5000000000    # $5B minimum
  min_avg_volume: 500000        # Higher volume requirement
  min_price_threshold: 10.0     # $10 minimum price
```

### Sector-Specific Analysis
```python
# Filter by sector
tech_symbols = [s for s in symbols if s.get('sector') == 'Technology']
screener.momentum_screen(tech_symbols)
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🔗 Related Projects

- [stock-prediction-ml](https://github.com/kennydoit/stock-prediction-ml) - ML models using these symbols
- Integration examples and advanced workflows

---

**Questions?** Open an issue or contact the maintainer.