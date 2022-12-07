from .PacketTransfer import DataConverter
from .PacketTypes import PacketTypes
from .RecWindow import RecWindow
import socket
from threading import Timer
from .Window import Window
from .Packet import Packet
import ipaddress
import random
import sys

value_data = PacketTypes()
maximum_order = 10
 
class UdpTransporter:
    def __init__(self, timeout, connection=socket.socket(socket.AF_INET, socket.SOCK_DGRAM), router_addr="localhost", router_port=3000, peer_ip=ipaddress.ip_address(socket.gethostbyname('localhost')), peer_port=8008):
        self.connection = connection
        self.router_addr = router_addr
        self.router_port = router_port
        self.peer_ip = ipaddress.ip_address(socket.gethostbyname(peer_ip)) if peer_ip == "localhost" else peer_ip
        self.peer_port = peer_port
        self.timeout = timeout
        self.stop_all_timers = False
        self.keep_alive_num = 25

    def initialize_sh(self):
        stack_order = random.randrange(0, 2**31)
        synchronize_value = Packet(packet_type=value_data.SYN,
                            seq_num=stack_order,
                            peer_ip_addr=self.peer_ip,
                            peer_port=self.peer_port,
                            payload='')
        get_ack_value = False
        index = 0
        while (not get_ack_value):
            try:
                self.donate_value(synchronize_value)
                answer, donator = self.connection.recvfrom(1024)
                packet = Packet.from_bytes(answer)
                if packet.packet_type == value_data.SYN_ACK:
                    order_number = int(packet.seq_num) + 1
                    value_ack = Packet(packet_type=value_data.ACK,
                                        seq_num=order_number,
                                        peer_ip_addr=self.peer_ip,
                                        peer_port=self.peer_port,
                                        payload='')
                    self.donate_value(value_ack)
                    get_ack_value = True
            except socket.timeout:
                index += 1
                print("Time is over => Sending back....")
                if self.maintain_indexer(index) is False:
                    sys.exit()
                else:
                    continue

    def get_hs(self, value, donator):
        any_order = random.randrange(0, 2**31)
        value_ack = str(value.seq_num + 1).encode("utf-8")
        ack_synchronize_value = Packet(packet_type=value_data.SYN_ACK,
                                seq_num=any_order,
                                peer_ip_addr=value.peer_ip_addr,
                                peer_port=value.peer_port,
                                payload=value_ack)
        self.connection.sendto(ack_synchronize_value.to_bytes(), donator)

    def donating(self, data):
        self.complete_sending = False
        values = DataConverter.export_values(value_data.DATA, self.peer_ip, self.peer_port, data, maximum_order)
        door = Window(values, maximum_order)
        rate_frame = {}
        self.donate_rated_door(door, rate_frame)
        non_reply = False
        index = 0
        while(not door.complete or non_reply):
            try:
                if self.connection == None:
                    break
                else:
                    answer, donator = self.connection.recvfrom(1024)
                    packet = Packet.from_bytes(answer)
                    print('RECEIVED ' + value_data.get_packet_name(packet.packet_type) + str(packet.seq_num))
                    if packet.packet_type == value_data.ACK:
                        rated_frames = door.door_extractor(packet.seq_num)
                        self.time_paused(rate_frame, rated_frames)
                        self.donate_rated_door(door, rate_frame)
                    elif packet.packet_type == value_data.NAK:
                        rated_frames = door.door_extractor((packet.seq_num - 1) % maximum_order)
                        self.time_paused(rate_frame, rated_frames)
                        self.donate_value(door.data_retrieval(packet.seq_num))
                        if packet.seq_num in rate_frame:
                            self.value_rated_packet([rate_frame[packet.seq_num]])
                    elif packet.packet_type == value_data.FINAL_REC_PACKET:
                        door.complete = True
                        print("Every values have been sent!!!")
                        break;
            except socket.timeout:
                if not non_reply:
                    index += 1
                    print("Time is over, send again....")
                    self.donate_rated_door(door, rate_frame)
                    if self.maintain_indexer(index) is False:
                        non_reply = True
                        break
                    else:
                        continue
        self.stop_all_timers = True
        return False if non_reply else True

    def get_reply(self):
        recorder = RecWindow()
        index = 0
        while not recorder.compressed_value():
            try:
                if (self.connection == None):
                    break
                value, donator = self.connection.recvfrom(1024)
                packet = Packet.from_bytes(value)
                if (packet.packet_type in [value_data.DATA, value_data.FINAL_SEND_PACKET]):
                    print('This ' + value_data.get_packet_name(packet.packet_type) + str(packet.seq_num) + 'has been received')
                    value_type, order_value = recorder.input_value(packet)
                    value_to_donate = Packet(
                        packet_type=value_type,
                        seq_num=order_value,
                        peer_ip_addr=packet.peer_ip_addr,
                        peer_port=packet.peer_port,
                        payload=''
                    )
                    self.donate_value(value_to_donate)
            except socket.timeout:
                index += 1
                print("Receive timeout, resending...")
                if self.maintain_indexer(index) is False:
                    sys.exit()
                else:
                    continue
        return recorder.compressed_buffer()

    def donate_value(self, donated_value):
        if donated_value != None:
            print('The ' + value_data.get_packet_name(donated_value.packet_type) + '#' + str(donated_value.seq_num) + ' has been sent')
            if self.connection != None:
                self.connection.sendto(donated_value.to_bytes(), (self.router_addr, self.router_port))
                self.connection.settimeout(self.timeout)

    def donate_rated_door(self, window, rated_frame):
        for packet in window.door_value_get():
            if packet is not None:
                order_value = packet.seq_num
                rated_frame[order_value] = {"packet": packet, "acknowledged": False}
                self.value_rated_packet([rated_frame[order_value]])
                self.donate_value(packet)

    def time_paused(self, rated_frame, rating):
        for FRAME in rating:
            if FRAME in rated_frame:
                rated_frame[FRAME]['acknowledged'] = True
    
    def time_controller(self, rated_information):
        if not self.stop_all_timers:
            packet = rated_information['packet']
            acknowledged = rated_information['acknowledged']
            if not acknowledged:
                self.donate_value(packet)
    
    def value_rated_packet(self, rated_information):
        Timer(self.timeout, self.time_controller, rated_information).start()
    
    def maintain_indexer(self, timeout_count):
        if timeout_count == self.keep_alive_num:
            print("System terminating due to no reply!!!!")
            return False