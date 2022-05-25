#!/usr/bin/env python
# coding: utf-8
'''
@File   :smartconfig.py
@Author :youxinweizhi
@Date   :2021/12/23
@Github :https://github.com/youxinweizhi
'''
import network
import socket
import utime
import wificonfig
from machine import reset

def help():
	print("""
		from smartconfig import SMARTCONFIG
		wlan=SMARTCONFIG()
		wlan.start()
	""")

class SMARTCONFIG(object):
	def __init__(self) -> None:
		self.AP_MODE = 0
		self.STA_MODE = 1
		self.STATION_CONNECTED = network.STAT_GOT_IP
		self.STA_CONFIG_FILENAME = 'sta_config.py'
		self.STA_CONFIG_IMPORT_NAME = self.STA_CONFIG_FILENAME.split('.')[0]
		self.INTERVAL_FROM_1970_TO_2000 = 946_656_000 # in second
		self.connect_code = {
				network.STAT_IDLE: "network idle",
				network.STAT_CONNECTING: "",
				network.STAT_GOT_IP: "Connected",
				network.STAT_NO_AP_FOUND: "could not found ap",
				network.STAT_WRONG_PASSWORD: "wrong password given",
				network.STAT_BEACON_TIMEOUT: "beacon timeout",
				network.STAT_ASSOC_FAIL: "assoc fail",
				network.STAT_HANDSHAKE_TIMEOUT: "handshake timeout"
			}

	@staticmethod
	def set_sta_status(active:bool):
		station = network.WLAN(network.STA_IF)
		station.active(active)

	#开启配网模式
	def start(self,essid=None, password='', timeout_sec=600):
		utime.sleep_ms(1000)
		station = network.WLAN(network.STA_IF)
		station.active(False)
		station.active(True)
		using_smartconfig = False
		print("\nConnecting to network...")

		if not station.isconnected():
			if not essid:
				try:
					sta_config = __import__(self.STA_CONFIG_IMPORT_NAME)
					essid = sta_config.essid
					password = sta_config.password
				except ImportError:
					print('Start smartconfig...')
					wificonfig.start()
					while not wificonfig.success():
						utime.sleep_ms(500)

					essid, password, sc_type, token = wificonfig.info()
					using_smartconfig = True
					print(f'-- Got info\n    ssid={essid}\n    password={password}\n    type={sc_type}\n    token={token}')

			station.connect(essid, password)
			retry_count = 0
			while not station.isconnected():
				if timeout_sec > 0:
					if retry_count >= timeout_sec * 2:
						break

				result_code = station.status()
				if result_code == network.STAT_IDLE or\
					result_code == network.STAT_GOT_IP or\
					result_code == network.STAT_NO_AP_FOUND or\
					result_code == network.STAT_WRONG_PASSWORD:
					break
				elif result_code == network.STAT_CONNECTING:
					pass

				retry_count += 1
				utime.sleep_ms(500)

		status_code = station.status()
		print(self.connect_code[status_code])
		print(station.ifconfig())

		if status_code == self.STATION_CONNECTED and using_smartconfig:
			self.write_config(essid, password)
			self.send_smartconfig_ack(station.ifconfig()[0])

		return status_code

	#配网应答
	def send_smartconfig_ack(self,local_ip):
		udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		token = wificonfig.info()[3].to_bytes(1, 'little') + self.get_mac_address()
		port = 10000

		if wificonfig.info()[2] == wificonfig.TYPE_ESPTOUCH:
			token += self.inet_pton(local_ip)
			port = 18266

		for _ in range(30):
			utime.sleep_ms(100)
			try:
				udp.sendto(token, ('255.255.255.255', port))
			except OSError:
				pass
		print('ack was sent...')

	#查看wif连接状态
	@staticmethod
	def isconnected():
		station = network.WLAN(network.STA_IF)
		return station.isconnected()

	#字符串 IP 地址转字节串
	def inet_pton(self,ip_str):
		result = b''
		ip_seg = ip_str.split('.')
		for seg in ip_seg:
			result += int(seg).to_bytes(1, 'little')
		return result

	#获取mac地址
	@staticmethod
	def get_mac_address():
		station = network.WLAN(network.STA_IF)
		return station.config('mac')

	#保存配网信息
	def write_config(self,essid, password):
		with open(self.STA_CONFIG_FILENAME, 'w') as output:
			output.write(
f'''# automatic generated file
essid = '{essid}'
password = '{password}'
'''
			)

	#删除配网信息
	def delete_config(self):
		import os
		try:
			os.remove(self.STA_CONFIG_FILENAME)
			reset()
		except:
			print('error: delete config faild')