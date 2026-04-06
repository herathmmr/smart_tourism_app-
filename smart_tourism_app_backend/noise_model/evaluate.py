

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
from model import build_noise_classifier_lite

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_curve,
    auc,
)

from dataset import load_splits, LABEL_NAMES
from model   import build_noise_classifier

WEIGHTS_PATH = 'noise_model_best.h5'
CLASS_NAMES  = ['Crowd Noise', 'Nature Noise']



# Load model + weights

def load_model(weights_path=WEIGHTS_PATH, splits_dir='data/splits'):
    X_train, _, _, _, _, _ = load_splits(splits_dir)
    input_shape = X_train.shape[1:]
    model = build_noise_classifier_lite(input_shape)
    model.load_weights(weights_path)
    print(f"Weights loaded from {weights_path}")
    return model



# Evaluate

def evaluate(model=None, splits_dir='data/splits'):
    _, _, X_test, _, _, y_test = load_splits(splits_dir)

    if model is None:
        model = load_model(splits_dir=splits_dir)

    # Predictions
    y_pred_probs = model.predict(X_test, verbose=0)
    y_pred       = np.argmax(y_pred_probs, axis=1)

    # Classification report 
    print("\n" + "=" * 55)
    print("Classification Report")
    print("=" * 55)
    print(classification_report(y_test, y_pred, target_names=CLASS_NAMES))

    # Confusion matrix 
    plot_confusion_matrix(y_test, y_pred)

    # ROC curve 
    plot_roc_curve(y_test, y_pred_probs)

    #  Per-class accuracy
    for cls_idx, cls_name in enumerate(CLASS_NAMES):
        mask     = y_test == cls_idx
        cls_acc  = np.mean(y_pred[mask] == y_test[mask])
        print(f"  {cls_name:15s} accuracy: {cls_acc:.4f}")

    return y_pred, y_pred_probs



# Confusion matrix plot

def plot_confusion_matrix(y_true, y_pred):
    cm = confusion_matrix(y_true, y_pred)
    cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Raw counts
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES,
                ax=axes[0])
    axes[0].set_title('Confusion Matrix (counts)')
    axes[0].set_ylabel('True Label')
    axes[0].set_xlabel('Predicted Label')

    # Normalised
    sns.heatmap(cm_norm, annot=True, fmt='.2f', cmap='Blues',
                xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES,
                ax=axes[1])
    axes[1].set_title('Confusion Matrix (normalised)')
    axes[1].set_ylabel('True Label')
    axes[1].set_xlabel('Predicted Label')

    plt.tight_layout()
    plt.savefig('confusion_matrix.png', dpi=150)
    print("Confusion matrix saved: confusion_matrix.png")
    plt.show()



# ROC curve plot

def plot_roc_curve(y_true, y_pred_probs):
    fpr, tpr, _ = roc_curve(y_true, y_pred_probs[:, 0], pos_label=0)
    roc_auc = auc(fpr, tpr)

    plt.figure(figsize=(7, 5))
    plt.plot(fpr, tpr, color='steelblue', lw=2,
             label=f'ROC curve (AUC = {roc_auc:.3f})')
    plt.plot([0, 1], [0, 1], color='gray', linestyle='--', lw=1)
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve — Noise Classifier')
    plt.legend(loc='lower right')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('roc_curve.png', dpi=150)
    print("ROC curve saved: roc_curve.png")
    plt.show()



# Main

if __name__ == '__main__':
    evaluate()
