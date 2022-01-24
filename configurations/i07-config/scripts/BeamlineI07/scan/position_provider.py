import logging


from gda.scan import ScanPositionProvider
from gda.device.scannable import ScannableUtils

logger = logging.getLogger('BeamlineI07.scan.position_provider')

class ValidPositionsProvider(ScanPositionProvider):

    def __init__(self, scannable, start, stop, step):
        self._scannable = scannable
        self._start = start
        self._stop = stop
        self._step = step
        self._valid_points = self.generate_points()

    def get(self, index):
        return self._valid_points[index]

    def size(self):
        return len(self._valid_points)

    def generate_points(self):
        return [p for p in self._points() if self._check(p)]

    def _points(self):
        yield self._start
        point = self._start
        for i in range(ScannableUtils.getNumberSteps(self._scannable, self._start, self._stop, self._step)):
            point = ScannableUtils.calculateNextPoint(point, self._step)
            yield point

    def _check(self, point):
        valid = self._scannable.checkPositionValid(point)
        if valid is not None:
            print("Ignoring position: {} for {} from scan".format(point, self._scannable.getName()))
            logger.debug("%s: ignoring position: %s reason: %s", self._scannable.getName(), point, valid)
        return valid is None
