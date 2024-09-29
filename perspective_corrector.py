import cv2
import numpy as np

class PerspectiveCorrector:
    def __init__(self, image):
        self.image = image
        self.gray = None
        self.img_blur = None
        self.img_canny = None
        self.img_dilation = None
        self.img_erosion = None
        self.warped_img = None

    @staticmethod
    def reorder(points):
        points_new = np.zeros_like(points)
        points = points.reshape((4, 2))
        add = points.sum(1)
        points_new[0] = points[np.argmin(add)]
        points_new[3] = points[np.argmax(add)]

        diff = np.diff(points, axis=1)
        points_new[1] = points[np.argmin(diff)]
        points_new[2] = points[np.argmax(diff)]

        return points_new

    @staticmethod
    def warp_img(img, points, w, h):
        points = PerspectiveCorrector.reorder(points)
        pts1 = np.float32(points)
        pts2 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        img_warp = cv2.warpPerspective(img, matrix, (w, h))

        return img_warp

    def correct_perspective(self):
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.img_blur = cv2.GaussianBlur(self.gray, (5, 5), 1)
        self.img_canny = cv2.Canny(self.img_blur, 80, 80)
        _, thresh = cv2.threshold(self.img_blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        kernel = np.ones((3, 3), np.uint8)
        self.img_dilation = cv2.dilate(thresh, kernel, iterations=1)
        self.img_erosion = cv2.erode(self.img_dilation, kernel, iterations=1)

        cntrs, _ = cv2.findContours(self.img_erosion, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        cnt_max = max(cntrs, key=cv2.contourArea)
        approx = cv2.approxPolyDP(cnt_max, 0.02 * cv2.arcLength(cnt_max, True), True)
        
        if len(approx) == 4:
            self.points = approx
            (height_q, width_q) = self.image.shape[:2]
            self.warped_img = PerspectiveCorrector.warp_img(self.image, approx, width_q, height_q)
        else:
            self.warped_img = self.image
            # TO-DO: dsize should be a standard dimension.
        self.warped_img = cv2.resize(self.warped_img, dsize=(1024, 768), interpolation=cv2.INTER_CUBIC)
        return self.warped_img
