import os
import os.path as osp
import argparse

import cv2
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--output", default="output", type=str, help="output directory")
parser.add_argument("--fps", default=30, type=int, help="exporting video fps")

def main(args):
    # Global information
    PATTERN_SIZE = (9, 6)

    # Video writer
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    writer1 = cv2.VideoWriter(osp.join(args['output'], 'video1.avi'), fourcc, args['fps'], (1280, 720))
    writer2 = cv2.VideoWriter(osp.join(args['output'], 'video2.avi'), fourcc, args['fps'], (1280, 720))

    # GUI window
    cv2.namedWindow("F1", cv2.WINDOW_GUI_EXPANDED)
    cv2.namedWindow("F2", cv2.WINDOW_GUI_EXPANDED)

    # Video reader
    cap1 = cv2.VideoCapture(2)
    cap2 = cv2.VideoCapture(4)
    try:
        while True:
            ret, frame1 = cap1.read()
            ret, frame2 = cap2.read()

            writer1.write(frame1)
            writer2.write(frame2)

            cv2.imshow("F1", frame1)
            cv2.imshow("F2", frame2)

            key = cv2.waitKey(1)
            if key == ord('q'):
                break
    except Exception as e:
        pass

    cap1.release()
    cap2.release()
    writer1.release()
    writer2.release()
    print("End of recording")

if __name__ == "__main__":
    args = vars(parser.parse_args())
    main(args)
