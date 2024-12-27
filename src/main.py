import logging, os, time, prometheus_client
from prometheus_client import Gauge
from smart_meter_connection import SmartMeterConnection
from smart_meter_thread import SmartMeterThread
from serial import Serial
from serial.threaded import ReaderThread
if __name__ == '__main__':

    sm_id = os.environ.get('SMARTMETER_ID', None)
    sm_key= os.environ.get('SMARTMETER_PASSWORD', None)
    sm_dev = os.environ.get('SMARTMETER_DEVICE', '/dev/ttyUSB0')
    sm_log_level = int(os.environ.get('SMARTMETER_LOGLEVEL', 10))
    sm_interval = int(os.environ.get('SMARTMETER_GET_INTERVAL', 10))
    sm_port = int(os.environ.get('PORT', 8000))

    logging.basicConfig(format='%(asctime)s %(levelname)s %(filename)s:%(lineno)d : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=sm_log_level)
    logger = logging.getLogger('connection')

    prometheus_client.start_http_server(sm_port)

    kWh_gauge = Gauge('accumulated_power_consumption_kWh', 'Accumulated power consumption in kWh')
    watt_gauge = Gauge('power_consumption_watt', 'Power consumption in Watt')
    ampare_gauge_r = Gauge('power_consumption_ampare_r', 'Power consumption in Ampare(R)')
    ampare_gauge_t = Gauge('power_consumption_ampare_t', 'Power consumption in Ampare(T)')

    serial = Serial(sm_dev, 115200, timeout=1)
    with ReaderThread(serial, SmartMeterThread) as protocol:
        protocol.establish_echonet(sm_id, sm_key)
        
        while True:
            logger.info('Sending request to smartmeter.')
            protocol.write_line('SKINFO')
            time.sleep(sm_interval)
                
    with SmartMeterConnection(sm_id, sm_key, sm_dev) as conn:
        conn.initialize_params()
         
        logger.info("================ CONNECTION ESTABLISHED ================")
        while True:
            kWh_raw_data = conn.get_data('kWh')
            kWh_unit_raw_data = conn.get_data('kWh_unit')
            logger.debug(f'kWh_raw: {kWh_raw_data}')
            logger.debug(f'kWh_unit_raw: {kWh_unit_raw_data}')
            if kWh_raw_data and kWh_unit_raw_data:
                kWh_data = int(kWh_raw_data, 16)
                kWh_unit_data = int(kWh_unit_raw_data, 16)
                #         0    1     2      3      4      5     6     7     8     9     A     B       C       D
                coeff = (1.0, 0.1, 0.01, 0.001, 0.0001, None, None, None, None, None, 10.0, 100.0, 1000.0, 10000.0)
                kWh_data *= coeff[kWh_unit_data]
                kWh_gauge.set(kWh_data)
                logger.info(f'[Gauge set] Current kWh: {kWh_data} kWh')
            watt_raw_data = conn.get_data('watt')
            if not watt_raw_data is None:
                watt_data = int(watt_raw_data,16)
                watt_gauge.set(watt_data)
                logger.info(f'[Gauge set] Current power consumption(Watt): {watt_data} W')

            ampare_data = conn.get_data('ampare')
            if not ampare_data is None:
                ampare_data_r = int(ampare_data[0:4], 16) * 100
                ampare_data_t = int(ampare_data[4:8], 16) * 100
                if not ampare_data_r  is None:
                    ampare_gauge_r.set(ampare_data_r)
                    logger.info(f'[Gauge set] Current power consumption(Ampare/R): {ampare_data_r} mA')
                if not ampare_data_t  is None:
                    ampare_gauge_t.set(ampare_data_t)
                    logger.info(f'[Gauge set] Current power consumption(Ampare/T): {ampare_data_t} mA')
            time.sleep(sm_interval)
