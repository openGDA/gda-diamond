from threading import Event
from java.time import Instant, Duration, ZoneId, LocalDateTime # @UnresolvedImport
from org.slf4j import LoggerFactory # @UnresolvedImport
from java.net import NoRouteToHostException  # @UnresolvedImportfrom gas_saving.valve import ValveController, Valve
from gda.device import DeviceException  # @UnresolvedImport


class WaitForGas:
    """ 
    It is not always appropriate to open a gas valve and reset the interlock (allowing shutter to open) immediately.
    This class is responsible for delaying the interlock reset according to some configuration.

    The strategy is to see whether the valve has been on for an accumulative amount of time specified
    within a search window. If it has not, we block for that specified time.
    """
    
    LOGGER = LoggerFactory.getLogger("gas_saving.live.WaitForGas")
    
    def __init__(self, pv, target_value, search_window_pv, delay_pv):

        """
        pv: pv whose history we are searching in the archiver
        target_value: the 'desirable' value
        search_window_pv: in minutes
        delay_pv: in minutes. we want to see the PV having target_value for this amount of time
                  or more in total within the search window; otherwise we wait by this amount
        """
        from gda.epics import LazyPVFactory  # @UnresolvedImport
        self.pv = pv
        livepv = LazyPVFactory.newDoublePV(pv)
        self.current_value = lambda: livepv.get()
        self.target = target_value
        self.window = LazyPVFactory.newDoublePV(search_window_pv)
        self.delay = LazyPVFactory.newDoublePV(delay_pv)
        
        from uk.ac.gda.epics.archiverclient import EpicsArchiverClient  # @UnresolvedImport
        self.archiver = EpicsArchiverClient("http://archappl.diamond.ac.uk/retrieval/data/")
        self.backup_archiver = EpicsArchiverClient("http://sbarchappl.diamond.ac.uk/retrieval/data/")
        
        # we use a threading.Event to wait, so that it can be interrupted (set) by a different thread
        self.gas_ready = Event()
    
    def wait(self):
        try:
            if self.should_wait():
                wait_min = self.delay.get()
                WaitForGas.LOGGER.info("Waiting %d min for gas to fill" % wait_min)
                wait_time = self.delay.get() * 60
                self.gas_ready.wait(wait_time)
                self.gas_ready.clear()
                WaitForGas.LOGGER.info("Finished waiting.")
        except:
            raise DeviceException("Error accessing archiver. Open gas & shutter manually.")
    
    def stop(self):
        self.gas_ready.set()
    
    def should_wait(self):

        now = LocalDateTime.now()
        search_start = now.minusMinutes(int(self.window.get()))

        records = self.retrieve_records(search_start)

        # We now calculate the 'on time' by finding pairs of 'off'/'on' events

        # no records (i.e. value has not changed for the duration of the search window)
        if records.isEmpty():
            # wait if the current value is not what we want
            return self.current_value() != self.target

        # we iterate from earliest to newest events
        laston = None
        ontime = 0

        # special case if we only have 1 record because we use two for each increment
        if records.get().getData().size() == 1:
            
            record = records.get().getData().get(0)
            record_time = self.get_record_time(record)
            if record.getVal() == self.target:
                # it's the transition to on;
                # set on time as time from then to now
                ontime = Duration.between(record_time, self.get_zone_time(now)).toMinutes()
            else:
                # it has been on from the start of search window
                # to time of record (no assumptions as to before search window)
                ontime = Duration.between(search_start, record_time).toMinutes()

        else:

            for record in records.get().getData():

                # if first 'Open' event since last duration increment,
                # cache the time
                if record.getVal() == self.target and not laston:
                    laston = self.get_record_time(record)

                # if 'Close' event and we have seen an 'Open' event earlier,
                # increment the on time by the duration between these two.
                elif record.getVal() != self.target and laston:
                    ontime += Duration.between(laston, self.get_record_time(record)).toMinutes()
                    laston = None
                
            # if final event was 'Open', we haven't yet counted the time since
            if laston:
                ontime += Duration.between(laston, self.get_zone_time(now)).toMinutes()

        WaitForGas.LOGGER.debug("Valve was open for a total of %d minutes within the specified window" % ontime)
        return ontime < self.delay.get()
    
    def get_record_time(self, record):
        return self.get_zone_time(Instant.ofEpochSecond(record.getSecs(), record.getNanos()))

    def get_zone_time(self, time):
        return time.atZone(ZoneId.systemDefault())

    def retrieve_records(self, start_time):
        try:
            return self.archiver.getRecordForPv(self.pv, start_time)
        except NoRouteToHostException, e:
            WaitForGas.LOGGER.warn("Primary EPICS archiver unreachable; trying Standby Archiver", e)
            return self.backup_archiver.getRecordForPv(self.pv, start_time)
