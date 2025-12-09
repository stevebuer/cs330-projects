# HF Propagation Forecast Feature

## Overview

The Propagation Forecast page provides AI-powered predictions of HF radio propagation conditions for the next 1-3 days based on recent DX cluster activity patterns.

## How It Works

### Data Collection
The system analyzes DX spot data from three time windows:
- **Last 24 hours**: Current activity baseline
- **Last 7 days**: Weekly trends
- **Last 30 days**: Monthly patterns

### Statistical Analysis
For each time period, we extract:
- **Band Distribution**: Activity levels on 10m, 12m, 15m, 17m, 20m, 30m, and 40m bands
- **Geographic Diversity**: Number of unique callsign prefixes (indicates DX potential)
- **Activity Trends**: Comparing recent activity to historical averages
- **Top DX Stations**: Most frequently spotted callsigns and regions

### AI-Powered Prediction
Statistics are fed to OpenAI's GPT-4 model with a carefully crafted prompt that:
1. Provides context about current propagation patterns
2. Requests specific predictions for each band
3. Asks for confidence levels and best operating times
4. Incorporates domain knowledge about HF propagation

### Caching Strategy
To optimize API usage and costs:
- Forecasts are cached for **12 hours**
- Same forecast shown to all users within cache period
- Manual refresh available via sidebar button
- Cache can hold different forecast lengths (1d, 2d, 3d) independently

## Setup

### 1. Install Dependencies

```bash
pip install openai>=1.0.0
```

Or if using the full requirements:

```bash
pip install -r requirements.txt
```

### 2. Configure OpenAI API Key

Add your OpenAI API key to `.env`:

```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

Get an API key from: https://platform.openai.com/api-keys

### 3. Cost Considerations

- Model used: `gpt-4o-mini` (cost-effective)
- Approximate cost: $0.01-0.02 per forecast generation
- With 12-hour caching: ~$0.04/day maximum
- Very affordable for personal/educational use

## Usage

### Via Streamlit Dashboard

1. Navigate to "Propagation Forecast" page
2. Select forecast period (1, 2, or 3 days) in sidebar
3. View current forecast or click "Generate New Forecast"
4. Read AI-generated predictions with band-by-band analysis

### Programmatic Usage

See the Jupyter notebook for detailed examples:
```
dashboard-notebooks/propagation_forecast_llm.ipynb
```

Basic usage:

```python
from propagation_forecast import collect_dx_statistics, generate_forecast_with_llm

# Collect statistics
stats = collect_dx_statistics()

# Generate 2-day forecast
forecast = generate_forecast_with_llm(stats, forecast_days=2)

print(forecast)
```

## Forecast Content

A typical forecast includes:

### 1. Overall Propagation Outlook
General assessment of expected conditions (Poor/Fair/Good/Excellent)

### 2. Band-by-Band Predictions
Specific forecasts for each amateur band:
- **10m (28 MHz)**: Long-distance DX potential, solar-dependent
- **12m (24 MHz)**: Mid-range propagation
- **15m (21 MHz)**: Reliable DX band during solar peaks
- **17m (18 MHz)**: Steady propagation
- **20m (14 MHz)**: Most reliable DX band
- **30m (10 MHz)**: Digital modes, night propagation
- **40m (7 MHz)**: Regional to continental

### 3. Best Operating Times
Recommended hours for optimal propagation (UTC and local)

### 4. DX Opportunities
Geographic regions expected to be reachable

### 5. Confidence Level
AI's confidence in the prediction (Low/Medium/High)

## Understanding the Predictions

### Key Indicators

**High Band Activity (10m, 12m, 15m)**
- Indicates good solar conditions
- Suggests excellent long-distance DX potential
- Typical during solar maximum

**Lower Band Only Activity (30m, 40m)**
- Suggests poor propagation conditions
- More regional/continental propagation
- Typical during solar minimum

**Increasing Activity Trend**
- Improving propagation conditions
- Solar flux likely increasing
- Good time for DX operations

**Geographic Diversity**
- More unique prefixes = better global propagation
- Concentrated regions = limited skip patterns

## Limitations

### Important Notes

1. **Activity-Based, Not Physics-Based**
   - Analyzes spot patterns, not actual solar data
   - Best used as a general guide, not scientific forecast

2. **Data Limitations**
   - Depends on DX cluster activity levels
   - Quiet periods may not indicate poor propagation
   - Active contesters can skew statistics

3. **Regional Variations**
   - Propagation varies by location
   - Forecast is general, not location-specific
   - Your mileage may vary

4. **Cache Duration**
   - 12-hour cache may miss rapid changes
   - Use refresh button for latest analysis

### For More Accurate Forecasts

Consult these authoritative sources:
- **NOAA Space Weather Prediction Center**: https://www.swpc.noaa.gov/
- **Solar Flux Index**: Daily solar flux measurements
- **K-Index**: Geomagnetic activity levels
- **VOACAP**: Voice of America Coverage Analysis Program
- **Sporadic-E Predictions**: For VHF/UHF enthusiasts

## Technical Details

### Model Architecture
- **LLM**: OpenAI GPT-4-mini
- **Context Window**: ~2000 tokens for forecast generation
- **Temperature**: 0.7 (balanced creativity and consistency)
- **System Prompt**: Expert propagation analyst persona

### Why LLM Instead of Traditional ML?

| Approach | Pros | Cons | Suitable? |
|----------|------|------|-----------|
| **LSTM/RNN** | Good for time series | Needs lots of labeled data | ❌ |
| **Random Forest** | Handles features well | Needs training data | ❌ |
| **LLM** | Works immediately, domain knowledge | API cost | ✅ |

For this project:
- Limited historical data with labeled outcomes
- Complex propagation patterns
- Need for human-readable output
- Time constraints (class project)

### Performance Metrics

**Response Time**:
- Data collection: 2-5 seconds
- LLM inference: 10-20 seconds
- Total: ~15-25 seconds per forecast
- Cached requests: <1 second

**Accuracy**:
- Not scientifically validated
- Subjective quality assessment
- Feels predictive and informative
- Suitable for educational/entertainment purposes

## Development

### Testing

Run the notebook to test components:
```bash
jupyter notebook dashboard-notebooks/propagation_forecast_llm.ipynb
```

### Debugging

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

View cache status in Streamlit sidebar (shows logged-in user and timezone).

### Extending

To enhance the forecast:

1. **Add Solar Data**: Incorporate actual solar flux and K-index
2. **Historical Training**: Build LSTM on historical spot + solar data
3. **Ensemble Model**: Combine LLM with physics-based models
4. **Confidence Intervals**: Multiple LLM runs for uncertainty
5. **Location-Specific**: Use user's grid square for targeted predictions

## CS330 Project Context

This implementation was created for CS330 Machine Learning course final project.

### Learning Objectives Met
✅ Applied ML to real-world problem  
✅ Worked with time series data  
✅ Implemented prediction system  
✅ Considered model selection trade-offs  
✅ Evaluated practical constraints  
✅ Documented methodology  

### Why This Approach Works

**Practical**: Delivers working predictions immediately  
**Educational**: Demonstrates ML concepts (LLM = large neural network)  
**Modern**: Uses state-of-the-art technology  
**Realistic**: Acknowledges data limitations  
**Extensible**: Can be enhanced with traditional ML later  

## Troubleshooting

### "OpenAI API key not found"
- Check `.env` file has `OPENAI_API_KEY` set
- Verify API key is valid at https://platform.openai.com/
- Restart Streamlit server after adding key

### "API request failed"
- Check internet connectivity
- Verify OpenAI API status: https://status.openai.com/
- Check API usage limits and billing

### "No spots found"
- Verify DX cluster API is running
- Check API_BASE_URL in `.env`
- Try different time windows

### Forecast seems outdated
- Click "Generate New Forecast" in sidebar
- Cache is valid for 12 hours by design
- Check timestamp shown below forecast

## License

Part of CS330 class project. For educational use.

## Credits

- **OpenAI GPT-4**: Forecast generation
- **DX Cluster Network**: Spot data
- **Streamlit**: Web interface
- **CS330 Course**: Machine learning concepts

---

**Note**: This is an experimental educational project. For critical propagation planning, use professional forecasting services and actual solar data.
