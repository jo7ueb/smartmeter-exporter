import logging,time
from typing import Optional, Tuple
from serial import Serial
from serial.threaded import LineReader
import traceback
import echonet as echonet

class SmartMeterThread(LineReader):
    def __init__(self):
        super().__init__()
        self.__logger = logging.getLogger(__name__)
        self.__last_line = None
        self.__is_echonet_established = False

    def connection_made(self, transport):
        super(SmartMeterThread, self).connection_made(transport)
        self.__logger.info("SmartMeterThread ready")
         
    def handle_line(self, data):
        self.__logger.debug(f'[SERIAL] <=== {data}')
        self.__last_line = data

        if self.__is_echonet_established:
            pass

    def connection_lost(self, exc):
        if exc:
            traceback.print_exc(exc)
        self.__logger.error("Something happened.")

    def __check_version(self):
        pass
    def __set_password(self, sm_password):
        pass
    def __set_id(self, sm_id):
        pass
    def __scan_smart_meter(self):
        pass
    def __set_reg(self, reg, val):
        pass
    def __get_ip_from_mac(self, macaddr):
        pass
    def __connect(self, addr):
        pass
    def establish_echonet(self, sm_id, sm_password):
        self.__logger.info('Establish connection to smartmeter Echonet ...')
        self.__logger.info('================ CONNECTION ESTABLISHED ================')
