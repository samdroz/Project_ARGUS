import io
import numpy as np
from PIL import Image, ImageChops, ImageEnhance
from typing import Dict, Any


class ImageForensicAnalyzer:
    """
    Deterministic image forensics using Error Level Analysis (ELA),
    high-frequency noise analysis, and compression artifact detection.
    """

    def perform_ela(self, image: Image.Image, quality: int = 90, scale: int = 10) -> Dict[str, Any]:
        """
        Perform Error Level Analysis (ELA) by re-compressing at specified quality
        and calculating pixel differences.
        """
        try:
            buffer = io.BytesIO()
            image.save(buffer, "JPEG", quality=quality)
            buffer.seek(0)
            resaved_image = Image.open(buffer)

            # Calculate difference
            diff = ImageChops.difference(image, resaved_image)
            diff_enhancer = ImageEnhance.Brightness(diff)
            enhanced_diff = diff_enhancer.enhance(scale)

            # Compute statistics
            diff_arr = np.array(diff, dtype=np.float32)
            mean_error = float(np.mean(diff_arr))
            max_error = float(np.max(diff_arr))
            std_error = float(np.std(diff_arr))

            # Local variance in blocks of 32x32 to find splicing anomalies
            h, w = diff_arr.shape[:2]
            block_size = 32
            block_means = []
            for y in range(0, h - block_size + 1, block_size):
                for x in range(0, w - block_size + 1, block_size):
                    block = diff_arr[y:y+block_size, x:x+block_size]
                    block_means.append(np.mean(block))

            block_variance = float(np.std(block_means)) if block_means else 0.0

            # High block variance relative to mean suggests localized editing/splicing
            splicing_risk = "LOW"
            if block_variance > 12.0 or (mean_error > 2.0 and block_variance / max(1.0, mean_error) > 3.0):
                splicing_risk = "HIGH"
            elif block_variance > 6.0:
                splicing_risk = "MEDIUM"

            return {
                "ela_mean_error": round(mean_error, 2),
                "ela_max_error": round(max_error, 2),
                "ela_std_error": round(std_error, 2),
                "ela_block_variance": round(block_variance, 2),
                "splicing_risk": splicing_risk
            }
        except Exception as e:
            return {
                "ela_error": str(e),
                "splicing_risk": "UNKNOWN"
            }

    def analyze_frequency_and_noise(self, image: Image.Image) -> Dict[str, Any]:
        """
        Evaluate frequency distribution and Laplacian variance (blurriness / sharpness / noise consistency).
        """
        try:
            gray = image.convert("L")
            img_arr = np.array(gray, dtype=np.float32)

            # Fast 2D Laplacian approximation
            padded = np.pad(img_arr, 1, mode="edge")
            laplacian = (
                padded[:-2, 1:-1] + padded[2:, 1:-1] +
                padded[1:-1, :-2] + padded[1:-1, 2:] -
                4.0 * padded[1:-1, 1:-1]
            )

            sharpness_variance = float(np.var(laplacian))

            # 2D FFT analysis for synthetic grid / generative artifacts
            f_transform = np.fft.fft2(img_arr)
            f_shift = np.fft.fftshift(f_transform)
            magnitude_spectrum = np.log(np.abs(f_shift) + 1.0)
            threshold = float(np.percentile(magnitude_spectrum, 95))
            high_freq_ratio = float(np.mean(magnitude_spectrum > threshold))

            return {
                "sharpness_score": round(sharpness_variance, 2),
                "high_frequency_artifact_ratio": round(high_freq_ratio, 4),
                "is_blurry": sharpness_variance < 50.0,
                "is_synthetic_noise_pattern": high_freq_ratio > 0.08
            }
        except Exception as e:
            return {
                "noise_analysis_error": str(e)
            }

    def analyze(self, image: Image.Image) -> Dict[str, Any]:
        """
        Run complete deterministic forensic suite on PIL image.
        """
        ela_results = self.perform_ela(image)
        freq_results = self.analyze_frequency_and_noise(image)

        is_synthetic = freq_results.get("is_synthetic_noise_pattern", False)
        splicing_risk = ela_results.get("splicing_risk", "LOW")

        if is_synthetic and splicing_risk in ("HIGH", "MEDIUM"):
            forensic_prediction = "Fake"
            forensic_confidence = 78.5
        elif splicing_risk == "HIGH":
            forensic_prediction = "Fake"
            forensic_confidence = 72.0
        elif is_synthetic:
            forensic_prediction = "Fake"
            forensic_confidence = 65.0
        else:
            forensic_prediction = "Real"
            forensic_confidence = 68.0

        return {
            "prediction": forensic_prediction,
            "confidence": forensic_confidence,
            "ela": ela_results,
            "frequency_analysis": freq_results
        }


image_forensics = ImageForensicAnalyzer()
