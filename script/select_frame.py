import os
import os.path as osp
import argparse

import cv2


def main(args):
    # Open video
    cap = cv2.VideoCapture(args['video'])
    if not cap.isOpened():
        raise RuntimeError("Cannot open video '{}'".format(args['video']))

    # Select target frames, e.g "30 420 570"
    fids = [ int(f) for f in args['frames'] ]
    for fid in fids:
        cap.set(cv2.CAP_PROP_POS_FRAMES, fid)
        _, frame = cap.read()

        # Save target frame
        cv2.imwrite("{}.jpg".format(fid), frame)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True, help="path of video file")
    parser.add_argument("--frames", nargs='+', help="frames to select")
    parser.add_argument("--output", default="target", help="output dir")

    args = vars(parser.parse_args())
    main(args)

