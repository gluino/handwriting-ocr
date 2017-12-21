"""
Last: 1095
Script with simple UI for creating gaplines data
Run: python WordClassDM.py --index 0
Controls:
    setting gaplines  - click and drag
    saving gaplines   - 's' key
    reseting gaplines - 'r' key
"""

import cv2
import numpy as np
import glob
import argparse
import simplejson
from ocr.normalization import imageNorm
from ocr.viz import printProgressBar


def loadImages(dataloc, idx=0):
    """ Load images and labels """
    print("Loading words...")

    dataloc += '/' if dataloc[-1] != '/' else ''
    # Load images and short them from the oldest to the newest
    imglist = glob.glob(dataloc + '*.jpg')
    imglist.sort(key=lambda x: float(x.split("_")[-1][:-4]))
    tmpLabels = [name[len(dataloc):] for name in imglist]

    labels = np.array(tmpLabels)
    images = np.empty(len(imglist), dtype=object)

    for i, img in enumerate(imglist):
        # TODO Speed up loading - Normalization
        if i >= idx:
            images[i] = imageNorm(
                cv2.cvtColor(cv2.imread(img), cv2.COLOR_BGR2RGB),
                height=60,
                border=False,
                tilt=True,
                hystNorm=True)
        printProgressBar(i, len(imglist))
    return (images[idx:], labels[idx:])


class Cycler:
    drawing = False
    scaleF = 4

    def __init__(self, idx, loc='data/words_raw'):
        """ Load images and starts from given index """
        self.images, self.labels = loadImages(loc, idx)
        self.idx = 0
        self.org_idx = idx
        self.image_act = self.images[self.idx]
        cv2.namedWindow('image')
        self.nextImage()
        cv2.setMouseCallback('image', self.mouseHandler)
        self.run()

    def run(self):
        while(1):
            self.imageShow()
            k = cv2.waitKey(1) & 0xFF
            if k == ord('d'):
                # Delete last line
                print("Delete last line - DOESNT WORK YET")
            elif k == ord('r'):
                # Clear current gaplines
                self.nextImage()
            elif k == ord('s'):
                # Save gaplines with image
                self.saveData()
            elif k == ord('n'):
                # Skip to next image
                self.idx += 1
                self.nextImage()
            elif k == 27:
                cv2.destroyAllWindows()
                break

        print("End of labeling at INDEX: " + str(self.org_idx + self.idx))

    def imageShow(self):
        cv2.imshow(
            'image',
            cv2.resize(
                self.image_act,
                (0,0),
                fx=self.scaleF,
                fy=self.scaleF,
                interpolation=cv2.INTERSECT_NONE))

    def nextImage(self):
        self.image_act = cv2.cvtColor(self.images[self.idx], cv2.COLOR_GRAY2RGB)
        self.label_act = self.labels[self.idx][:-4]
        self.gaplines =  [0, self.image_act.shape[1]]
        for x in self.gaplines:
            self.drawLine(x)

        print(self.org_idx + self.idx, ":", self.label_act.split("_")[0])
        self.imageShow();

    def saveData(self):
        self.gaplines.sort()
        print("Saving image with gaplines: ", self.gaplines)

        try:
            assert len(self.gaplines) - 1 == len(self.label_act.split("_")[0])

            cv2.imwrite("data/words2/%s.jpg" % (self.label_act),
                        self.images[self.idx])
            with open('data/words2/%s.txt' % (self.label_act), 'w') as fp:
                simplejson.dump(self.gaplines, fp)

            self.idx += 1
        except:
            print("Wront number of gaplines")

        print()
        self.nextImage()

    def deleteLastLine(self):
        pass

    def drawLine(self, x):
        cv2.line(
            self.image_act, (x, 0), (x, self.image_act.shape[0]), (0,255,0), 1)

    def mouseHandler(self, event, x, y, flags, param):
        # Clip x into image width range
        x = max(min(self.image_act.shape[1], x // self.scaleF), 0)

        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.tmp = self.image_act.copy()
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing == True:
                self.image_act = self.tmp.copy()
                self.drawLine(x)
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            self.gaplines.append(x)
            self.image_act = self.tmp.copy()
            self.drawLine(x)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            "Script creating UI for gaplines classification")
    parser.add_argument(
        "--index",
        type=int,
        default=0,
        help="Index of starting image")

    args = parser.parse_args()
    Cycler(args.index)