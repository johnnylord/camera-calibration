import os
import os.path as osp
import argparse

import cv2
import numpy as np
import pickle


parser = argparse.ArgumentParser()
parser.add_argument("--size", default=1.0, type=float, help="size of the chessboard square in meter")
parser.add_argument("--input", default="input/", help="input directory")
parser.add_argument("--output", default="output/camera.pkl", help="output file")

# Chessboard setting
PATTERN_SIZE = (9, 6)
CAMERA_WIDTH = 1920
CAMERA_HEIGHT = 1080

def main(args):
    # Read imgs of chessboard from input directory
    img_files = [ osp.join(args['input'], f) for f in os.listdir(args['input']) if 'jpg' in f ]

    # Prepare world coordinate information of chessboard (planar model)
    # =================================================================
    pattern_points = np.zeros((np.prod(PATTERN_SIZE), 3), np.float32)
    pattern_points[:, :2] = np.indices(PATTERN_SIZE).T.reshape(-1, 2)
    pattern_points *= args['size']

    # Prepare pixel coordinate information of chessboard
    # ==================================================
    obj_points, img_points = [], []

    chessboards = []
    h, w = cv2.imread(img_files[0], cv2.IMREAD_GRAYSCALE).shape[:2]
    for f in img_files:
        img = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
        assert img.shape[0] == h and img.shape[1] == w

        found, corners = cv2.findChessboardCorners(img, PATTERN_SIZE)
        if found:
            print("Found chessboard in '{}'".format(f))
            # Refine the precision of corners
            term = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.1)
            cv2.cornerSubPix(img, corners, (5, 5), (-1, -1), term)
            chessboards.append((f, corners.reshape(-1, 2), pattern_points))
        else:
            chessboards.append((f, None, None))

    # Extract pixel coordinate & world coordinate pairs
    chessboards = [x for x in chessboards if x[1] is not None and x[2] is not None ]
    for (fname, corners, pattern_points) in chessboards:
        img_points.append(corners)
        obj_points.append(pattern_points)

    # Export camera intrinsic & extrinsic parameters
    # ============================================
    rms, camera_matrix, dist_coefs, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, (w, h), None, None)

    chessboard = {
            'size': args['size'],
            'pattern': PATTERN_SIZE }
    intrinsic = {
            'width': CAMERA_WIDTH,
            'height': CAMERA_HEIGHT,
            'matrix': camera_matrix,
            'dist_coefs': dist_coefs }
    extrinsics = {}

    valid_names = [ x[0] for x in chessboards ]
    for fname, rvec, tvec in zip(valid_names, rvecs, tvecs):
        rvec = np.array(rvec)
        R, _ = cv2.Rodrigues(rvec) # 3x3
        T = np.array(tvec) # 3x1
        extrinsics[fname] = { 'R': R, 'T': T }

    with open(args['output'], 'wb') as f:
        camera = {
            'chessboard': chessboard,
            'intrinsic': intrinsic,
            'extrinsics': extrinsics }
        pickle.dump(camera, f)
        print("Save calibration result to '{}'".format(args['output']))

if __name__ == '__main__':
    args = vars(parser.parse_args())
    main(args)
