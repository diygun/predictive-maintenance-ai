import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from pathlib import Path
import os


def compute_stft_spectrogram(signal_window: np.ndarray,
                             fs: float = 200.0,
                             n_fft: int = 256) -> np.ndarray:


    f, t, Zxx = signal.stft(
        signal_window,
        fs=fs,
        window="hann",
        nperseg=n_fft,
        noverlap=0,      # important : pas de chevauchement
        boundary=None,
        padded=False,
    )

    S = np.abs(Zxx)
    # amplitude -> dB (on ajoute un epsilon pour éviter log(0))
    S_db = 20 * np.log10(S + 1e-8)

    return S_db


def save_spectrogram_png(matrix: np.ndarray, filepath: Path) -> None:

    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(2, 2), dpi=100)
    plt.imshow(matrix, aspect="auto", origin="lower", cmap="viridis")
    plt.axis("off")
    plt.savefig(filepath, bbox_inches="tight", pad_inches=0)
    plt.close()


def ensure_output_dirs(base_dir: Path):

    base_dir = Path(base_dir)
    (base_dir / "sain").mkdir(parents=True, exist_ok=True)
    (base_dir / "balourd").mkdir(parents=True, exist_ok=True)
