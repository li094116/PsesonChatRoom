import select
import socket
import queue

from threading import Thread
import datetime

# create a TCP/IP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(False)
# bind the socket to the port
server_address = ("127.0.0.1", 12345)
print("server is running...")
server.bind(server_address)
server.listen(5)
# sockets from which we expect to read
inputs = [server]

userlist = []

#sockets to which we expecto to write
outputs = []
# outgoing message queues 
message_queues = {}
# set timeout for select() will waiting time
timeout = 5

#Server的命令线程，用户获取服务器对客户的一些操作
def command():
	print("command is start!")
	while True:
		server_speak = input()
		# 执行踢出用户操作
		for read in inputs[1:len(inputs)]:
			for user in userlist:
				try:
					if "KICK" in server_speak and str(user, encoding="UTF-8")[2:] in server_speak:
						read.send(bytes("kill you!", encoding="UTF-8"))
						inputs.remove(read)
						for otherread in inputs[1:]:
							otherread.send(bytes((str(user, encoding="UTF-8") + "kill"), encoding="UTF-8"))
							otherread.send(bytes((str(user, encoding="UTF-8") + "  " + "leave the room"), encoding="UTF-8"))
						userlist.remove(user)
						print(str(user, encoding="UTF-8") + "is died")
						server_speak = None
				except:
					pass
		# 踢出用户后不执行以下操作重新执行循环
		if server_speak == None:
			continue
		# 显示当前在线用户列表
		if "LIST_USER" in server_speak:
			for user in userlist:
				print(str(user, encoding="UTF-8")[2:])
		# 关闭所有连接，并关闭服务器
		elif "EXIT" in server_speak:
			for read in inputs[1:len(inputs)]:
				read.send(bytes("kill you!", encoding="UTF-8"))
				inputs.remove(read)
			server.close()
		# 显示版权
		elif "HELP" in server_speak:
			print("Copyright©2020 Yuxi Li All rights reserved.")
		else:
			# 遍历连接列表实现服务器广播消息
			for read in inputs[1:]:
				read.send(bytes(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " " + "Server:" + " " + \
								server_speak, encoding="UTF-8"))
#Server命令线程
if (__name__ == "__main__"):
	receive = Thread(target=command)
	receive.start()

#遍历inputs进行对客户端的信息进行转发操作
while inputs:
	# wait for at least one of the sockets to be ready for processing
	print("waiting for the next event")
	readable, writable, exceptional = select.select(inputs, outputs, inputs)
	
	if not (readable or writable or exceptional):
		print("timeout....")
		continue
	# handle inputs
	# 判断当前是否有消息在消息队列中
	for s in readable:
		if s is server:
		# A "readable" server socket is ready to accept a connection
			conn, addr = s.accept()
			print("new connection from", addr)
			conn.setblocking(False)
			inputs.append(conn)
			# give the connection a queue for data we want to send
			message_queues[conn] = queue.Queue()
		else:
			try:
				data = s.recv(32768)
				# 如果有同名用户，回把当前在线用户挤掉
				if data in userlist:
					reuserindex = userlist.index(data)
					inputs[reuserindex + 1].send(bytes("kill you!", encoding="UTF-8"))
					inputs.remove(inputs[reuserindex + 1])
					for read in inputs[1:]:
						for i in userlist:
							read.send(i)
					continue
			except ConnectionResetError:
				# 当客户端断开连接删除连接列表的对象并删除对应的用户名把新的用户列表返回给还在线的用户
				try:
					reuser = inputs.index(s)
				except:
					continue
				inputs.remove(s)
				deluser = userlist[reuser-1]
				while deluser in userlist:
					userlist.remove(deluser)
				for read in inputs[1:len(inputs)]:
					read.send(bytes((str(deluser, encoding="UTF-8") + "kill"), encoding="UTF-8"))
				deluser = None
				continue
			# 遍历连接列表对用户实现信息的转发
			for read in inputs[1:len(inputs)]:
				# 判断接收的是用户名还是消息，用户名执行if，消息执行else进行转发
				if (str(data, encoding="UTF-8") not in userlist) and ("@@" in str(data, encoding="UTF-8")):
					userlist.append(data)
					userlist = sorted(set(userlist), key=userlist.index)
					for i in userlist:
						read.send(i)
				else:
					for i in userlist:
						read.send(i)
					read.send(data)
			if data:
				# A readable client socket has data
				# print("receved {0} from {1}".format(data, s.getpeername()))
				message_queues[s].put(data)
				# add output channel for response
				if s not in outputs:
					outputs.append(s)
			else:
				# interpret empty result as closed connection
				# print("closing {0} after reading no data".format(addr))
				# stop listening for input on the connection
				if s in outputs:
					outputs.remove(s)
				try:
					inputs.remove(s)
				except:
					continue
				s.close()

				# remove message queue
				del message_queues[s]
	#handle outputs
	for s in writable:
		try:
			next_msg = message_queues[s].get_nowait()
		except :
			# no message waiting so stop checking for writability
			outputs.remove(s)
		else:
			pass
			# print("sending {0} to {1}".format(next_msg, s.getpeername()))
	#handle "exceptional conditions"
	for s in exceptional:
		# print("handing exceptional condition for {} ".format(s.getpeername()))
		# stop listening for input on the connection
		inputs.remove(s)
		if s in outputs:
			outputs.remove(s)
		s.close()
		# remove message queue
		del message_queues[s]


