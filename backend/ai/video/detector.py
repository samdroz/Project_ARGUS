from ai.image.detecter import detect_image


class VideoDetector:

    def analyze_frames(self, frame_paths):

        predictions = []
        confidences = []

        for frame in frame_paths:

            result = detect_image(frame)

            predictions.append(result["prediction"])
            confidences.append(result["confidence"])

        return {
            "predictions": predictions,
            "confidences": confidences
        }


video_detector = VideoDetector()