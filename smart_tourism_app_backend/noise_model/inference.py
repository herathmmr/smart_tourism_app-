

import argparse
import json
import os
import tempfile
import time
from datetime import datetime, timezone

import numpy as np
import sounddevice as sd
import soundfile as sf
import tensorflow as tf

from preprocess import extract_mfcc, SAMPLE_RATE, DURATION



# Config

WEIGHTS_PATH   = 'noise_model_best.h5'
CLASS_NAMES    = ['crowd', 'nature']
DB_THRESHOLD   = 65.0   # dB — above this is considered loud / crowded
CONF_THRESHOLD = 0.70   # minimum confidence to trust the prediction



# Load model

def load_model(weights_path=WEIGHTS_PATH, input_shape=(40, 173, 3)):
    """Load model architecture + weights."""
    from model import build_noise_classifier
    model = build_noise_classifier(input_shape)
    model.load_weights(weights_path)
    return model



# dB Level measurement

def measure_db(audio, reference=94.0):
   
    rms = np.sqrt(np.mean(audio ** 2) + 1e-9)
    db  = 20 * np.log10(rms) + reference
    return round(float(db), 1)



# Record from microphone

def record_audio(duration=DURATION, sample_rate=SAMPLE_RATE):
   
    print(f"  Recording {duration}s ...")
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='float32'
    )
    sd.wait()
    return audio.flatten()



# Single classification
def classify(model,
             audio=None,
             location_id='unknown',
             duration=DURATION,
             sample_rate=SAMPLE_RATE,
             db_threshold=DB_THRESHOLD,
             conf_threshold=CONF_THRESHOLD):
   
    if audio is None:
        audio = record_audio(duration, sample_rate)

    # Measure dB 
    db_level = measure_db(audio)

    # Extract MFCC features
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        sf.write(tmp.name, audio, sample_rate)
        features = extract_mfcc(tmp.name, sample_rate, duration)
        os.unlink(tmp.name)

    # Inference
    features_batch = np.expand_dims(features, axis=0)          # (1, 40, 173, 3)
    probs     = model.predict(features_batch, verbose=0)[0]    # (2,)
    class_idx = int(np.argmax(probs))
    confidence = float(probs[class_idx])
    label      = CLASS_NAMES[class_idx]

    # Determine crowded status using BOTH classifier AND dB level
    # Both must agree to reduce false positives
    is_crowded = (
        label == 'crowd'
        and db_level >= db_threshold
        and confidence >= conf_threshold
    )

    result = {
        'acoustic_signal': {
            'label'      : label,
            'confidence' : round(confidence, 3),
            'db_level'   : db_level,
            'is_crowded' : is_crowded,
            'class_probs': {
                'crowd' : round(float(probs[0]), 3),
                'nature': round(float(probs[1]), 3),
            },
            'timestamp'  : datetime.now(timezone.utc).isoformat(),
            'location_id': location_id,
        }
    }

    return result


# Continuous monitoring loop
def monitor_loop(model, location_id='unknown',
                 interval_sec=30, output_file=None):
   
    print(f"\nContinuous monitoring — {location_id}")
    print(f"Recording every {interval_sec}s. Press Ctrl+C to stop.\n")

    results = []
    try:
        while True:
            result = classify(model, location_id=location_id)
            signal = result['acoustic_signal']

            # Console output
            status = "CROWDED" if signal['is_crowded'] else "calm"
            print(
                f"[{signal['timestamp'][:19]}] "
                f"{signal['label']:6s} | "
                f"conf={signal['confidence']:.2f} | "
                f"dB={signal['db_level']} | "
                f"→ {status}"
            )

            results.append(result)

            # Write to JSONL file if specified
            if output_file:
                with open(output_file, 'a') as f:
                    f.write(json.dumps(result) + '\n')

            time.sleep(interval_sec)

    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

    return results


# TFLite inference 
def classify_tflite(tflite_path, audio, sample_rate=SAMPLE_RATE,
                    duration=DURATION, location_id='unknown',
                    db_threshold=DB_THRESHOLD):
    
    import tempfile, os

    db_level = measure_db(audio)

    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        sf.write(tmp.name, audio, sample_rate)
        features = extract_mfcc(tmp.name, sample_rate, duration)
        os.unlink(tmp.name)

    interpreter = tf.lite.Interpreter(model_path=tflite_path)
    interpreter.allocate_tensors()

    input_details  = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    input_data = np.expand_dims(features, axis=0).astype(np.float32)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    probs     = interpreter.get_tensor(output_details[0]['index'])[0]
    class_idx = int(np.argmax(probs))
    label     = CLASS_NAMES[class_idx]

    return {
        'acoustic_signal': {
            'label'      : label,
            'confidence' : round(float(probs[class_idx]), 3),
            'db_level'   : db_level,
            'is_crowded' : label == 'crowd' and db_level >= db_threshold,
            'timestamp'  : datetime.now(timezone.utc).isoformat(),
            'location_id': location_id,
        }
    }


# Main
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Noise Model — Inference')
    parser.add_argument('--continuous',  action='store_true',
                        help='Run continuous monitoring loop')
    parser.add_argument('--location',   default='test_location',
                        help='Tourist location ID')
    parser.add_argument('--interval',   type=int, default=30,
                        help='Seconds between recordings (continuous mode)')
    parser.add_argument('--output',     default=None,
                        help='JSONL file to log results')
    parser.add_argument('--tflite',     default=None,
                        help='Path to .tflite model (optional)')
    args = parser.parse_args()

    if args.tflite:
        print(f"Using TFLite model: {args.tflite}")
        audio = record_audio()
        result = classify_tflite(args.tflite, audio, location_id=args.location)
        print(json.dumps(result, indent=2))
    else:
        model = load_model()

        if args.continuous:
            monitor_loop(model, location_id=args.location,
                         interval_sec=args.interval,
                         output_file=args.output)
        else:
            result = classify(model, location_id=args.location)
            print(json.dumps(result, indent=2))
