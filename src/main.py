import cv2
import numpy as np
import sys
import os


_cur_dir = os.path.dirname(os.path.realpath(__file__))


class Chop:
    def __init__(self, rows=5, cols=6, debug=False):
        self.rows = rows
        self.cols = cols
        self.debug = debug

    def split(self, src_path):
        img = cv2.imread(src_path)
        if img is None:
            sys.stdout.write("cannot read image.\n")
            sys.exit(1)

        h, w = img.shape[:2]
        thumb_paths = []
        thumb_h, thumb_w = h // self.rows, w // self.cols
        for j in range(self.rows):
            for i in range(self.cols):
                y1 = max(0, j * thumb_h)
                y2 = min(h, (j + 1) * thumb_h - 1)
                x1 = max(0, i * thumb_w)
                x2 = min(w, (i + 1) * thumb_w - 1)

                thumb = img[y1:y2, x1:x2]
                dst_path = os.path.join(dst_folder, "thumb_{}_{}.jpg".format(j, i))
                cv2.imwrite(dst_path, thumb)
                thumb_paths.append(dst_path)
                if self.debug:
                    cv2.imshow("thumb", thumb)
                    key = cv2.waitKey(500)
                    if key == ord('q'):
                        break
        return thumb_paths


if __name__ == '__main__':
    img_fname = "sample.png"
    src_folder = os.path.join(_cur_dir, "..", "data")
    dst_folder = os.path.join(_cur_dir, "..", "data/result")
    Chop(debug=True).split(src_path=os.path.join(src_folder, img_fname))
