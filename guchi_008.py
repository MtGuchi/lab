import csv
import struct
import sys

args = sys.argv

g_start = 0
g_new = 0
g_badges = []
g_badge = []
g_log_acc = []
g_log_audio = []
g_log_ir = []
g_log_vdd = []
g_badge.append(g_log_acc)
g_badge.append(g_log_audio)
g_badge.append(g_log_ir)
g_badge.append(g_log_vdd)


def dump_data(data):
    for d in data:
        print("0x%02x," % d, end="")
    print("")


def process_data_acc(data):
    global g_log_acc
    print("acc")
     # dump_data(data)
     # Epoch Time
    ts = struct.unpack("<I", data[2:6])
    ts = ts[0]
     # serial number within 1s
    index = struct.unpack("<H", data[6:8])
    index = index[0]
    length = data[8]
    print("timestamp = %d" % ts)
    print("index = %d" % index)
    print("length = %d" % length)
    
    data_acc = []
    for i in range(length // 2): # //:切捨除算
        val = data[i * 9 + 9:i * 9 + 18]
        (x0, y0, z0, x1, y1, z1) = extract_acc(val)
        t = ts + (index + (i * 2)) / 100
        g_log_acc.append((t, x0, y0, z0))
        t = ts + (index + (i * 2) + 1) / 100
        g_log_acc.append((t, x1, y1, z1))


def extract_acc(data):
    x0 = b""
    x0 += data[0].to_bytes(1, byteorder="big")
    t = data[1] >> 4
     # 負の場合
    if t & 0x08 == 0x08:
        t |= 0xF0
    t = t & 0xFF # 正負に関わらず8bitに統一
    x0 += t.to_bytes(1, byteorder="big")
    x0 = struct.unpack("<h", x0)
    x0 = x0[0]
     
    y0 = b""
    t = data[1] << 4
    t = t & 0xFF
    t = t | data[2] >> 4
    y0 += t.to_bytes(1, byteorder="big")
    t = data[2] & 0x0f
    if t & 0x08 == 0x08:
        t |= 0xF0    
    t = t & 0xFF
    y0 += t.to_bytes(1, byteorder="big")
    y0 = struct.unpack("<h", y0)
    y0 = y0[0]

    z0 = b""
    z0 += data[3].to_bytes(1, byteorder="big")
    t = data[4] >> 4
    if t & 0x08 == 0x08:
        t |= 0xF0
    t = t & 0xFF
    z0 += t.to_bytes(1, byteorder="big")
    z0 = struct.unpack("<h", z0)
    z0 = z0[0]

    x1 = b""
    t = data[4] << 4
    t = t & 0xFF
    t = t | data[5] >> 4
    x1 += t.to_bytes(1, byteorder="big")
    t = data[5] & 0x0f
    if t & 0x08 == 0x08:
        t |= 0xF0    
    t = t & 0xFF
    x1 += t.to_bytes(1, byteorder="big")
    x1 = struct.unpack("<h", x1)
    x1 = x1[0]
    
    y1 = b""
    y1 += data[6].to_bytes(1, byteorder="big")
    t = data[7] >> 4
    if t & 0x08 == 0x08:
        t |= 0xF0
    t = t & 0xFF
    y1 += t.to_bytes(1, byteorder="big")
    y1 = struct.unpack("<h", y1)
    y1 = y1[0]
    
    z1 = b""
    t = data[7] << 4
    t = t & 0xFF
    t = t | data[8] >> 4
    t = t & 0xFF
    z1 += t.to_bytes(1, byteorder="big")
    t = data[8] & 0x0f
    if t & 0x08 == 0x08:
        t |= 0xF0    
    t = t & 0xFF
    z1 += t.to_bytes(1, byteorder="big")
    z1 = struct.unpack("<h", z1)
    z1 = z1[0]

    return (x0, y0, z0, x1, y1, z1)


def process_data_ir(data):
    global g_log_ir
    print("ir")
     # dump_data(data)
     # Epoch Time
    ts = struct.unpack("<I", data[2:6])
    ts = ts[0]
    length = data[6]
    print("timestamp = %d" % ts)
    print("length = %d" % length)

    data_ir = []
    for i in range(length):
        data_ir.append(data[i + 6])
         # print("%d" % data[i + 6])
         # print(data_ir[i])
    
    for i in range(100):
        g_log_ir.extend((ts, data_ir[i]))


def process_data_audio(data):
    global g_log_audio
    print("audio")
     # dump_data(data)
     # Epoch Time
    ts = struct.unpack("<I", data[2:6])
    ts = ts[0]
     # serial number within 1s
    index = struct.unpack("<H", data[6:8])
    index = index[0]
    length = data[8]
    print("timestamp = %d" % ts)
    print("index = %d" % index)
    print("length = %d" % length)
    
    data_audio = []
    for i in range(length // 6): # //:切捨除算
        val = data[i * 9 + 9:i * 9 + 18]
        (audio_0, audio_1, audio_2, audio_3, audio_4, audio_5) = extract_audio(val)
        data_audio.extend((audio_0, audio_1, audio_2, audio_3, audio_4, audio_5))
     # 余った分の処理
    val = data[16 * 9 + 6:16 * 9 + 15]
    (audio_0, audio_1, audio_2, audio_3, audio_4, audio_5) = extract_audio(val)
    data_audio.extend((audio_2, audio_3, audio_4, audio_5))

    for i in range(length): # //:切捨除算
        t = ts + index + i / 100
        g_log_audio.extend((t, data_audio[i]))


def extract_audio(data):
    audio_0 = b""
    audio_0 += data[0].to_bytes(1, byteorder="big")
    t = data[1] >> 4
    t = t & 0xFF
    audio_0 += t.to_bytes(1, byteorder="big")
    audio_0 = struct.unpack("<H", audio_0)
    audio_0 = audio_0[0]
    
    audio_1 = b""
    t = data[1] << 4
    t = t & 0xFF
    t = t | data[2] >> 4
    audio_1 += t.to_bytes(1, byteorder="big")
    t = data[2] & 0x0f
    t = t & 0xFF
    audio_1 += t.to_bytes(1, byteorder="big")
    audio_1 = struct.unpack("<H", audio_1)
    audio_1 = audio_1[0]
    
    audio_2 = b""
    audio_2 += data[3].to_bytes(1, byteorder="big")
    t = data[4] >> 4
    t = t & 0xFF
    audio_2 += t.to_bytes(1, byteorder="big")
    audio_2 = struct.unpack("<H", audio_2)
    audio_2 = audio_2[0]

    audio_3 = b""
    t = data[4] << 4
    t = t & 0xFF
    t = t | data[5] >> 4
    audio_3 += t.to_bytes(1, byteorder="big")
    t = data[5] & 0x0f
    t = t & 0xFF
    audio_3 += t.to_bytes(1, byteorder="big")
    audio_3 = struct.unpack("<H", audio_3)
    audio_3 = audio_3[0]
    
    audio_4 = b""
    audio_4 += data[6].to_bytes(1, byteorder="big")
    t = data[7] >> 4
    t = t & 0xFF
    audio_4 += t.to_bytes(1, byteorder="big")
    audio_4 = struct.unpack("<H", audio_4)
    audio_4 = audio_4[0]
    
    audio_5 = b""
    t = data[7] << 4
    t = t & 0xFF
    t = t | data[8] >> 4
    t = t & 0xFF
    audio_5 += t.to_bytes(1, byteorder="big")
    t = data[8] & 0x0f
    t = t & 0xFF
    audio_5 += t.to_bytes(1, byteorder="big")
    audio_5 = struct.unpack("<H", audio_5)
    audio_5 = audio_5[0]

    return (audio_0, audio_1, audio_2, audio_3, audio_4, audio_5)


def process_data_vdd(data):
    global g_log_vdd
     # print("vdd, vbat")
     # dump_data(data)
    
     # Epoch Time
    ts = struct.unpack("<I", data[2:6])
    ts = ts[0]
     # serial number within 1s
    vdd = struct.unpack("<f", data[6:10])
    vbat = struct.unpack("<f", data[10:14])
    vdd = vdd[0]
    vbat = vbat[0]
    print("timestamp = %d" % ts)
    g_log_vdd.extend((ts, vdd, vbat))


def process_data_version(data):
    print("version")
     # dump_data(data)
    ver = data[2]
     # print(ver)


def process_data(data):
    id = data[0]
    if id == 0x00:
        process_data_acc(data)
    elif id == 0x01:
        process_data_ir(data)
    elif id == 0x02:
        process_data_ir(data)
    elif id == 0x04:
        process_data_audio(data)
    elif id == 0x05:
        process_data_vdd(data)
    elif id == 0xff:
        process_data_version(data)
    else:
        print("impossible 2")
        print(id)
        exit(1)


def first_ts(num, g_badges):
    global g_badges
    global g_start
    global g_new
    g_new = g_badges[num]->[g_log_acc]->[0]->[0]
    if g_start < g_new:
        g_start = g_new


def main(f):
    state = "STATE_SEARCH_HEADER"
    count = 0
    through = 0

    while True:
        d = f.read(1)
        if len(d) == 0:
            break
        
         # print(d)
         # count = count + 1
         # if count > 10:
         #   break
         # print(d, end="")
        
        if state == "STATE_SEARCH_HEADER":
            if d == b"\xAA":
                state = "STATE_SEARCH_HEADER_DOUBLE"
        elif state == "STATE_SEARCH_HEADER_DOUBLE":
            if d == b"\xAA":
                data = b"" 
                state = "STATE_PROCESS_RECORD"
            else:
                state = "STATE_SEARCH_HEADER"
        elif state == "STATE_PROCESS_RECORD":
            data += d
            if d == b"\x55":
                state = "STATE_PROCESS_RECORD_WITH_TRAILER"
        elif state == "STATE_PROCESS_RECORD_WITH_TRAILER":
            if d == b"\x55":
                state = "STATE_SEARCH_HEADER"
                process_data(data)
            else:
                state = "STATE_PROCESS_RECORD"
                data += d
        else:
            print("impossible!!!: " + state)
            exit(1)
    f.close


num = len(args) - 1
for i in range(num):
    f = open(args[i + 1], 'rb')
    main(f)
     # print(g_log_acc)
     # print(g_log_ir)
     # print(g_log_audio)
     # print(g_log_vdd)
    g_badges.extend(g_badge)

    g_start = 0
    find_ts(i, g_badges)

     # print(g_badges)
