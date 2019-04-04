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
            fileNamePath = PureWindowsPath(msg_dict['filename'])
        filesize = msg_dict['filesize']
        if os.path.isfile(fileNamePath):
            f = open(fileNamePath,'wb')
        else:
            pathDir = fileNamePath.replace(('/' + fileName), '')
            if not os.path.exists(pathDir):
                os.makedirs(pathDir)
            f = open(fileNamePath, 'wb')
        self.request.send(b'200 ok')
        receivesize = 0
        while receivesize < filesize:
            data = self.request.recv(1024)  #不能加strip()
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
        if os.path.isfile(filename):
            filesize = os.stat(filename).st_size
            f = open (filename,'rb')
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

    def handle(self):
        while True:
            self.data = self.request.recv(1024).strip()
            if self.data:
                msg_dict = json.loads(self.data.decode('utf-8'))
                cmd = msg_dict['action']
                if hasattr(self,'cmd_%s'%cmd):
                    func = getattr(self,'cmd_%s'%cmd)
                    func(msg_dict)
            else:
                print("nothing is received...")    
                self.request.send(b'nothing')



if __name__ == '__main__':
    host,port = '127.0.0.1',10000
    server = socketserver.ThreadingTCPServer((host,port),FtpHandler)
    print("run")
    server.serve_forever()
