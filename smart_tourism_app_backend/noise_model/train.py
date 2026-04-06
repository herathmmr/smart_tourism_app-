import os
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf

from dataset import load_splits
from model import build_noise_classifier_lite


# Config
SPLITS_DIR   = 'data/splits'
WEIGHTS_PATH = 'noise_model_best.h5'
EPOCHS       = 100
BATCH_SIZE   = 32
LEARNING_RATE = 1e-4


# Callbacks
def get_callbacks(weights_path=WEIGHTS_PATH):
    return [
        # Stop training when val_loss stops improving
        tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),
        # Save the best weights automatically
        tf.keras.callbacks.ModelCheckpoint(
            filepath=weights_path,
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        ),
        # Reduce LR when plateau is detected
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-6,
            verbose=1
        ),
        # TensorBoard logging
        tf.keras.callbacks.TensorBoard(
            log_dir='logs/noise_model',
            histogram_freq=1
        ),
    ]


# Training
def train(splits_dir=SPLITS_DIR):
    # Load pre-built splits
    X_train, X_val, X_test, y_train, y_val, y_test = load_splits(splits_dir)

    input_shape = X_train.shape[1:]   # (40, 216, 3)
    print(f"\nInput shape : {input_shape}")
    print(f"Train size  : {X_train.shape[0]}")
    print(f"Val size    : {X_val.shape[0]}")
    print(f"Test size   : {X_test.shape[0]}\n")

    # Build model
    model = build_noise_classifier_lite(input_shape)

    # Compile
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    # Train
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=get_callbacks(),
        verbose=1
    )

    # Quick test evaluation
    test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
    print(f"\nTest accuracy : {test_acc:.4f}")
    print(f"Test loss     : {test_loss:.4f}")

    # Save final model
    model.save('noise_model_final.h5')
    print("Model saved: noise_model_final.h5")

    # Plot learning curves
    plot_history(history)

    return model, history


# Learning curve plot
def plot_history(history):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    # Accuracy
    axes[0].plot(history.history['accuracy'],     label='Train')
    axes[0].plot(history.history['val_accuracy'], label='Validation')
    axes[0].set_title('Model Accuracy')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Accuracy')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Loss
    axes[1].plot(history.history['loss'],     label='Train')
    axes[1].plot(history.history['val_loss'], label='Validation')
    axes[1].set_title('Model Loss')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Loss')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('training_curves.png', dpi=150)
    print("Training curves saved: training_curves.png")
    plt.show()


# Main
if __name__ == '__main__':
    train()