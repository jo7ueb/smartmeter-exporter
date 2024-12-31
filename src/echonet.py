import logging

# 第3章 電文構成(フレームフォーマット) 3.2 電文構成 を参照

smartmeter_eoj = b'\x02\x88\x01' #住宅設備関連機器(低圧スマート電力量メータクラス)
wisun_module_eoj = b'\x05\xFF\x01' #管理操作関連機器/コントローラ
epc_kWh = b'\xE0' #EPC 積算電力量
epc_kWh_unit = b'\xE1' #EPC積算電力量単位
epc_watt = b'\xE7' #EPC 瞬時電力計測値
epc_ampare = b'\xE8' #EPC 瞬時電流計測値

esv_req_codes = {
    "Get": b'\x62',
}

esv_res_codes = {
    "Get_Res": b'r', #b'\x72' (pythonの仕様上、bytes.fromhexすると文字変換されてしまう)
}

logger = logging.getLogger(__name__)

def process_elite_response_packet(data):

    # basic header
    packet_header = {
        'ehd1': bytes.fromhex(data[0:2]),
        'ehd2': bytes.fromhex(data[2:4]),
        'tid': bytes.fromhex(data[4:8]),
        'seoj': bytes.fromhex(data[8:14]),
        'deoj': bytes.fromhex(data[16:20]),
        'esv': bytes.fromhex(data[20:22]),
        'opc': int(data[22:24], 16),
    }
    packet_data = bytes.fromhex(data[24:])
    logger.debug(packet_header)
    logger.debug(f'Processing {packet_header["opc"]} objects...')

    # SEOJ(送信元オブジェクト)がスマートメーターでない場合は無視する
    if packet_header['seoj'] != smartmeter_eoj:
        logger.info(f'Ignoring packet with unrecognized SEOJ {packet_header["seoj"]}')
        return None, None

    # データ部を読み取る
    byteidx = 0
    observations = []
    for i in range (packet_header['opc']):
        logger.debug(f'[EPC {i}')
        pdc = int.from_bytes(packet_data[byteidx+1:byteidx+2])
        observation = {
            'epc': packet_data[byteidx],
            'pdc': pdc,
            'edt': packet_data[byteidx+2:byteidx+2+pdc]
        }
        observations.append(observation)
        byteidx += (2 + pdc)
        logger.debug(f'    data: {observations[i]}')
        
def parse_elite_response_data(data: str):
    parse_data = {
        "ehd1": bytes.fromhex(data[0:0+2]),
        "ehd2": bytes.fromhex(data[2:2+2]),
        "tid": bytes.fromhex(data[4:4+4]),
        "seoj": bytes.fromhex(data[8:8+6]),
        "deoj": bytes.fromhex(data[14:14+6]),
        "esv": bytes.fromhex(data[20:20+2]),
        "opc": bytes.fromhex(data[22:22+2]),
        "epc": bytes.fromhex(data[24:24+2]),
        "pdc": bytes.fromhex(data[26:26+2]),
        "edt": data[28:],
    }
    return parse_data

def make_elite_request_str():
    data = {
        "ehd1": b'\x10',
        "ehd2": b'\x81',
        "tid": b'\x00\x01',
        "seoj": wisun_module_eoj,
        "deoj": smartmeter_eoj,
        "esv": esv_req_codes['Get'], #読み出し要求
        "opc": b'\x04',          #処理対象プロパティカウンタ数
        "epc1": epc_kWh,
        "pdc1": b'\x00',   
        "epc2": epc_kWh_unit,
        "pdc2": b'\x00',   
        "epc3": epc_watt,
        "pdc3": b'\x00',   
        "epc4": epc_ampare,
        "pdc4": b'\x00',   
    }
    return b''.join(data.values())
