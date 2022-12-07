from .PacketTypes import PacketTypes
from .Packet import Packet


maximum_overwrite_size = 1013

class DataConverter:
    @staticmethod
    def export_values(value_data_type, p_location, p_gate, value, maximum_order):
        overwrite = DataConverter.data_inliner(value)
        packets = []
        for seq_num, payload in enumerate(overwrite):
            packet_value = Packet(packet_type=value_data_type,
                            seq_num=seq_num % maximum_order,
                            peer_ip_addr=p_location,
                            peer_port=p_gate,
                            payload=payload.encode("utf-8"))
            packets.append(packet_value)
        packets[-1].packet_type = PacketTypes().FINAL_SEND_PACKET
        return packets

    @staticmethod
    def data_inliner(overwrite):
        return [overwrite[i:min(len(overwrite), i + maximum_overwrite_size)] for i in range(0, len(overwrite.encode()), maximum_overwrite_size)]