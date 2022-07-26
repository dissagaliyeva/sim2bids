import os
from incf.convert import convert

IDS = {}
start = 1


def create_uuid():
    global start

    if start in IDS.keys():
        start += 1

    new = f'0{start}' if start < 10 else start
    new = 'sub-' + new
    
    IDS[start] = new
    return new


def reset_index():
    global start, IDS
    start = 1
    IDS = {}

