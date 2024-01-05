import socket
import struct
import ssl
import sys
import time
import argparse
import itertools
import random
import os
import datetime

from concurrent.futures import ThreadPoolExecutor


class Tools:
    def __init__(self):
        pass
    def convert_string_to_bytes(self, string):
        bytes = b''
        for i in string:
            bytes += struct.pack("B", ord(i))
        return bytes
    
    def parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("send_hostname", help='Hostname you want to transmit')
        parser.add_argument("-f", "--fuzz", type=str, nargs="*", default=["fuzz", "word_list.txt"], help='ex. [ (@@@word@@@ in Templete data) (word_list_filepath to input contents to @@@word@@@) ... ]')
        parser.add_argument("-p", "--port", nargs=3, default=["https","tcp", 443], help='Transmission Protocol and Port number (ex.) http tcp(or udp) 80')
        parser.add_argument("-t", "--intervaltime", type=float, default=1.2, help='interval time of transmitting')
        parser.add_argument("-mt", "--multi_thread", type=int, default=150, help='number of threads')
        parser.add_argument("-d", "--data_path", type=str, default="./templete_data.header", help='Templete data filepath to fuzz') 

        args = parser.parse_args()
        return args

class FileIO:
    def __init__(self, directory):
        self.directory = directory
        return
    def http_response_save(self, count, data, res, address=""):
        status_code = res.splitlines()[0].split()[1]
        print("status_code:", status_code)
        
        with open(self.directory+"/"+str(status_code)+"_request_count_"+str(count)+".log" ,"w", encoding="utf-8") as f:
            f.write("REQUEST:\n")
            f.write(data)
            f.write("\n\n")

            f.write("ADDRESS(UDP only):\n")
            f.write(address)
            f.write("\n\n")
    
        with open(self.directory+"/"+str(status_code)+"_response_count_"+str(count)+".html" ,"w", encoding="utf-8") as f:
            f.write(res)
            
        return

class DataFuzzer:
    def __init__(self, templete_data_path):
        with open(templete_data_path, "r") as f:
            self.templete_data = f.read()
        
            
        return
    
    def prepair_for_mutate_http_header_contents(self, fuzz_point_and_dict_list_path):
    
        self.word_list_dict_list = []
        self.keyword_list = []
        
        for i in range(int(len(fuzz_point_and_dict_list_path)/2)):
            self.keyword_list.append(fuzz_point_and_dict_list_path[2*i+0])
            with open(fuzz_point_and_dict_list_path[2*i+1]) as f:
                words = f.read().splitlines()
            self.word_list_dict_list.append(words)
        
        return
    
    
    def mutate_http_header_contents(self):#for fuzzing (http/https)
        if not self.keyword_list or not self.word_list_dict_list:
            print("ERROR: Please execute 'prepair_for_mutate_http_header_contents' function before executing this fuction")
            sys.exit(0)
        temp_data = "\r\n".join(self.templete_data.splitlines())+"\r\n\r\n"
        for mutant in itertools.product(*self.word_list_dict_list):
            print("\nmutation: "+",".join(mutant))
            data = temp_data
            for i in range(len(mutant)):
                data = data.replace("@@@"+str(self.keyword_list[i])+"@@@", mutant[i])
        
            yield data
        
        

class HTTPClient:
    def __init__(self, send_host, send_port=443, https_mode=True):
        self.send_host = send_host #For TCP proxy. If you dont use TCP proxy, this valiable is same as host_name.
        self.send_port = send_port #For TCP proxy. If you dont use TCP proxy, this valiable is same as target_port.
        
        self.timeout = 20
        if https_mode is True:
            self.ssl_context = ssl.create_default_context()
        else:
            self.ssl_context = None
        
        return
     
    
    def UDPclient(self, DATA):#send_data:binary
        
        pre_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        pre_client.settimeout(self.timeout)
        
        
        try:
            if self.ssl_context:
                client = self.ssl_context.wrap_socket(pre_client, server_hostname=self.send_host)
            else:
                client = pre_client

            print("data: ", DATA)
            client.sendto(DATA, (self.send_host, self.send_port))

            
            full_msg = b''
            while True:
                msg, address = client.recvfrom(4096)
                if len(msg) <= 0:
                    break
                full_msg += msg
            res = full_msg.decode("utf-8", 'ignore')
            #print(res)
            #print(address)
        
        except Exception as err:
            print("ERROR: ", err)
            res = "an error\n"
            address = ""
            
        pre_client.close()
        client.close()
        
        return res, address
        
        
    def TCPclient(self, DATA):#send_data:binary

        pre_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        pre_client.settimeout(self.timeout)
        
            
        try:
            if self.ssl_context is not None:
                
                client = self.ssl_context.wrap_socket(pre_client, server_hostname=self.send_host)
                
            else:
                client = pre_client
                
            client.connect((self.send_host, self.send_port))
               
            print("data: ", DATA)
           
            client.send(DATA)

            
            full_msg = b''
            while True:
                msg = client.recv(4096)
                if len(msg) <= 0:
                    break
                full_msg += msg
            res = full_msg.decode("utf-8", 'ignore')
            #print(res)
            
        except Exception as err:
            print("ERROR: ", err)
            res = "an error\n"
       

        pre_client.close()
        client.close()
        
        return res


def tcp_task(FIO, HC, args, count, data):
    
    b_data = Tools().convert_string_to_bytes(data)
    time.sleep(args.intervaltime+random.uniform(0.0, 0.0001))
    res = HC.TCPclient(b_data)
    FIO.http_response_save(count, data, res)
    return


def udp_task(FIO, HC, args, count, data):
    
    b_data = Tools().convert_string_to_bytes(data)
    time.sleep(args.intervaltime+random.uniform(0.0, 0.0001))
    res, address = HC.UDPclient(b_data)
    FIO.http_response_save(count, data, res, address)
    return


def main():
    print("""
◇─────────────────────────────────────────────────────◇
■■    ■  ■■■■■■ ■■■■■■■  ■■■■■■ ■     ■  ■■■■■■  ■■■■■■ 
■■    ■  ■         ■     ■      ■     ■      ■■      ■■ 
■■■   ■  ■         ■     ■      ■     ■      ■       ■  
■ ■■  ■  ■         ■     ■      ■     ■     ■       ■   
■  ■  ■  ■■■■■■    ■     ■■■■■  ■     ■    ■■      ■■   
■  ■■ ■  ■         ■     ■      ■     ■    ■       ■    
■   ■ ■  ■         ■     ■      ■     ■   ■       ■     
■   ■■■  ■         ■     ■      ■■   ■■  ■■      ■■     
■    ■■  ■         ■     ■       ■   ■   ■       ■      
■     ■  ■■■■■■    ■     ■       ■■■■   ■■■■■■■ ■■■■■■■
◇─────────────────────────────────────────────────────◇ """)
    
    
    args = Tools().parser()
    TCPorUDP = args.port[1]#TCP or UDP
    directory_name = args.send_hostname+"_"+datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
    os.mkdir(directory_name)
    FIO = FileIO(directory_name)
    
    if args.port[0] == "https":
        DF = DataFuzzer(args.data_path)
        DF.prepair_for_mutate_http_header_contents(args.fuzz)
        HC = HTTPClient(args.send_hostname, send_port=int(args.port[2]), https_mode=True)
        
        with ThreadPoolExecutor(max_workers=args.multi_thread, thread_name_prefix="thread") as executor:
            for count, data in enumerate(DF.mutate_http_header_contents()):
                
                if TCPorUDP == "udp":
                    executor.submit(udp_task, FIO, HC, args, count, data)
                    
                elif TCPorUDP == "tcp":
                    executor.submit(tcp_task, FIO, HC, args, count, data)
                
                
    
    elif args.port[0] == "http":
        DF = DataFuzzer(args.data_path)
        DF.prepair_for_mutate_http_header_contents(args.fuzz)
        
        HC = HTTPClient(args.send_hostname, send_port=int(args.port[2]), https_mode=False)
        
        with ThreadPoolExecutor(max_workers=args.multi_thread, thread_name_prefix="thread") as executor:
            for count, data in enumerate(DF.mutate_http_header_contents()):
                
                if TCPorUDP == "udp":
                    executor.submit(udp_task, FIO, HC, args, count, data)
                elif TCPorUDP == "tcp":
                    executor.submit(tcp_task, FIO, HC, args, count, data)
                
 
                
    
    else:
        print("unknown protocol:", args.port[0])
        sys.exit(1)

    return


if __name__ == "__main__":
    main()
    