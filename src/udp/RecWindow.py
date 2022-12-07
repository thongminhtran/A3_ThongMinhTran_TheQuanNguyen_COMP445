from .PacketTypes import PacketTypes
value_types = PacketTypes()
maximum_order = 10
class RecWindow:

    def __init__(self, max_seq_num=maximum_order):
        self.buffer = []
        self.max_seq_num = max_seq_num
        self.current_seq_start = 0
        self.window_size = int(self.max_seq_num / 2)
        self.window = dict.fromkeys([seq for seq in range(0, self.max_seq_num)])
        self.buffer_ready = False
    
    def compressed_value(self):
        return self.buffer_ready

    def compressed_buffer(self):
        return "".join(self.buffer)

    def get_door(self):
        return [window[index] for index in self.order_checker()]

    def input_value(self, value):
        print('Starting input a value ', value.seq_num)
        if value.seq_num in self.order_checker():
            print('Valid order numbers are: ')
            print(self.order_checker())
            self.window[value.seq_num] = value
            if value.packet_type == value_types.FINAL_SEND_PACKET:
                self.final_flag = True
        return self.identifier()

    def identifier(self):
        is_slid_window = False
        for INDEX in self.order_checker():
            current_packet = self.window[INDEX]
            if INDEX == self.current_seq_start and current_packet != None:
                self.buffer.append(current_packet.payload.decode('utf-8'))
                self.next()
                is_slid_window = True
                if (current_packet.packet_type == value_types.FINAL_SEND_PACKET):
                    print("all packets have been received")
                    self.buffer_ready = True
                    return (value_types.FINAL_REC_PACKET, (self.current_seq_start - 1) % self.max_seq_num)
        if (is_slid_window):
            return (value_types.ACK, (self.current_seq_start - 1) % self.max_seq_num)
        else:
            return (value_types.NAK, self.current_seq_start)

    def next(self):
        self.window[self.current_seq_start] = None
        self.current_seq_start = (self.current_seq_start + 1) % self.max_seq_num

    def order_checker(self):
        return [num % self.max_seq_num for num in range(self.current_seq_start, self.current_seq_start + self.window_size)]