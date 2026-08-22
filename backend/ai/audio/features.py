import io
import math
import os
import wave
from typing import Dict, Any, Tuple
import torch


def load_wav_file(file_path: str, max_duration_sec: int = 60) -> Tuple[torch.Tensor, int, float]:
    """
    Load a WAV audio file into a normalized float32 PyTorch tensor using standard library.
    Returns: (waveform_tensor [channels, samples], sample_rate, duration_sec)
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found at {file_path}")

    with wave.open(file_path, "rb") as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()

        if framerate <= 0:
            framerate = 16000

        total_duration = n_frames / framerate
        frames_to_read = min(n_frames, int(framerate * max_duration_sec))
        raw_bytes = wf.readframes(frames_to_read)

    if sampwidth == 2:
        tensor = torch.frombuffer(bytearray(raw_bytes), dtype=torch.int16).float() / 32768.0
    elif sampwidth == 4:
        tensor = torch.frombuffer(bytearray(raw_bytes), dtype=torch.int32).float() / 2147483648.0
    elif sampwidth == 1:
        tensor = (torch.frombuffer(bytearray(raw_bytes), dtype=torch.uint8).float() - 128.0) / 128.0
    else:
        # Fallback for 24-bit or uncompressed PCM
        tensor = torch.frombuffer(bytearray(raw_bytes), dtype=torch.int16).float() / 32768.0

    if n_channels > 1:
        tensor = tensor.view(-1, n_channels).t()
    else:
        tensor = tensor.unsqueeze(0)

    duration_sec = tensor.shape[1] / framerate
    return tensor, framerate, duration_sec


class AudioFeatureExtractor:
    """
    Deterministic acoustic and spectral feature extraction for synthetic speech & voice clone detection.
    """

    def extract_features(self, waveform: torch.Tensor, sample_rate: int) -> Dict[str, Any]:
        # Convert to mono if multi-channel
        if waveform.ndim > 1 and waveform.shape[0] > 1:
            mono = torch.mean(waveform, dim=0, keepdim=True)
        else:
            mono = waveform

        samples = mono.shape[1]
        if samples < 512:
            return {
                "error": "Audio too short for spectral analysis.",
                "duration_sec": 0.0
            }

        # 1. Zero-Crossing Rate (ZCR)
        signs = torch.sign(mono[0])
        zcr = float(torch.mean(torch.abs(signs[1:] - signs[:-1])) / 2.0)

        # 2. STFT Spectrogram
        n_fft = min(512, samples)
        hop_length = n_fft // 2
        window = torch.hann_window(n_fft)
        stft = torch.stft(mono, n_fft=n_fft, hop_length=hop_length, window=window, return_complex=True)
        magnitude = torch.abs(stft)[0]  # [freq_bins, time_frames]

        # 3. Spectral Centroid
        freq_bins = magnitude.shape[0]
        freqs = torch.linspace(0, sample_rate / 2.0, steps=freq_bins)
        sum_mag = torch.sum(magnitude, dim=0) + 1e-8
        centroid_per_frame = torch.sum(magnitude * freqs.unsqueeze(1), dim=0) / sum_mag
        mean_centroid = float(torch.mean(centroid_per_frame))

        # 4. Spectral Flatness (ratio of geometric mean to arithmetic mean)
        eps = 1e-8
        log_mag = torch.log(magnitude + eps)
        geom_mean = torch.exp(torch.mean(log_mag, dim=0))
        arith_mean = torch.mean(magnitude, dim=0) + eps
        flatness_per_frame = geom_mean / arith_mean
        mean_flatness = float(torch.mean(flatness_per_frame))

        # 5. Energy and Pitch Variance
        frame_energy = torch.sum(magnitude ** 2, dim=0)
        energy_std = float(torch.std(frame_energy))
        energy_mean = float(torch.mean(frame_energy))
        energy_var_ratio = energy_std / max(1e-6, energy_mean)

        # Spectral discontinuity check (sudden jumps in centroid)
        centroid_diff = torch.abs(centroid_per_frame[1:] - centroid_per_frame[:-1])
        max_centroid_jump = float(torch.max(centroid_diff)) if centroid_diff.numel() > 0 else 0.0
        has_spectral_discontinuity = max_centroid_jump > (sample_rate * 0.35)

        # Unnatural pitch / spectral flatness consistency (typical in synthetic neural vocoders)
        unnatural_stability = (energy_var_ratio < 0.40 and mean_flatness < 0.05) or (mean_centroid > (sample_rate * 0.42))

        return {
            "sample_rate": sample_rate,
            "zero_crossing_rate": round(zcr, 4),
            "spectral_centroid_hz": round(mean_centroid, 2),
            "spectral_flatness": round(mean_flatness, 4),
            "energy_variance_ratio": round(energy_var_ratio, 3),
            "spectral_discontinuity": has_spectral_discontinuity,
            "unnatural_pitch_stability": unnatural_stability
        }


audio_features = AudioFeatureExtractor()
