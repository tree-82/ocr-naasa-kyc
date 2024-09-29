import cv2
import numpy as np

class LineDetector:
    def __init__(self, image):
        self.image = image
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.blurred = cv2.GaussianBlur(self.gray, (5, 5), 0)
        self.edges = cv2.Canny(self.blurred, 50, 150, apertureSize=3)
        self.rotated_image = None

    def detect_longest_line(self):
        lines = cv2.HoughLinesP(self.edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)
        max_length = 0
        best_line = None
        for line in lines:
            for x1, y1, x2, y2 in line:
                length = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                if length > max_length:
                    max_length = length
                    best_line = (x1, y1, x2, y2)
        return best_line

    def calculate_rotation_angle(self, line):
        x1, y1, x2, y2 = line
        angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
        return angle

    def rotate_image(self, angle, image):
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, -angle, 1.0)

        # Compute the new bounding dimensions of the image
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
        new_w = int((h * sin) + (w * cos))
        new_h = int((h * cos) + (w * sin))

        # Adjust the rotation matrix to take into account translation
        M[0, 2] += (new_w / 2) - center[0]
        M[1, 2] += (new_h / 2) - center[1]

        rotated_image = cv2.warpAffine(image, M, (new_w, new_h))
        return rotated_image

    def is_line_in_top_half(self, line, image):
        x1, y1, x2, y2 = line
        h = image.shape[0]
        return (y1 < h // 2) and (y2 < h // 2)

    def change_orientation_by_line(self):
        best_line = self.detect_longest_line()
        if best_line:
            angle = self.calculate_rotation_angle(best_line)
            rotated_image = self.rotate_image(angle, self.image)
            self.rotated_image = rotated_image
            
            if not self.is_line_in_top_half(best_line, rotated_image):
                # Rotate by 180 degrees if the line is in the bottom half
                rotated_image = self.rotate_image(180, rotated_image)

            self.rotated_image = rotated_image
            return self.rotated_image
        else:
            print("No line detected.")
            return self.image

