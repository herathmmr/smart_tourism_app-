

import numpy as np
import librosa
import tempfile
import soundfile as sf


# Constants

SAMPLE_RATE  = 22050   # Hz
DURATION     = 5.0     # seconds
N_MFCC       = 40      # number of MFCC coefficients
N_FFT        = 2048    # FFT window size
HOP_LENGTH   = 512     # frames between windows


# MFCC Feature Extraction

def extract_mfcc(file_path,
                 sample_rate=SAMPLE_RATE,
                 duration=DURATION,
                 n_mfcc=N_MFCC,
                 n_fft=N_FFT,
                 hop_length=HOP_LENGTH):

    
    audio, sr = librosa.load(file_path, sr=sample_rate, mono=True, duration=duration)

   
    target_length = int(sample_rate * duration)
    if len(audio) < target_length:
        audio = np.pad(audio, (0, target_length - len(audio)), mode='constant')
    else:
        audio = audio[:target_length]

    
    audio = np.append(audio[0], audio[1:] - 0.97 * audio[:-1])

    # Compute MFCCs
    mfcc = librosa.feature.mfcc(
        y=audio, sr=sr,
        n_mfcc=n_mfcc,
        n_fft=n_fft,
        hop_length=hop_length
    )

    
    mfcc_delta  = librosa.feature.delta(mfcc)
    mfcc_delta2 = librosa.feature.delta(mfcc, order=2)

    mfcc_combined = np.stack([mfcc, mfcc_delta, mfcc_delta2], axis=-1)

    mean = mfcc_combined.mean()
    std  = mfcc_combined.std() + 1e-8   # avoid division by zero
    mfcc_combined = (mfcc_combined - mean) / std

    return mfcc_combined   # shape: (40, ~216, 3)


# Audio Augmentation

def augment_audio(audio, sr=SAMPLE_RATE):
   

    # 1. Add slight Gaussian noise
    noise_factor = np.random.uniform(0.002, 0.015)
    audio = audio + noise_factor * np.random.randn(len(audio))

    # 2. Time stretch — slightly speed up or slow down
    rate  = np.random.uniform(0.9, 1.1)
    audio = librosa.effects.time_stretch(audio, rate=rate)

    # 3. Pitch shift — ±2 semitones
    n_steps = np.random.uniform(-2, 2)
    audio   = librosa.effects.pitch_shift(audio, sr=sr, n_steps=n_steps)

    return audio


def extract_mfcc_from_array(audio, sample_rate=SAMPLE_RATE, duration=DURATION,
                             n_mfcc=N_MFCC, n_fft=N_FFT, hop_length=HOP_LENGTH):
    
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        sf.write(tmp.name, audio, sample_rate)
        return extract_mfcc(tmp.name, sample_rate, duration, n_mfcc, n_fft, hop_length)



# Quick test

if __name__ == '__main__':
    import os
    print("preprocess.py — self test")
    print(f"Sample rate : {SAMPLE_RATE} Hz")
    print(f"Duration    : {DURATION} s")
    print(f"MFCC dims   : ({N_MFCC}, ~{int(SAMPLE_RATE * DURATION / HOP_LENGTH) + 1}, 3)")
    print("Import OK.")
