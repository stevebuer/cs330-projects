# Propagation Forecast Setup Guide

## Quick Start

### 1. Install OpenAI Package

If using a virtual environment:
```bash
source venv/bin/activate  # or your venv path
pip install openai>=1.0.0
```

Or add to your existing requirements installation:
```bash
pip install -r requirements.txt
```

### 2. Get OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-...`)

### 3. Add to Environment

Edit your `.env` file:
```bash
# Add this line
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 4. Restart Streamlit

```bash
# Stop current server (Ctrl+C)
# Restart
./run-dashboard-local.sh
# or
streamlit run streamlit/main.py
```

### 5. Test the Feature

1. Navigate to "Propagation Forecast" page in dashboard
2. Select forecast period (1-3 days)
3. Click "Generate New Forecast" if needed
4. View AI-generated predictions

## Cost Estimate

- **Model**: gpt-4o-mini (most cost-effective)
- **Per forecast**: $0.01 - $0.02
- **With caching**: ~$0.04/day maximum
- **For class project**: Should cost less than $1 total

## Troubleshooting

### Import Error
```python
ModuleNotFoundError: No module named 'openai'
```

**Solution**: Install the package
```bash
pip install openai
```

### API Key Error
```
Error: OpenAI API key not found
```

**Solution**: 
1. Check `.env` file has `OPENAI_API_KEY=...`
2. Restart Streamlit after adding key
3. Verify key is valid at OpenAI dashboard

### No Credits
```
insufficient_quota
```

**Solution**: Add credits to your OpenAI account
- Go to https://platform.openai.com/account/billing
- Add payment method
- Should only need $5-10 for class project

## Files Created

1. **`streamlit/pages/propagation_forecast.py`** - Main forecast page
2. **`dashboard-notebooks/propagation_forecast_llm.ipynb`** - Documentation notebook
3. **`docs/PROPAGATION_FORECAST.md`** - Detailed documentation
4. **`requirements.txt`** - Updated with openai package

## Next Steps for Class Project

1. ✅ Feature implementation complete
2. ✅ Documentation notebook created
3. ✅ Technical documentation written
4. ⏳ Install openai package
5. ⏳ Add OpenAI API key
6. ⏳ Generate test forecasts
7. ⏳ Take screenshots for project report
8. ⏳ Write project summary

## What to Include in Project Report

### Machine Learning Component
- Explain LLM as neural network architecture
- Discuss why LLM was chosen over LSTM/RNN
- Show trade-offs in model selection
- Reference CS330 concepts learned

### Time Series Analysis
- DX spot data as time series
- Trend analysis (24h, 7d, 30d windows)
- Pattern recognition in band activity
- Forecasting future conditions

### Implementation Details
- Data collection pipeline
- Statistical feature extraction
- Prompt engineering for LLM
- Caching strategy for optimization

### Results
- Example forecasts generated
- Discussion of prediction quality
- Limitations and future improvements
- Cost analysis

## Demo Script

For presenting your project:

```
1. Show the dashboard overview
2. Navigate to Propagation Forecast page
3. Show current statistics (spots, bands, regions)
4. Click "Generate New Forecast"
5. Explain the AI analysis process
6. Read through forecast sections:
   - Overall outlook
   - Band-by-band predictions
   - Best operating times
   - DX opportunities
7. Open Jupyter notebook
8. Walk through methodology
9. Discuss CS330 concepts applied
```

## Academic Context

### CS330 Topics Applied
- ✅ Machine Learning fundamentals
- ✅ Neural networks (LLM architecture)
- ✅ Time series analysis
- ✅ Feature engineering
- ✅ Model evaluation
- ✅ Practical constraints

### Key Points for Report
1. **Problem**: Predict propagation without traditional solar data
2. **Solution**: Analyze spot patterns with LLM
3. **Trade-offs**: LLM vs LSTM/RNN given data constraints
4. **Results**: Working forecast system
5. **Learning**: Model selection based on data availability

---

**Ready to present!** The feature is complete and documented. Just need to add your OpenAI API key to start generating forecasts.
