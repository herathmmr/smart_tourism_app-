

import tensorflow as tf
from tensorflow.keras import layers, Model, regularizers



# Main Model Builder

def build_noise_classifier(input_shape, num_classes=2, l2_reg=1e-4):
    
    reg = regularizers.l2(l2_reg)
    inputs = tf.keras.Input(shape=input_shape, name='mfcc_input')

    # ── CNN Block 1: Low-level spectral features ──
    x = layers.Conv2D(32, kernel_size=(3, 3), padding='same',
                      activation='relu', kernel_regularizer=reg,
                      name='conv1')(inputs)
    x = layers.BatchNormalization(name='bn1')(x)
    x = layers.MaxPooling2D(pool_size=(2, 2), name='pool1')(x)
    x = layers.Dropout(0.25, name='drop1')(x)

    # ── CNN Block 2: Mid-level pattern extraction ──
    x = layers.Conv2D(64, kernel_size=(3, 3), padding='same',
                      activation='relu', kernel_regularizer=reg,
                      name='conv2')(x)
    x = layers.BatchNormalization(name='bn2')(x)
    x = layers.MaxPooling2D(pool_size=(2, 2), name='pool2')(x)
    x = layers.Dropout(0.25, name='drop2')(x)

    # ── CNN Block 3: High-level feature maps ──
    x = layers.Conv2D(128, kernel_size=(3, 3), padding='same',
                      activation='relu', kernel_regularizer=reg,
                      name='conv3')(x)
    x = layers.BatchNormalization(name='bn3')(x)
    x = layers.MaxPooling2D(pool_size=(2, 2), name='pool3')(x)
    x = layers.Dropout(0.30, name='drop3')(x)

    # ── Reshape for LSTM: (batch, time_steps, features) ──
   
    shape = x.shape
    x = layers.Reshape(
        (shape[2], shape[1] * shape[3]),
        name='reshape_for_lstm'
    )(x)

   
    x = layers.Bidirectional(
        layers.LSTM(64, return_sequences=True, dropout=0.2,
                    recurrent_dropout=0.2),
        name='bilstm1'
    )(x)
    x = layers.Dropout(0.30, name='drop4')(x)

    
    x = layers.Bidirectional(
        layers.LSTM(32, return_sequences=False, dropout=0.2,
                    recurrent_dropout=0.2),
        name='bilstm2'
    )(x)
    x = layers.Dropout(0.30, name='drop5')(x)

    
    x = layers.Dense(64, activation='relu',
                     kernel_regularizer=reg, name='dense1')(x)
    x = layers.Dropout(0.40, name='drop6')(x)

    # softmax over 2 classes
    outputs = layers.Dense(
        num_classes, activation='softmax', name='output'
    )(x)

    model = Model(inputs, outputs, name='NoiseClassifier_CNN_BiLSTM')
    return model


# Lightweight model (faster inference on mobile)

def build_noise_classifier_lite(input_shape, num_classes=2):
    
    inputs = tf.keras.Input(shape=input_shape, name='mfcc_input')

    x = layers.Conv2D(16, (3, 3), padding='same', activation='relu')(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(0.25)(x)

    x = layers.Conv2D(32, (3, 3), padding='same', activation='relu')(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(0.25)(x)

    shape = x.shape
    x = layers.Reshape((shape[2], shape[1] * shape[3]))(x)

    x = layers.LSTM(32, return_sequences=False, dropout=0.2)(x)
    x = layers.Dropout(0.30)(x)

    x = layers.Dense(32, activation='relu')(x)
    outputs = layers.Dense(num_classes, activation='softmax')(x)

    model = Model(inputs, outputs, name='NoiseClassifier_Lite')
    return model


# Main — print summary

if __name__ == '__main__':
    INPUT_SHAPE = (40, 216, 3)   # (n_mfcc, time_steps, channels)

    print("=" * 55)
    print("Full model")
    print("=" * 55)
    model = build_noise_classifier(INPUT_SHAPE)
    model.summary()

    print("\n" + "=" * 55)
    print("Lite model (mobile)")
    print("=" * 55)
    lite = build_noise_classifier_lite(INPUT_SHAPE)
    lite.summary()
