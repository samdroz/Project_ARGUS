import cv2
import os


class FrameExtractor:

    def extract(self, video_path, output_folder):

        os.makedirs(output_folder, exist_ok=True)

        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise Exception("Cannot open video")

        fps = cap.get(cv2.CAP_PROP_FPS)

        print(f"FPS: {fps}")

        frame_interval = int(fps)

        print(f"Extracting every {frame_interval} frames")

        saved = []

        frame_no = 0

        while True:

            ret, frame = cap.read()

            if not ret:
                print("Reached end of video")
                break

            if frame_no % frame_interval == 0:

                filename = os.path.join(
                    output_folder,
                    f"frame_{frame_no}.jpg"
                )

                success = cv2.imwrite(filename, frame)

                print(
                    f"Saving frame {frame_no} -> {filename} : {success}"
                )

                saved.append(filename)

            frame_no += 1

        cap.release()

        print(f"Saved {len(saved)} frames")

        return saved


extractor = FrameExtractor()