from gui_utils.camera import Camera
from generic_tester import CameraSpeedTester, get_settings

import time

import cv2
import logging
from loop_timing.loop_profiler import LoopPerfTimer
import numpy as np
import time



class CV2SpeedTester(CameraSpeedTester):

    def _proc_frame(self, frame, *args):
        LoopPerfTimer.add_marker("Frame capture")

        if self._n_frames == 0:
            # needs to be same thread as display
            cv2.namedWindow(self._win_name)

        self._process_image(frame)
        LoopPerfTimer.mark_loop_start()

        cv2.imshow(self._win_name, frame)
        LoopPerfTimer.add_marker("display")

        k = cv2.waitKey(1)
        if k & 0xff == ord('q'):
            self.shutdown()
        LoopPerfTimer.add_marker("keyboard")

        # Printing timing info
        self._fps_info['n_frames'] += 1
        now = time.perf_counter()
        elapsed = now - self._fps_info['t_start']
        if elapsed > CameraSpeedTester.FPS_INTERVAL_SEC:
            logging.info("FPS:  %.3f" % (self._fps_info['n_frames'] / elapsed), )
            self._fps_info = {'t_start': now, 'n_frames': 0}

        self._n_frames += 1

    def shutdown(self):
        self._cam.shutdown()
        cv2.destroyAllWindows()


def run_cv2_test(cam_ind=0):
    "Make a Camera(), give to tester, run test, exit."
    logging.info("Testing CV2 capture/display rate with camera %i." % (cam_ind,))
    width, height = get_settings(cam_ind)

    settings = {cv2.CAP_PROP_FRAME_WIDTH: width,
                cv2.CAP_PROP_FRAME_HEIGHT: height}
    cv2_cam = Camera(cam_ind, None, settings=settings)
    CV2SpeedTester(cv2_cam, n_burn=120, n_collect=200).shutdown()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    run_cv2_test()
