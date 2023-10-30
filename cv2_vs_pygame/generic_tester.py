from abc import abstractmethod, ABCMeta
import time
from loop_timing.loop_profiler import LoopPerfTimer
import numpy as np
import logging

from gui_utils.camera_settings import user_pick_resolution


def get_settings(index):
    width, height = user_pick_resolution(camera_index=index, gui=False)
    return width, height


class CameraSpeedTester(metaclass=ABCMeta):
    FPS_INTERVAL_SEC = 2.0

    def __init__(self, camera, n_burn=90, n_collect=60, plot=True, win_name="speed tester"):
        self._burn = n_burn
        self._collect = n_collect
        self._plot = plot
        self._win_name = win_name
        self._n_frames = 0
        self._dropped = 0
        self._cam = camera
        self._cam.set_callback(self._proc_frame)

        self._timing_init()
        self._cam.start()

        self._fps_info = {'t_start': time.perf_counter(),
                          'n_frames': 0,
                          'n_dropped': 0}

    def _timing_init(self):
        LoopPerfTimer.reset(enable=True, burn_in=self._burn,
                            display_after=self._collect, save_filename=None)  # "cv2_cam.pkl")

    @LoopPerfTimer.time_function
    def _process_image(self, img):
        if self._n_frames < self._burn:
            img[20:250, 20:250, :] = np.uint8((img[20:250, 20:250, :]) / 2)
        else:
            img[20:250, 20:250, :] = np.uint8((254 + np.int64(img[20:250, 20:250, :])) / 2)

    @abstractmethod
    def _proc_frame(self, frame, *args):
        """
        Process/display 1 frame of video using LoopPerfTimer to collect timing data.
        :param frame:  H x W x 3 image from camera capture.
        :param args:  Additional args (flags/timestamp) returned by capture
        """

    @abstractmethod
    def shutdown(self):
        """
        Close camera and all windows
        """
