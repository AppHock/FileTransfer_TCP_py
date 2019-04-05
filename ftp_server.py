import socketserver
import os
import json
from pathlib import Path, PureWindowsPath
import platform # 判断当前系统

class FtpHandler(socketserver.BaseRequestHandler):

    def cmd_put( self,*args ):
        msg_dict = args[0]
        # mac文件路劲转window路劲
        fileNamePath = msg_dict['fileNamePath']
        fileName = msg_dict['fileName']
        if (platform.system() == 'Windows'):
            # 判断当前系统，去获取文件夹路劲
            # 添加C盘路劲前缀
            fileNamePath = "c:" + fileNamePath
            fileNamePath = fileNamePath.replace("/", '\\')
            # PureWindowsPath(fileNamePath)
            
        filesize = msg_dict['filesize']
        
        if os.path.isfile(fileNamePath):
            f = open(fileNamePath,'wb')
        else:
            pathDir = fileNamePath.replace(('\\' + fileName), '')
            if not os.path.exists(pathDir):
                # 判断pathDir文件夹路劲是否存在，不存在新建文件夹
                os.makedirs(pathDir)
            f = open(fileNamePath, 'wb')
        self.request.send(b'200 ok')
        receivesize = 0
        while receivesize < filesize:
            data = self.request.recv(1000000)  #不能加strip()
            print(len(data))
            if not data:
                print("nothing is received...")
                break
            f.write(data)
            receivesize += len(data)
        else:
            f.close()
            print('file has uploaded')

    def cmd_get(self,*args):
        msg_dic = args[0]
        filename = msg_dic['filename']
        fileNamePath = filename
        if (platform.system() == 'Windows'):
            # 判断当前系统，去获取文件夹路劲
            # 添加C盘路劲前缀
            fileNamePath = "c:" + filename
            fileNamePath = fileNamePath.replace("/", '\\')
            filesize = 0
        if os.path.isfile(fileNamePath):
            filesize = os.stat(fileNamePath).st_size
            f = open (fileNamePath,'rb')
            msg_dic = {
                'filesize':filesize
            }
            self.request.send(json.dumps(msg_dic).encode('utf-8'))
            data = self.request.recv(1024)
            for line in f:
                self.request.send(line)
            else:
                print(filename,'dowloaded success...')
                f.close()
        else:
            print('未找到路劲')
    def handle(self):
        while self.isConnected:
            self.data = self.request.recv(1024).strip()
            if self.data:
                msg_dict = json.loads(self.data.decode('utf-8'))
                cmd = msg_dict['action']
                if hasattr(self,'cmd_%s'%cmd):
                    func = getattr(self,'cmd_%s'%cmd)
                    func(msg_dict)
            else:
                print("nothing is received...")
                break

    def finish(self):
        print("finished")
        self.isConnected = False
    
    def setup(self):
        print("setup")
        self.isConnected = True

    def server_close(self):
        print('socket close')


if __name__ == '__main__':
    host,port = '192.168.2.205',10000
    server = socketserver.ThreadingTCPServer((host,port),FtpHandler)
    print("run")
    server.serve_forever()
    
