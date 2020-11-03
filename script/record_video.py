import os
import os.path as osp
import time
import argparse

import cv2
import numpy as np
from multiprocessing import Process, Queue

parser = argparse.ArgumentParser()
parser.add_argument("--output", default="output", type=str, help="output directory")
parser.add_argument("--camera", default=2, type=int, help="number of cameras")

def find_webcams(n, limit=10):
    """Find n numbers of webcams"""
    webcams = []
    for i in range(1, limit):
        cap = cv2.VideoCapture(i)
        if not cap.isOpened():
            continue
        webcams.append((i, cap))
        if len(webcams) >= n:
            break

    return webcams

def export_video(writer, queue):
    while True:
        if not queue.empty():
            frame = queue.get()
            writer.write(frame)
        else:
            time.sleep(0.01)

def main(args):
    # Global information
    PATTERN_SIZE = (9, 6)

    # Video readers
    webcams = find_webcams(args['camera'])
    indices = [ cam[0] for cam in webcams ]
    caps = [ cam[1] for cam in webcams ]

    # Video writers
    writers = []
    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    for i, cap in enumerate(caps):
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        writer = cv2.VideoWriter(osp.join(args['output'], 'video{}.mp4'.format(i)), fourcc, fps, (width, height))
        queue = Queue(maxsize=64)
        process = Process(target=export_video, args=(writer, queue), daemon=True)
        process.start()
        writers.append((process, queue))

    # Video windows
    windows = []
    for i, cap in enumerate(caps):
        win_name = "Cam{}".format(i)
        cv2.namedWindow(win_name, cv2.WINDOW_GUI_EXPANDED)
        windows.append(win_name)

    medias = list(zip(caps, writers, windows))
    while True:
        start_time = time.time()
        frames = [ media[0].read()[1] for media in medias ]

        for i, frame in enumerate(frames):
            print(medias[i][1][1].qsize())
            medias[i][1][1].put(frame)

        for i, frame in enumerate(frames):
            win_name = medias[i][2]
            cv2.imshow(win_name, frame)

        elapsed_time = time.time() - start_time
        print(elapsed_time)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    for media in medias:
        media[0].release()
    cv2.destroyAllWindows()
    print("End of recording")

if __name__ == "__main__":
    args = vars(parser.parse_args())
    main(args)
