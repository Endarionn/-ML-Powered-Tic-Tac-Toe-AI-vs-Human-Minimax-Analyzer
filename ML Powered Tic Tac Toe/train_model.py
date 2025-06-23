import pandas as pd
import numpy as np
import time
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import Callback

CSV_FILE = "tic_tac_toe_data.csv"
MODEL_FILE = "tictactoe_model.keras"
EPOCHS = 15
BATCH_SIZE = 32

print("🔍 [1/5] Reading CSV data...")
df = pd.read_csv(CSV_FILE)

print("✅ CSV successfully loaded.")
print("🔄 [2/5] Converting data to numerical format...")

# Convert board data to numbers
X = df.drop("move", axis=1)
X = X.replace({"X": -1, "O": 1, "-": 0})
X = X.values.astype(np.float32)

y = df["move"].values
y = to_categorical(y, num_classes=9)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

print("✅ Data preparation complete.")
print("🧠 [3/5] Defining the model...")

# Define the model
model = Sequential([
    Dense(64, input_dim=9, activation='relu'),
    Dense(32, activation='relu'),
    Dense(9, activation='softmax')
])

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

print("✅ Model compiled.")
print(f"🚀 [4/5] Starting training ({EPOCHS} epochs, batch size {BATCH_SIZE})...")

# Custom callback to show training progress
class ProgressLogger(Callback):
    def on_train_begin(self, logs=None):
        self.start_time = time.time()

    def on_epoch_end(self, epoch, logs=None):
        elapsed = time.time() - self.start_time
        percent = (epoch + 1) / EPOCHS * 100
        avg_time = elapsed / (epoch + 1)
        remaining = avg_time * (EPOCHS - epoch - 1)
        print(f"📊 Epoch {epoch+1}/{EPOCHS} - {percent:.1f}% complete | "
              f"Loss: {logs['loss']:.4f}, Acc: {logs['accuracy']:.4f} | "
              f"⏱️ Estimated time remaining: {remaining:.1f}s")

# Train the model
model.fit(X_train, y_train, epochs=EPOCHS, batch_size=BATCH_SIZE,
          validation_split=0.1, verbose=0, callbacks=[ProgressLogger()])

print("✅ Training complete.")
print("💾 [5/5] Saving the model...")

model.save(MODEL_FILE)

print(f"✅ Model successfully saved as: {MODEL_FILE}")
