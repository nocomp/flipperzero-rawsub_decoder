#!/usr/bin/env python3
import argparse
import sys
import os

# The code of this function is based on Flipper file plotter by ShotokanZH (https://github.com/ShotokanZH/flipper_sub_plotters_comparers/blob/master/plotall.py)
def convert_file_to_array(f):
    y = []
    while True:
        line = f.readline()
        if not line:
            break
        if line.startswith("RAW_Data: "):
            for d in line.split(" ")[1:]:
                d = int(d)
                y.append(d)
                #print(f"{d}")
    return y

def get_burst(y):
    #print(f"{y}")
    burst = []
    burst_found = False
    # search burst
    for v in y:
        #print(f"get_burst: analyzing {v}")
        if v >= 1700 and v < 1800:
            burst.append(v)
            burst_found = True
            #print(f"Found beginning of a burst: {v}")
            continue
        if burst_found and v < -1000000:
            #print(f"Found end of burst: {v}")
            break
        if burst_found:
            burst.append(v)
            #print(f"Append {v}")
    return burst

def decode_burst(y):
    data = []
    preamble = []
    preamble_ended = False
    symbols = []
    symbols_split = []
    for v in y:
        if v <= -4000 and v > -5000:
            preamble_ended = True
            preamble.append(v)
            continue
        if not preamble_ended:
            preamble.append(v)
        if preamble_ended:
            symbols.append(v)

    print(f"Preamble = {preamble}")
    print(f"Symbols = {symbols}")

    for v in symbols:
        decode_symbol(symbols_split, v)

    print(f"Symbols_split = {symbols_split}")

    l = len(symbols_split)
    print(f"Length Symbols = {l}")
    odd_len = False
    if l % 2 != 0:
        odd_len = True
        print(f"Odd number of symbols: {l}...")
        #raise BaseException(f"Odd number of symbols: {l}")

    for v in range(int(l / 2)):
        index = v * 2
        a = symbols_split[index]
        b = symbols_split[index+1]
        #print(f"{a} {b}")
        data.append(decode_manchester(a, b))
    if odd_len:
        last = symbols[-1]
        print(f"Last symbol {last} was not used...")

    print(f"Data = {data}")
    print(f"Length data = {len(data)}")
    return data

def decode_symbol(a_list, v):
    if v >= 350 and v < 450:
        a_list.append(1)
        #print(f"Symbol {v} converted to 1")
    elif v <= -350 and v > -450:
        a_list.append(0)
        #print(f"Symbol {v} converted to 0")
    elif v >= 700 and v < 900:
        a_list.append(1)
        a_list.append(1)
        #print(f"Symbol {v} converted to 11")
    elif v <= -700 and v > -900:
        a_list.append(0)
        a_list.append(0)
        #print(f"Symbol {v} converted to 00")
    else:
        raise BaseException(f"Symbol {v} unknown")

def decode_manchester(a, b):
    if a == 0 and b == 1:
        return 0
    elif a == 1 and b == 0:
        return 1
    else:
        raise BaseException(f"Symbols {a} {b} incompatible with Manchester coding")

def convert_to_bytes(data):
    # Little or Big endian ??
    pass

def main():
    parser = argparse.ArgumentParser(description="Flipper file RAW analyzer based on Manchester decoding")
    parser.add_argument(
        "filename", help=".sub file to be analyzed", type=str)
    args = parser.parse_args()
    try:
        for fname in args.fname:
            with open(fname, "r") as f:
                y = convert_file_to_array(f)
                b = get_burst(y)
                print(f"Burst found: {b}")
                data = decode_burst(b)
                data_bytes = convert_to_bytes(data)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(locals())
        print("ERROR:", e)
        print(exc_type, fname, exc_tb.tb_lineno)


if __name__ == '__main__':
    main()
