import logging
import pandas
import csv
import time
import socket
import json
from process.network import SocketClient
from process.sql_helper import SqlHelper
from process.location import Location
from process.config import load_config

measure_data_dict = {}
anchors_groups = {}
label_type = {}


def load_tag_config():
    global label_type
    df = pandas.read_excel('config/label.xlsx')
    for col_name, col_data in df.items():
        if isinstance(col_name, int):
            label_type[col_name] = int(col_data[0])


def load_anchor_config():
    global anchors_groups
    dfs = pandas.read_excel('config/anchor.xlsx', sheet_name=None)
    for key, df in dfs.items():
        anchors_groups[key] = {}
        anchors_groups[key]['scenario'] = int(df.loc[0, 'scenario'])
        anchors_groups[key]['level'] = int(df.loc[0, 'level'])
        anchors_groups[key]['anchors'] = []
        for col_name, col_data in df.items():
            if isinstance(col_name, int):
                anchor = {}
                anchor['id'] = col_name
                anchor['x'] = col_data.values[0]
                anchor['y'] = col_data.values[1]
                anchor['z'] = col_data.values[2]
                anchors_groups[key]['anchors'].append(anchor)
    print(anchors_groups)

load_tag_config()
load_anchor_config()


def process_measure_data(measure_data,sc):

    global measure_data_dict
    asctime = measure_data.asctime
    label_address = measure_data.label_address
    node_address = measure_data.node_address
    frame_num = measure_data.frame_num
    distance = measure_data.distance

    print('{asctime}:\tlabel:{label_address}\t<--->\tnode:{node_address}\t[frame:{frame_num}]:\tdistance:{distance}'.format(
        asctime=asctime,
        label_address=label_address,
        node_address=node_address,
        frame_num=frame_num,
        distance=distance))
    logging.debug('{asctime}:\tlabel:{label_address}\t<--->\tnode:{node_address}\t[frame:{frame_num}]:\tdistance:{distance}'.format(
        asctime=asctime,
        label_address=label_address,
        node_address=node_address,
        frame_num=frame_num,
        distance=distance))

    # new label join
    if label_address not in measure_data_dict.keys():
        measure_data_dict[label_address] = []
    # new frame
    elif measure_data_dict[label_address][0].frame_num != frame_num:
        # packet loss
        if len(measure_data_dict[label_address]) < 4:
            logging.warning('label {label_address} packet loss'.format(
                label_address=label_address))
        # clean res data list
        measure_data_dict[label_address] = []
    # save measure data.
    measure_data_dict[label_address].append(measure_data)

    # cal position
    if len(measure_data_dict[label_address]) >= 4:
        if res := cal_position(label_address):
            process_res(res[0], res[1], res[2], res[3], res[4], res[5], sc)


def process_res(x, y, frame_num, label_address, scenario, level , sc):
    global label_type
    with open("res.csv", mode="a", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [time.asctime(), frame_num, label_address, x, y])
    # config = load_config()
    # ip = config['server_ip']
    # port = config['server_port']
    role = 1
    if label_address in label_type.keys():
        role = label_type[label_address]
    try:
        msg_dict = {
            'packet_header': 'UWB',
            'asc_time': time.strftime("%H:%M:%S %d-%m-%Y", time.localtime()),
            'role': int(role),
            'label_id': label_address,
            'scenario': scenario,
            'level': level,
            'x': x,
            'y': y,
            'z': 0.5
        }
        msg = json.dumps(msg_dict)
        logging.debug(msg)
        msg=msg+'\r\n'
        print(msg)
        # sc = SocketClient(ip, port)
        sc.send(msg)
    except socket.error as err:
        print(err)
    except Exception as e:
        logging.error(e)


def cal_position(label_address: int):
    global anchors_groups

    # get all address list
    address_list_all = get_address_list(label_address)

    # group addresses
    address_list_groups = {}
    for key , value in anchors_groups.items():
        address_list_groups[key] = []
        for anchor in value['anchors']:
            if anchor['id'] in address_list_all:
                address_list_groups[key].append(anchor['id'])

    # select the group with a large number
    address_list = []
    group_str = ''
    for key , value in anchors_groups.items():
        if len(address_list_groups[key]) > len(address_list):
            address_list = address_list_groups[key]
            group_str = key
    
    if len(address_list) < 4:
        return None
    elif len(address_list) >= 4:
        address_list = get_near_4_address(address_list, label_address)

    frame_num = measure_data_dict[label_address][0].frame_num
    measure_data_list = measure_data_dict[label_address]

    for address in address_list:
        if address == 0:
            return None

    location_helper = Location()

    distance_list = []
    anchor_position_list = []

    for address in address_list:
        for measure_data in measure_data_list:
            if measure_data.node_address == address:
                distance_list.append(measure_data.distance / 100)
                break
            
    for address in address_list:
        for anchor in anchors_groups[group_str]['anchors']:
            if anchor['id'] == address:
                anchor_position_list.append(
                    [anchor['x'], anchor['y'], anchor['z']])
                break
    location_helper.set_distances(distance_list)
    location_helper.set_anthor_coor(anchor_position_list)

    [x, y] = location_helper.trilateration_4()

    return [x, y, frame_num, label_address, anchors_groups[group_str]['scenario'], anchors_groups[group_str]['level']]



def get_address_list(label_address):
    address_list = []
    for measure_data in measure_data_dict[label_address]:
        address_list.append(measure_data.node_address)
    return address_list


def get_near_4_address(address_list, label_address):
    global measure_data_dict
    res = []
    index = 0
    distance_list = []
    for address in address_list:
        for measure_data in measure_data_dict[label_address]:
            if measure_data.node_address == address:
                distance_list.append(measure_data.distance)
                break
    for i in range(4):
        index = -1
        d = 0xfff
        for j in range(len(address_list)):
            if address_list[j] not in res:
                if distance_list[j] < d:
                    index = j
                    d = distance_list[j]
        if index >= 0:
           res.append(address_list[index])
    return res
