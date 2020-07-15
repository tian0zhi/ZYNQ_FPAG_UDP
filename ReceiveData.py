import threading
import struct
import socket
import time
import inspect
import ctypes

def _async_raise(tid, exctype):
	"""raises the exception, performs cleanup if needed"""
	tid = ctypes.c_long(tid)
	if not inspect.isclass(exctype):
		exctype = type(exctype)
	res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
	if res == 0:
		raise ValueError("invalid thread id")
	elif res != 1:
		# """if it returns a number greater than one, you're in trouble,
		# and you should call it again with exc=NULL to revert the effect"""
		ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
		raise SystemError("PyThreadState_SetAsyncExc failed")
 
 
def stop_thread(thread):# 杀死进程的一种方法
	_async_raise(thread.ident, SystemExit)


def UDPServer(li):# 接收从FPGA发给PC的数据
	local_ip = '192.168.1.23' #192.168.1.23
	local_port = 8080
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # 开启udp服务器
	s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1100*1024)# 设置缓冲区大小1024*1024为1M
	s.bind((local_ip, local_port))# 监听8080端口
	print('端口绑定成功!\n')
	i = 0
	# data,addr = s.recvfrom(1100)
	# while len(data) > 2:
		# if len(data)>1000:
	while i/1024 != 4:# 数字4为4个连续用示波器软件保存的数据长度，可以适当更改，不要太大，4约为9.3M文本。
		data,addr = s.recvfrom(1100*1024)
		# li.append(data)
		# print(i+1)
		# i = i + 1
		if len(data)>1000:
			i = i + 1
			print(i)
			li.append(data)
			# f = open('save.txt' , 'a')  # 新建本地文件存储
			# data_tuple = struct.unpack('>BL512H',data)
			# adc_data=data_tuple[3:]#提取adc数据
			# for k in adc_data:
				# f.write(str(hex(k))[2:]+' ')
			# print(data)
			# print(len(data))
			# f.close()
		# data,addr = s.recvfrom(1100)
	# print('接收到的数据太短，UDPServer线程退出!!\n')


def UDPEnquire():# PC发送给FPGA的询问数据
	FPGA_ip = '192.168.1.11'
	FPGA_port = 8080
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)#建立客户端面向网络的无连接套接字
	# sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	ask_order=struct.pack('>BL',0x28,0x00010001)#询问命令
	control_order = struct.pack('>BL6B8B', 0x28, 0x00010002, 0x00, 0x0a, 0x35, 0x00, 0x01, 0x02, 0x00, 0x00, 0x00, 0x01,0x00, 0x08, 0x00, 0x00)
	while True:
		sock.sendto(ask_order,(FPGA_ip,FPGA_port))#发送询问命令给FPGA
		# print('发送询问命令给FPGA')
		sock.sendto(control_order, (FPGA_ip, FPGA_port))  # 发送控制命令给FPGA
		print('发送给FPGA')
		time.sleep(0.1)



def main2(li):# 无用的测试代码
	t1 = threading.Thread(target=UDPServer,args = (li,))
	t2 = threading.Thread(target=UDPEnquire)
	
	t1.setDaemon(True)   #把子进程设置为守护线程，必须在start()之前设置
	t2.setDaemon(True)   #把子进程设置为守护线程，必须在start()之前设置
	
	t1.start()
	t2.start()
	char = input('输入阻塞!!\n')
	print("end")



if __name__ == '__main__':
	li = []
	t1 = threading.Thread(target=UDPServer,args = (li,))
	t2 = threading.Thread(target=UDPEnquire)
	
	t1.setDaemon(True)   #把子进程设置为守护线程，必须在start()之前设置
	t2.setDaemon(True)   #把子进程设置为守护线程，必须在start()之前设置
	
	t1.start()
	t2.start()
	char = input('输入阻塞!!\n')
	print("end")
	
	# li = []
	# t = threading.Thread(target=main2,args = (li,))
	# t.start()
	# t.join()
	stop_thread(t2)# 杀死t2线程
	print('解析数据!\n')
	f = open('save.txt' , 'a')  # 新建本地文件存储
	for data in li:
		if len(data)>1000:
			data_tuple = struct.unpack('>BL512H',data)
			adc_data=data_tuple[2:]#提取adc数据
			for k in adc_data:
				f.write(str(hex(k))[2:]+' ')
	f.close()
