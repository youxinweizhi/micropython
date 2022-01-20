#!/usr/bin/env python
# coding: utf-8
'''
@File   :zbx_sender.py
@Author :youxinweizhi
@Date   :2019/7/9
@Github :https://github.com/youxinweizhi
'''

import socket
import struct
import json

class ZBXSENDER():
    def __init__(self,server="127.0.0.1",port=10051):
        self.server=server
        self.port=port
        self.timeout=5
    def make_data(self, host, key, value, clock=None):
        sender_data = {
            "request": "sender data",
            "data": [{
                'host': host,
                'key': key,
                'value': value,
            }],
        }
        to_send = json.dumps(sender_data)
        return to_send

    def send(self,mydata):
        # socket.setdefaulttimeout(self.timeout)
        data_length = len(mydata)
        data_header = struct.pack('q', data_length)
        data_to_send = b'ZBXD\1' + data_header + (mydata.encode('utf-8'))
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.server, self.port))
            sock.send(data_to_send)
        except Exception as err:
            err_message = u'Error talking to server: %s\n' %str(err)
            print(err_message)

        response_header = sock.recv(5).decode()
        if not response_header == 'ZBXD\1':
            err_message = u'Invalid response from server. Malformed data?\n---\n%s\n---\n' % str(mydata)
            print(err_message)

        response_data_header = sock.recv(8)
        response_data_header = response_data_header[:4]
        response_len = struct.unpack('i', response_data_header)[0]
        response_raw = sock.recv(response_len)
        print(response_raw)
        sock.close()

if __name__ == '__main__':
    z=ZBXSENDER(server="192.168.254.201")
    mydata=z.make_data("server","test_trap_1","16")
    z.send(mydata)