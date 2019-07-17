'''
Created on 3 Jun 2019

@author: fy65
'''
from contextlib import contextmanager
import socket
import time
import sys
import struct

@contextmanager
def socketcontext(*args, **kw):
    s = socket.socket(*args, **kw)
    try:
        yield s
    finally:
        s.close()
        
@contextmanager
def connectioncontext(arg):
    print ('waiting for a connection')
    conn, addr = arg.accept()
    try:
        yield conn, addr
    finally:
        conn.close() 
        
def recv_basic(the_socket):
    '''basic receive parsing received data stream until no more data
    '''
    total_data=[]
    while True:
        data = the_socket.recv(8192)
        if not data: break
        total_data.append(data)
    return ''.join(total_data)
    
def recv_timeout(the_socket,timeout=2):
    '''parsing received data stream with timeout, default time out is 2 seconds
    '''
    the_socket.setblocking(0)
    total_data=[];data='';begin=time.time()
    while 1:
        #if you got some data, then break after wait sec
        if total_data and time.time()-begin>timeout:
            break
        #if you got no data at all, wait a little longer
        elif time.time()-begin>timeout*2:
            break
        try:
            data=the_socket.recv(8192)
            if data:
                total_data.append(data)
                begin=time.time()
            else:
                time.sleep(0.1)
        except:
            pass
    return ''.join(total_data)

def recv_end(the_socket, End='\n'):
    '''parsing received data stream terminated by specified end mark
    '''
    total_data=[];data=''
    while True:
            data=the_socket.recv(8192)
            if End in data:
                total_data.append(data[:data.find(End)])
                break
            total_data.append(data)
            if len(total_data)>1:
                #check if end_of_data was split
                last_pair=total_data[-2]+total_data[-1]
                if End in last_pair:
                    total_data[-2]=last_pair[:last_pair.find(End)]
                    total_data.pop()
                    break
    return ''.join(total_data)

def recv_size(the_socket):
    '''parsing received message with length header of 4 bytes
    '''
    #data length is packed into 4 bytes
    total_len=0;total_data=[];size=sys.maxint
    size_data=sock_data='';recv_size=8192
    while total_len<size:
        sock_data=the_socket.recv(recv_size)
        if not total_data:
            if len(sock_data)>4:
                size_data+=sock_data
                size=struct.unpack('>i', size_data[:4])[0]
                recv_size=size
                if recv_size>524288:recv_size=524288
                total_data.append(size_data[4:])
            else:
                size_data+=sock_data
        else:
            total_data.append(sock_data)
        total_len=sum([len(i) for i in total_data ])
    return ''.join(total_data)

def send_size(the_socket, data):
    '''send message packed with message length header of 4 bytes
    '''
    the_socket.sendall(struct.pack('>i', len(data))+data)

def send_end(the_socket, data, End='\n'):
    '''send message which terminated by specified end mark
    '''
    the_socket.sendall(data+End)
