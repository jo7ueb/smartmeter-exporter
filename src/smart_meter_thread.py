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
        self.__received_lines = []
        self.__is_echonet_established = False

    def connection_made(self, transport):
        super(SmartMeterThread, self).connection_made(transport)
        self.__logger.info("SmartMeterThread ready")
         
    def handle_line(self, data):
        self.__logger.debug(f'[SERIAL] <=== {data}')
        self.__received_lines.append(data)

        if self.__is_echonet_established:
            pass

    def connection_lost(self, exc):
        if exc:
            traceback.print_exc(exc)
        self.__logger.error("Something happened.")

    # 内部で送信する際はこのラッパーを使う
    def __write(self, line):
        self.__logger.debug(f'[SERIAL] ===> {line}')
        self.write_line(line)
        time.sleep(0.1)
        
    # コネクションを張る処理に使う関数群
    def __check_version(self):
        self.__write('SKVER')
        self.__logger.debug(self.__received_lines)
        ever = self.__received_lines.pop(0)
        version = ever.split(' ')[1]
        self.__logger.info(f'Wi-SUN version: {version}')
        assert self.__received_lines.pop(0) == 'OK'
        return version

    def __set_password(self, sm_password):
        self.__write(f'SKSETPWD C {sm_password}')
        assert self.__received_lines.pop(0) == 'OK'
 
    def __set_id(self, sm_id):
        self.__write(f'SKSETRBID {sm_id}')
        assert self.__received_lines.pop(0) == 'OK'
        
    def __scan_smart_meter(self):
        self.__logger.info('Scanning smart meter')
        for duration in range (6, 14):
            self.__logger.debug(f'Start scanning with duration {duration}')
            self.__write(f'SKSCAN 2 FFFFFFFF {duration}')
            assert self.__received_lines.pop(0) == 'OK'
            
            while len(self.__received_lines) == 0:
                pass

            line = self.__received_lines.pop(0)
            if line.startswith('EVENT 22'):  # 見つからなかった
                 continue
            elif line.startswith('EVENT 20'): # 見つかった
                time.sleep(1)  # 電文が揃うのを待つ
                assert self.__received_lines.pop(0).startswith('EPANDESC')
                channel = self.__received_lines.pop(0).split(':')[1]
                channel_page = self.__received_lines.pop(0).split(':')[1]
                pan_id = self.__received_lines.pop(0).split(':')[1]
                addr = self.__received_lines.pop(0).split(':')[1]
                LQI = self.__received_lines.pop(0).split(':')[1]
                pair_id = self.__received_lines.pop(0).split(':')[1]

                # LQI値からRSSIを求める
                rssi = 0.275*int(LQI, 16) - 104.27

                self.__logger.info('Scan has been finished.')
                self.__logger.debug(f'    channel: {channel}')
                self.__logger.debug(f'    channel_page: {channel_page}')
                self.__logger.debug(f'    pan_id: {pan_id}')
                self.__logger.debug(f'    addr: {addr}')
                self.__logger.debug(f'    RSSI(dBm): {rssi}')
                self.__logger.debug(f'    pair_id: {pair_id}')

                return channel, pan_id, addr
            else:
                raise Exception(f'Unexpected reply: {self.__received_lines}')
        raise Exception('Scan failure.')
 
    def __set_reg(self, reg_name, value):
        self.__write(f'SKSREG {reg_name} {value}')
 
        assert self.__received_lines.pop(0) == 'OK'

    def __get_ip_from_mac(self, macaddr):
        pass
    def __connect(self, addr):
        pass
    def establish_echonet(self, sm_id, sm_password):
        self.__logger.info('Establish connection to smartmeter Echonet ...')

        # ローカルエコーは邪魔なので消す
        self.__set_reg('SFE', '0')
        self.__check_version()
        self.__set_password(sm_password)
        self.__set_id(sm_id)
        channel, pan_id, addr = self.__scan_smart_meter()
        self.__set_reg('S2', channel)
        self.__set_reg('S3', pan_id)
        link_local_addr = self.__get_ip_from_mac(addr)
        self.__connect(link_local_addr)

        self.__logger.info('================ CONNECTION ESTABLISHED ================')
