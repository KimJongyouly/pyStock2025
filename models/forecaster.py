import numpy as np
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler

# Define the PyTorch LSTM model
class PyTorchLSTM(nn.Module):
    def __init__(self, input_size=1, hidden_layer_size=50, output_size=1):
        super().__init__()
        self.hidden_layer_size = hidden_layer_size
        self.lstm = nn.LSTM(input_size, hidden_layer_size, batch_first=True)
        self.linear = nn.Linear(hidden_layer_size, output_size)

    def forward(self, input_seq):
        lstm_out, _ = self.lstm(input_seq)
        last_time_step_out = lstm_out[:, -1, :]
        predictions = self.linear(last_time_step_out)
        return predictions

class LSTMForecaster:
    """
    A class to create, train, and use a PyTorch-based LSTM model for time series forecasting.
    """
    def __init__(self, n_steps=60):
        self.n_steps = n_steps
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = PyTorchLSTM()
        self.training_data_raw = None

    def _create_sequences(self, input_data):
        sequences = []
        labels = []
        for i in range(len(input_data) - self.n_steps):
            seq = input_data[i:i + self.n_steps]
            label = input_data[i + self.n_steps:i + self.n_steps + 1]
            sequences.append(seq)
            labels.append(label)
        return torch.FloatTensor(np.array(sequences)), torch.FloatTensor(np.array(labels))

    def build_and_train(self, data, epochs=50, batch_size=32):
        """
        Builds and trains the LSTM model.
        """
        self.training_data_raw = data.reshape(-1, 1)
        scaled_data = self.scaler.fit_transform(self.training_data_raw)

        X_train, y_train = self._create_sequences(scaled_data)

        loss_function = nn.MSELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)

        for i in range(epochs):
            for j in range(0, len(X_train), batch_size):
                seq_batch = X_train[j:j+batch_size]
                label_batch = y_train[j:j+batch_size]

                optimizer.zero_grad()
                
                y_pred = self.model(seq_batch)

                single_loss = loss_function(y_pred, label_batch)
                single_loss.backward()
                optimizer.step()
            
            if (i+1) % 10 == 0:
                print(f'Epoch: {i+1:3} loss: {single_loss.item():10.8f}')


    def predict(self, days_to_predict=30):
        """
        Predicts future values.
        """
        if self.training_data_raw is None:
            raise ValueError("Model has not been trained yet.")

        self.model.eval()

        scaled_data = self.scaler.transform(self.training_data_raw)

        last_sequence = scaled_data[-self.n_steps:]
        
        future_predictions = []

        with torch.no_grad():
            current_sequence = torch.FloatTensor(last_sequence).view(1, self.n_steps, 1)
            
            for _ in range(days_to_predict):
                next_pred = self.model(current_sequence)
                future_predictions.append(next_pred.item())

                new_sequence_end = next_pred.view(1, 1, 1)
                current_sequence = torch.cat((current_sequence[:, 1:, :], new_sequence_end), axis=1)

        predicted_prices = self.scaler.inverse_transform(np.array(future_predictions).reshape(-1, 1))
        
        self.model.train()
        
        return predicted_prices.flatten().tolist()