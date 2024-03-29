from __future__ import print_function
from PCANBasic import *
import os.path
import datetime
import sys
import keyboard
from ctypes import *
import socket

cols = ["No", "Time_Offset", "Type", "ID", "Data_Length", 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight']

def send_message(host, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(message.encode())
        response = s.recv(1024)
        print('Received:', response.decode())


if __name__ == "__main__":
    
    dataset_type = "Normal"
    x = datetime.datetime.now()
    x = "Dataset\\KIA " + dataset_type + " Dataset " + str(x).split()[0] + "-"
    ind = 0

    while os.path.isfile( x + str(ind) + ".txt"):
        ind += 1
        print("Yes")

    print("No")
    x = x + str(ind) + ".txt"
    f = open(x, "a")
    all_data = ""
    for col in cols:
        all_data += col + "\t"

    print(all_data)
    f.write(all_data + "\n")
    def update_progress(progress):
        print("\r progress [{0}] {1}%".format('#'*(progress//10), progress), end='')
    

    CAN = PCANBasic()                            #CANi
    CAN_BUS = PCAN_USBBUS3
    result = CAN.Initialize(CAN_BUS, PCAN_BAUD_100K, 2047, 0, 0) #Channel, Btr, HwType, IOPort, INterrupt
    if result != PCAN_ERROR_OK:
        # An error occurred, get a text describing the error and show it
        #
        print("oh No")
        CAN.GetErrorText(result)
        print(result)
    start_time = 0
    readResult = PCAN_ERROR_OK,
    IsFirst = True
    ind = 1
    while True:
        # Check the receive queue for new messages
        #
        readResult = CAN.Read(CAN_BUS)
        if readResult[0] != PCAN_ERROR_QRCVEMPTY:
            # Process the received message
            #
            print("A message was received")
            all_data = str(ind) + ')' + "\t"
            if IsFirst:
                offset = 0
                start_time = readResult[2].micros + 1000 * readResult[2].millis + 0x100000000 * 1000 * readResult[2].millis_overflow
                start_time = start_time / 1000
                # start_time = readResult[2].millis
                IsFirst = False
            else:
                current_time = readResult[2].micros + 1000 * readResult[2].millis + 0x100000000 * 1000 * readResult[2].millis_overflow
                # current_time = readResult[2].millis
                current_time = current_time / 1000
                offset = (current_time - start_time)
            
        
            all_data += "{:.3f}".format(offset) + "\t"
            id_hex = hex(readResult[1].ID)[2:]
            for _ in range(4 - len(id_hex)):
                id_hex = '0' + id_hex.upper()
            
            all_data += str(readResult[1].MSGTYPE) + "\t" + id_hex + "\t" + str(hex(readResult[1].LEN)[2:]) 
                

            data_field = []
            for j in range(readResult[1].LEN):
                data_hex = hex(readResult[1].DATA[j])[2:]  
                for _ in range(2 - len(data_hex)):
                    data_hex = '0' + data_hex.upper()
                data_field.append(data_hex.upper())
                all_data += "\t" + data_hex.upper()

            for _ in range(readResult[1].LEN, 8):
                all_data += "\t" + "-1"
                data_field.append("-1")            
            data = {
                "No": ind,
                "Time_Offset": offset,
                "Type": readResult[1].MSGTYPE,
                "ID": id_hex,
                "Data_Length": readResult[1].LEN,
                'One': data_field[0],
                'Two': data_field[1],
                'Three': data_field[2],
                'Four': data_field[3],
                'Five': data_field[4],
                'Six': data_field[5],
                'Seven': data_field[6],
                'Eight': data_field[7]
            }

            message_str = ','.join(str(data[col]) for col in cols)
            send_message('192.168.10.127', 65432, message_str)

            all_data += "\t" 
            all_data += "\n"
            ind += 1
            print(all_data)
            f.write(all_data)
            
            if keyboard.is_pressed('k'):
                break
    CAN.Uninitialize(PCAN_NONEBUS)