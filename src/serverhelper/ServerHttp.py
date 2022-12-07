from udp.Packet import Packet
from udp.UdpTransporter import UdpTransporter
from udp.RecWindow import RecWindow
import socket
import threading
from .ConnectionStatus import ConnectionStatus
from udp.PacketTypes import PacketTypes
from .FileRequest import FileRequest
import datetime

value_request = 0
socket_value = PacketTypes()

class ServerHttp:
    def __init__(self, verbose, port, directory, router_port, router_host):
        self.verbose = verbose
        self.port = port
        self.directory = directory
        self.router_port = router_port
        self.router_host = router_host
        self.clients = {}
        self.receiver_windows = {}
        self.timeout = 2

    def initiate(self):
        commander = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            commander.bind(('', self.port))
            commander.settimeout(10)
            if (self.verbose):
                print('HTTPFS is connected to port ', self.port)
            while True:
                try:
                    value, donator = commander.recvfrom(1024)

                    threading.Thread(target=self.client_receiver, args=(commander, value, donator)).start()
                except socket.timeout:
                    continue
        finally:
            commander.close()

    def client_receiver(self, CONN, VALUE, DONATOR):
        packet_data = Packet.from_bytes(VALUE)
        worker ="%s:%s" % (packet_data.peer_ip_addr, packet_data.peer_port)
        if (packet_data.packet_type == socket_value.SYN):
            udp_transporter = UdpTransporter(self.timeout, CONN, self.router_host, self.router_port, packet_data.peer_ip_addr, packet_data.peer_port)
            udp_transporter.get_hs(packet_data, DONATOR)
            self.clients[worker] = udp_transporter
        elif packet_data.packet_type in [socket_value.DATA, socket_value.FINAL_SEND_PACKET]:
            udp_transporter = None
            if worker in self.clients:
                udp_transporter = self.clients[worker]
                if not worker in self.receiver_windows:
                    self.receiver_windows[worker] = RecWindow()
                if not self.receiver_windows[worker] is None:
                    recorder = self.receiver_windows[worker]
                    packet_to_send = self.taker(CONN, DONATOR, packet_data, recorder)
                    while not recorder.compressed_value():
                        try:
                            answer, DONATOR = CONN.recvfrom(1024)
                            packet_data = Packet.from_bytes(answer)
                            packet_to_send = self.taker(CONN, DONATOR, packet_data, recorder)
                        except socket.timeout:
                            CONN.sendto(packet_to_send.to_bytes(), DONATOR)
                            continue
                    question_query = recorder.compressed_buffer()
                    self.receiver_windows[worker] = None
                    if (self.verbose):
                        print(question_query)
                    query_list = question_query[0:question_query.index('\r\n\r\n')].split()
                    body_list = question_query[question_query.index('\r\n\r\n'):].replace('\r\n\r\n', '')
                    type_list = query_list[value_request]
                    answer = ''
                    try:
                        answer = {}
                        if (type_list.lower() == 'get'):
                            answer = FileRequest(query_list, self.directory, body_list).get_query()
                        elif (type_list.lower() == 'post'):
                            answer = FileRequest(query_list, self.directory, body_list).post_query()
                    except:
                        answer = {'status': 500, 'content': ''}
                    finally:
                        http_response = ConnectionStatus.create_response(answer['status'], answer['content'], answer['mimetype'])
                        if (self.verbose):
                            print(http_response)
                        sent_success = udp_transporter.donating(http_response)
                        if sent_success:
                            print('Successfully sent request!')
                        else:
                            print('Communication lost.')
                        if worker in self.clients:
                            self.clients[worker].connection = None
                            self.clients.pop(worker)


    def taker(self, CONN, DONATOR, VALUE, DATA_TYPE):
        packet_value, result = DATA_TYPE.input_value(VALUE)
        deliverables = Packet(
            packet_type=packet_value,
            seq_num=result,
            peer_ip_addr=VALUE.peer_ip_addr,
            peer_port=VALUE.peer_port,
            payload=''
        )
        CONN.sendto(deliverables.to_bytes(), DONATOR)
        CONN.settimeout(self.timeout)
        print('Sent ' + socket_value.get_packet_name(packet_value) + str(result))

        return deliverables