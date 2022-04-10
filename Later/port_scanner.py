import time
import socket
from IPy import IP # pip install IPy
import paramiko    # pip install paramiko
import threading
import termcolor


def check_ip(ip):
    ''' return IP address is possible
    else convert hostname to IP address
    by socket.gethostbyname(ip)'''
    try:
        IP(ip)
        return ip
    except ValueError:
        return socket.gethostbyname(ip)


def scan(target):
    converted_ip = check_ip(target)     
    print('\n'+'[+] Scanning started for '+ str(target))  
    for port in range(1,101):
        connect(converted_ip , port )


def connect(ipaddress,port):
    ''' 
    [+] nslookup www.wwe.com   >  works as dns lookup  for the ( IP address )
    Look for the Address       >  199.232.254.133
    we connect to a server , not with a domain name but with an IP address'''

    try:
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.settimeout(0.5)  # we assume port will reply within 0.5 seconds else its closed
        sock.connect((ipaddress,port))
        print(termcolor.colored( f'[+] Port {port} is open', 'green') )
        return sock
    except:
        # print(termcolor.colored( f'[+] Port {port} is Closed', 'red') )
        # return False
        pass


def ssh_connect(password,code=0):
    """ 
    paramiko = makes a connection with a remote device through SSh
    by using SSH2 as a replacement for SSL to make a secure connection between two devices

    here host == [+] target address 
    username  == [+] username of the target address
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host,port=22,username=username,password=password)
    except paramiko.AuthenticationException:
        code = 1
    except socket.error as e:
        code = 2
    ssh.close()
    return code 
        

def main():
    ''' Loop through Ip addresses or Domain names inorder
    to scan the ports for each server '''
    ipaddress = input('[+] Enter Targets to Scan ( Split with , ): ').split(',')
    for each_ip in ipaddress:
        if each_ip:
            scan(each_ip.strip(' '))

main()



