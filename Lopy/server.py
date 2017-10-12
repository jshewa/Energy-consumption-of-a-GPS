import socket

def tcp():
    TCP_IP = 'localhost'

    TCP_PORT = 5005

    BUFFER_SIZE = 20 
    s= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind(('192.168.4.1', TCP_PORT))
    print('waiting for connection')
    s.listen(1)

    conn, addr = s.accept()

    print ('Connection address:', addr)

    while(1):
        data= conn.recv(BUFFER_SIZE)
        data= data.decode('utf-8')
        if (not data):
            break
        print('recieved data:',data)
        conn.send(data)
    conn.close() 
