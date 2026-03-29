

import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from preprocess import extract_mfcc, augment_audio, SAMPLE_RATE, DURATION
import librosa
import soundfile as sf
import tempfile



# Label mapping

LABEL_MAP = {
    'crowd' : 0,   # Human crowd noise
    'nature': 1,   # Nature / ambient noise
}
LABEL_NAMES = {v: k for k, v in LABEL_MAP.items()}



# Build dataset from manifest CSV

def build_dataset(manifest_csv,
                  sample_rate=SAMPLE_RATE,
                  duration=DURATION,
                  augment=True,
                  augment_factor=2):
    """
    Read a CSV manifest and extract MFCC features for every clip.

    CSV must have columns:
        filepath   — path to .wav file
        label      — integer label (0 or 1)
        label_name — 'crowd' or 'nature'

    Args:
        manifest_csv    : Path to dataset manifest CSV
        sample_rate     : Audio sample rate
        duration        : Clip duration in seconds
        augment         : Whether to apply augmentation on training data
        augment_factor  : How many augmented copies per original clip

    Returns:
        X : np.ndarray  shape (n_samples, n_mfcc, time_frames, 3)
        y : np.ndarray  shape (n_samples,)
    """
    df = pd.read_csv(manifest_csv)
    X, y = [], []
    skipped = 0

    for idx, row in df.iterrows():
        try:
            # Extract original features
            features = extract_mfcc(row['filepath'], sample_rate, duration)
            X.append(features)
            y.append(int(row['label']))

            # Augmentation — generate extra copies
            if augment:
                audio, sr = librosa.load(row['filepath'], sr=sample_rate,
                                         mono=True, duration=duration)
                for _ in range(augment_factor):
                    aug_audio = augment_audio(audio.copy(), sr=sr)
                    aug_features = _features_from_array(aug_audio, sample_rate, duration)
                    X.append(aug_features)
                    y.append(int(row['label']))

        except Exception as e:
            print(f"  [SKIP] {row['filepath']}: {e}")
            skipped += 1

    print(f"\nDataset built: {len(X)} samples ({skipped} skipped)")
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.int32)


def _features_from_array(audio, sample_rate, duration):
    """Helper: extract MFCC features from a numpy audio array."""
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        sf.write(tmp.name, audio, sample_rate)
        feats = extract_mfcc(tmp.name, sample_rate, duration)
        os.unlink(tmp.name)
    return feats



# Train / Val / Test split

def split_dataset(X, y, val_ratio=0.15, test_ratio=0.15, random_state=42):
    """
    Stratified split into train / validation / test sets.

    Default: 70% train, 15% val, 15% test.

    Returns:
        (X_train, X_val, X_test, y_train, y_val, y_test)
    """
    temp_ratio = val_ratio + test_ratio

    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y,
        test_size=temp_ratio,
        stratify=y,
        random_state=random_state
    )

    relative_test = test_ratio / temp_ratio
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp,
        test_size=relative_test,
        stratify=y_temp,
        random_state=random_state
    )

    print("\nDataset split:")
    print(f"  Train : {X_train.shape[0]} samples")
    print(f"  Val   : {X_val.shape[0]} samples")
    print(f"  Test  : {X_test.shape[0]} samples")

    return X_train, X_val, X_test, y_train, y_val, y_test



# Save / Load numpy arrays

def save_splits(X_train, X_val, X_test, y_train, y_val, y_test,
                out_dir='data/splits'):
    os.makedirs(out_dir, exist_ok=True)
    np.save(f'{out_dir}/X_train.npy', X_train)
    np.save(f'{out_dir}/X_val.npy',   X_val)
    np.save(f'{out_dir}/X_test.npy',  X_test)
    np.save(f'{out_dir}/y_train.npy', y_train)
    np.save(f'{out_dir}/y_val.npy',   y_val)
    np.save(f'{out_dir}/y_test.npy',  y_test)
    print(f"Splits saved to {out_dir}/")


def load_splits(out_dir='data/splits'):
    X_train = np.load(f'{out_dir}/X_train.npy')
    X_val   = np.load(f'{out_dir}/X_val.npy')
    X_test  = np.load(f'{out_dir}/X_test.npy')
    y_train = np.load(f'{out_dir}/y_train.npy')
    y_val   = np.load(f'{out_dir}/y_val.npy')
    y_test  = np.load(f'{out_dir}/y_test.npy')
    print(f"Splits loaded from {out_dir}/")
    return X_train, X_val, X_test, y_train, y_val, y_test



# Generate a sample manifest (for testing)

def create_sample_manifest(output_csv='dataset_manifest.csv'):
    """
    Creates a sample CSV manifest template.
    Replace filepaths with your actual data.
    """
    data = {
        'filepath'  : [
            'data/crowd/ella_market_001.wav',
            'data/crowd/sigiriya_entrance_001.wav',
            'data/nature/sinharaja_forest_001.wav',
            'data/nature/mirissa_beach_calm_001.wav',
        ],
        'label'     : [0, 0, 1, 1],
        'label_name': ['crowd', 'crowd', 'nature', 'nature'],
        'duration'  : [4.0, 4.0, 4.0, 4.0],
        'source'    : ['field', 'field', 'field', 'field'],
    }
    df = pd.DataFrame(data)
    df.to_csv(output_csv, index=False)
    print(f"Sample manifest saved to {output_csv}")
    return df



# Main

if __name__ == '__main__':
    MANIFEST = 'dataset_manifest.csv'

    if not os.path.exists(MANIFEST):
        print("No manifest found — creating sample template...")
        create_sample_manifest(MANIFEST)
        print("Add your audio file paths to dataset_manifest.csv then re-run.")
    else:
        print("Building dataset...")
        X, y = build_dataset(MANIFEST, augment=True, augment_factor=2)
        splits = split_dataset(X, y)
        save_splits(*splits)
        print("Done.")
