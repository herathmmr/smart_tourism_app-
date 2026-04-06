

import os
import numpy as np
import tensorflow as tf
from model import build_noise_classifier_lite

from model import build_noise_classifier


WEIGHTS_PATH = 'noise_model_best.h5'
TFLITE_PATH  = 'noise_model.tflite'
INPUT_SHAPE  = (40, 216, 3)


def export_tflite(weights_path=WEIGHTS_PATH,
                  tflite_path=TFLITE_PATH,
                  input_shape=INPUT_SHAPE,
                  quantize=True):
    
    # Rebuild model and load weights
    model = build_noise_classifier_lite(input_shape)
    model.load_weights(weights_path)
    print(f"Weights loaded from {weights_path}")

    # Convert to TFLite
    converter = tf.lite.TFLiteConverter.from_keras_model(model)

    if quantize:
        # Dynamic range quantization:
        #   weights: float32 → int8  (size ÷ 4)
        #   activations: quantized at inference time
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        print("Quantization: enabled (dynamic range)")
    else:
        print("Quantization: disabled")

    tflite_model = converter.convert()

    with open(tflite_path, 'wb') as f:
        f.write(tflite_model)

    size_kb = len(tflite_model) / 1024
    print(f"\nExported: {tflite_path}")
    print(f"Size    : {size_kb:.1f} KB")

    # Quick validation 
    _validate_tflite(tflite_path, input_shape)

    return tflite_path


def _validate_tflite(tflite_path, input_shape):
    
    interpreter = tf.lite.Interpreter(model_path=tflite_path)
    interpreter.allocate_tensors()

    input_details  = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    dummy = np.random.rand(1, *input_shape).astype(np.float32)
    interpreter.set_tensor(input_details[0]['index'], dummy)
    interpreter.invoke()

    output = interpreter.get_tensor(output_details[0]['index'])
    print(f"Validation OK — output shape: {output.shape}, probs: {output[0]}")


if __name__ == '__main__':
    export_tflite()
