import socket
import os
import datetime
import stat
import json
import time

class FtpClient(object):
    def __init__(self):
        self.client = socket.socket()
        self.lastFilemtimeMax = 0.0

    def connect( self,ip,port ):
        self.client.connect((ip,port))

    def interactive(self):
        while True:
            fileName = "/Users/papi/Desktop/clientFile"
            # 判断文件夹是否被修改（根据文件夹修改时间判断）
            if self.lastFilemtimeMax != os.path.getmtime(fileName):
                cmd = ("put " + fileName).strip()
                if len(cmd)==0:continue
                cmd_str = cmd.split()[0]
                if hasattr(self,'cmd_%s'%cmd_str):
                    func = getattr(self,'cmd_%s'%cmd_str)
                    func(cmd)     
            time.sleep(10)

    def cmd_put( self,*args ):
        cmd_split = args[0].split()
        if len(cmd_split) > 1:
            filename = cmd_split[1]
            # 获取文件夹大小
            print(os.path.getsize(filename))
            # 判断是否是文件夹
            if os.path.isdir(filename):
                for root, dirs, files in os.walk(filename):
                    self.lastFilemtimeMax = os.path.getmtime(filename)
                    for fname in files:
                        if fname == ".DS_Store": continue
                        time.sleep(1)
                        fname_path = root + '/' + fname
                        if os.path.isfile(fname_path):
                            filesize = os.stat(fname_path).st_size
                            serverFilePath = fname_path.replace('clientFile', '随便文件夹')
                            msg_dic = {
                                'action':'put',
                                'fileNamePath':serverFilePath,
                                'filesize':filesize,
                                'fileName':fname
                            }
                            self.client.send(json.dumps(msg_dic).encode('utf-8'))
                            server_response = self.client.recv(1024)
                            if server_response == b'200 ok':
                                f = open(fname_path, 'rb')
                                for line in f.readlines():
                                    self.client.send(line)
                                else:
                                    print(fname_path,'upload success...')
                                    f.close()
                            else:
                                print("error")
            else:
                print(filename,'is not exist')


    def cmd_get( self ,*args):
        cmd_split = args[0].split()
        if len(cmd_split) > 1:
            filename = cmd_split[1]
            msg_dic = {
                'action': 'get',
                'filename': filename
            }
            if os.path.isfile(filename):
                f = open(filename+'.get','wb')
            else:
                f = open(filename,'wb')
            self.client.send(json.dumps(msg_dic).encode('utf-8'))
            self.data = self.client.recv(1024)
            msg_dic = json.loads(self.data.decode('utf-8'))
            filesize = msg_dic['filesize']
            self.client.send(b'200 ok')
            receivesize = 0
            while receivesize < filesize:
                data = self.client.recv(1024)
                f.write(data)
                lenth = len(data)
                receivesize += lenth
            else:
                print(filename,'dowloaded sucess....')
                f.close()

    # 根据时间格式和unix时间参数，返回对应时间字符串
    def get_time_date(self, dateFormate, unixTime):
        return time.strftime(dateFormate, time.localtime(unixTime))

if __name__ == '__main__':
    ftp = FtpClient()
    ftp.connect('127.0.0.1',10000)
    ftp.interactive()
    