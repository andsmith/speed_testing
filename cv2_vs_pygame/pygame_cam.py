import pygame
import pygame.camera
import pygame.locals
from generic_tester import CameraSpeedTester, get_settings
import logging
from threading import Thread
import time
from loop_timing.loop_profiler import LoopPerfTimer


class PygameCamWrap(object):
    """
    Map inputs from pygame.camera to what generic_tester needs (cv2 style).
    """

    def __init__(self, index, resolution, callback=None):
        """
        :param index:  camera index
        :param resolution:  width, height
        :param callback:  function to call with each frame
        """
        self._callback = callback
        self._finished = False
        self._index, self._resolution = index, resolution
        self._cam = None
        self._display = None
        self._snapshot = None
        self._capture_thread = None

    def display(self):
        self._display.blit(self._snapshot, (0, 0))
        self._display.blit(self._snapshot, (0, 0))

    def _thread_proc(self):
        logging.info("Pygame camera thread wrapper starting.")
        pygame.init()
        pygame.camera.init()
        self._cam = pygame.camera.Camera([self._index], self._resolution, "RGB")
        self._display = pygame.display.set_mode(self._resolution, 0)
        self._snapshot = pygame.surface.Surface(self._resolution, 0, self._display)
        self._capture_thread = Thread(target=self._thread_proc)
        while not self._finished:
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.locals.QUIT or (e.type == pygame.locals.KEYDOWN and
                                                    e.key == pygame.locals.K_ESCAPE):
                    break

            if self._cam.query_image():
                self._snapshot = self._cam.get_image(self._snapshot)
                if self._callback is not None:
                    self._callback(self._snapshot)

        self._cam.stop()
        self._snapshot.stop()
        self._display.stop()
        logging.info("Pygame camera thread wrapper finishing.")

    def set_callback(self, callback):
        self._callback = callback

    def start(self):
        self._capture_thread.start()

    def stop(self):
        self._finished = True


class PygameSpeedTester(CameraSpeedTester):
    """lightweight wrapper"""

    def _proc_frame(self, frame, *args):
        LoopPerfTimer.add_marker("Frame capture")

        self._process_image(frame)
        LoopPerfTimer.mark_loop_start()

        self._cam.display(frame)
        LoopPerfTimer.add_marker("display")

        # Printing timing info
        self._fps_info['n_frames'] += 1
        now = time.perf_counter()
        elapsed = now - self._fps_info['t_start']
        if elapsed > CameraSpeedTester.FPS_INTERVAL_SEC:
            logging.info("FPS:  %.3f" % (self._fps_info['n_frames'] / elapsed), )
            self._fps_info = {'t_start': now, 'n_frames': 0}

        self._n_frames += 1

    def start(self):
        self._cam.start()

    def shutdown(self):
        self._cam.stop()


def run_pygame_test(cam_ind=0):
    "Make a Camera object, give to tester, run test, exit."
    logging.info("Testing pygame capture/display rate with camera %i." % (cam_ind,))
    width, height = get_settings(cam_ind)
    pygame_cam = PygameCamWrap(cam_ind, resolution=(width, height))
    PygameSpeedTester(pygame_cam, n_burn=120, n_collect=200).shutdown()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    run_pygame_test()
