import logging, os, time, prometheus_client
from prometheus_client import Gauge
from smart_meter_thread import SmartMeterThread
from serial import Serial
from serial.threaded import ReaderThread
import echonet

if __name__ == '__main__':

    sm_id = os.environ.get('SMARTMETER_ID', None)
    sm_key= os.environ.get('SMARTMETER_PASSWORD', None)
    sm_dev = os.environ.get('SMARTMETER_DEVICE', '/dev/ttyUSB0')
    sm_log_level = int(os.environ.get('SMARTMETER_LOGLEVEL', 10))
    sm_interval = int(os.environ.get('SMARTMETER_GET_INTERVAL', 15))
    sm_port = int(os.environ.get('PORT', 8000))

    logging.basicConfig(format='%(asctime)s %(levelname)s %(filename)s:%(lineno)d : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=sm_log_level)
    logger = logging.getLogger('connection')

    serial = Serial(sm_dev, 115200, timeout=1)
    with ReaderThread(serial, SmartMeterThread) as protocol:
        protocol.establish_echonet(sm_id, sm_key)
        
        while True:
            logger.info('Sending request to smartmeter.')
            protocol.send_echonet_packet(echonet.make_elite_request_str())
            time.sleep(sm_interval)
                
