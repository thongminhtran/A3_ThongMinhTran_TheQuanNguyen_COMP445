import ipaddress
MINIMUM_LENGTH = 11
MAXIMUM_LENGTH = 1024
class Packet:


    def __init__(self, packet_type, peer_ip_addr, peer_port, payload, seq_num=0):
        self.packet_type = int(packet_type)
        self.seq_num = int(seq_num)
        self.peer_ip_addr = peer_ip_addr
        self.peer_port = int(peer_port)
        self.payload = payload

    def value_set(self, chosen_value):
        self.seq_num = int(chosen_value)

    def to_bytes(self):
        buffer = bytearray()
        buffer.extend(self.packet_type.to_bytes(1, byteorder='big'))
        buffer.extend(self.seq_num.to_bytes(4, byteorder='big'))
        buffer.extend(self.peer_ip_addr.packed)
        buffer.extend(self.peer_port.to_bytes(2, byteorder='big'))
        buffer.extend(self.payload)
        return buffer

    def __repr__(self, *args, **kwargs):
        return "#%d, peer=%s:%s, size=%d" % (self.seq_num, self.peer_ip_addr, self.peer_port, len(self.payload))

    @staticmethod
    def from_bytes(original_data):

        if len(original_data) < MINIMUM_LENGTH:
            raise ValueError("{} bytes only. This is too little".format(len(original_data)))
        if len(original_data) > MAXIMUM_LENGTH:
            raise ValueError("{} bytes. This exceeds the maximum value.}".format(len(original_data)))

        curr = [0, 0]

        def nbytes(byte_number):
            curr[0], curr[1] = curr[1], curr[1] + byte_number
            return original_data[curr[0]: curr[1]]

        value_data = int.from_bytes(nbytes(1), byteorder='big')
        number_order = int.from_bytes(nbytes(4), byteorder='big')
        p_location = ipaddress.ip_address(nbytes(4))
        p_gate = int.from_bytes(nbytes(2), byteorder='big')
        overwrite = original_data[curr[1]:]

        return Packet(packet_type=value_data,
                      seq_num=number_order,
                      peer_ip_addr=p_location,
                      peer_port=p_gate,
                      payload=overwrite)
