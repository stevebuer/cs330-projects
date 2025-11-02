# Simple RNN Model for DX Band Openness Prediction

This directory contains a basic Recurrent Neural Network (RNN) implementation for learning purposes and performance comparison with the LSTM model in the `lstm-model/` directory.

## Overview

The Simple RNN model provides a simpler, more interpretable alternative to LSTM for sequence prediction tasks. This is useful for:
- Learning how RNNs work compared to LSTMs
- Quick experimentation on smaller datasets
- Understanding the differences in model complexity and performance
- Educational purposes

## Key Differences: RNN vs LSTM

| Aspect | Simple RNN | LSTM |
|--------|-----------|------|
| **Architecture** | Basic cells with hidden state | Memory cells with gates |
| **Parameters** | Fewer (~3x fewer) | More (due to gate mechanisms) |
| **Vanishing Gradient** | Prone to this problem | Resistant (by design) |
| **Training Speed** | Faster | Slower |
| **Long-term Dependencies** | Weaker | Stronger |
| **Complexity** | Simpler to understand | More complex |

## Files

- `rnn_train_example.py` - Main training script
- `example_rnn_dx_spot_data.csv` - Sample training data
- `rnn_model.h5` - Saved trained model (generated after first run)

## Usage

### Installation

Ensure you have the required packages:
```bash
pip install tensorflow scikit-learn pandas numpy
```

### Training the Model

```bash
python rnn_train_example.py
```

This will:
1. Load the example data
2. Create sequences of length 3 days
3. Scale the features
4. Train a SimpleRNN model for 30 epochs
5. Evaluate on test data
6. Display predictions and accuracy
7. Save the trained model as `rnn_model.h5`

### Expected Output

```
✓ Loaded data: 15 records
✓ Using features: ['total_spots', 'unique_dx_stations', ...]
✓ Created 12 sequences of length 3
✓ Train set: 9 samples, Test set: 3 samples
✓ Features scaled

============================================================
Building Simple RNN Model
============================================================
Input shape: (batch_size, 3, 7)
RNN units: 32 (compared to LSTM: typically more parameters)
Output layer: 1 neuron with sigmoid (binary classification)

Model summary:
_________________________________________________________________
 Layer (type)                Output Shape              Param #   
_________________________________________________________________
 simple_rnn (SimpleRNN)      (None, 32)                1312      
 dense (Dense)               (None, 16)                528       
 dense_1 (Dense)             (None, 1)                 17        
_________________________________________________________________
Total params: 1,857
Trainable params: 1,857
Non-trainable params: 0

============================================================
Training for 30 epochs with batch size 2
============================================================
Epoch 1/30
5/5 [==============================] 0s 65ms/step - loss: 0.7165 - accuracy: 0.4444 - val_loss: 0.6944 - val_accuracy: 0.6667
...
```

## Model Architecture

```
Input: (batch_size, 3 timesteps, 7 features)
  ↓
SimpleRNN(32, activation='relu')  # 32 hidden units
  ↓
Dense(16, activation='relu')       # Intermediate layer
  ↓
Dense(1, activation='sigmoid')     # Binary classification output (0 or 1)
```

## Data Format

The training data CSV requires:
- **Features**: `total_spots`, `unique_dx_stations`, `unique_spotters`, `spots_10m`, `spots_12m`, `spots_15m`, `spots_10m_fm`
- **Labels**: `band_open_10m` (1=band open, 0=band closed)
- Optional columns: `date`, `band_open_12m`, `band_open_15m`

Example row:
```
5000,1800,1500,1200,300,800,50,2025-10-01,1,1,1
total_spots=5000, unique_dx_stations=1800, ..., band_open_10m=1
```

## Comparing with LSTM Model

To compare this RNN model with the LSTM model:

```bash
# Train RNN model
cd rnn-model
python rnn_train_example.py

# Train LSTM model
cd ../lstm-model
python lstm_train_example.py

# Compare the accuracy and loss metrics printed by each
```

### Expected Comparison

On the same dataset with same hyperparameters:
- **RNN**: Typically faster training, may have slightly lower accuracy on longer sequences
- **LSTM**: Slower training, better at capturing long-term dependencies

## Parameters to Experiment With

Edit `rnn_train_example.py` to try different configurations:

```python
SEQUENCE_LENGTH = 3      # Try 2, 5, 7 to see effect on sequence length
LABEL_BAND = 'band_open_10m'  # Try 'band_open_12m' for different bands
EPOCHS = 30              # Try 50, 100 for more training
BATCH_SIZE = 2           # Try 4, 8, 16 for different batch sizes
```

## Understanding the Model

### SimpleRNN Layer
- Processes sequences one timestep at a time
- Maintains a hidden state that gets updated each step
- Formula: `h_t = tanh(W_ih * x_t + W_hh * h_{t-1} + b_h)`
- Much simpler than LSTM's cell and gate mechanisms

### Why SimpleRNN?
- **Educational**: Easier to understand before diving into LSTM
- **Faster**: Fewer parameters means quicker training
- **Good for**: Short sequences, simple patterns
- **Limited for**: Long sequences, complex temporal dependencies

## Next Steps

1. Increase training data for better generalization
2. Experiment with different sequence lengths
3. Try adding more dense layers
4. Implement early stopping to prevent overfitting
5. Use grid search to find optimal hyperparameters
6. Compare predictions between RNN and LSTM models

## References

- [TensorFlow SimpleRNN Documentation](https://www.tensorflow.org/api_docs/python/tf/keras/layers/SimpleRNN)
- [Understanding RNNs vs LSTMs](https://colah.github.io/posts/2015-08-Understanding-LSTMs/)
- [RNN Tutorial](https://stanford.edu/~shervine/teaching/cs-230/cheatsheet-recurrent-neural-networks)
