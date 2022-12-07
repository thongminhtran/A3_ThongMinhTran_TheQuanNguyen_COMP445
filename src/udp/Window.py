class Window:
    def __init__(self, data, max_seq_num):
        self.data = data
        self.max_seq_num = max_seq_num
        self.window_size = int(self.max_seq_num / 2)
        self.current_seq_start = 0
        self.data_index = 0
        self.window = [packet for packet in self.data[0 : min(len(self.data), self.window_size)]]
        self.complete = False
  
    def door_value_get(self):
        return [packet for packet in self.window if packet.seq_num in self.order_check()]

    def data_retrieval(self, order_number):
        if order_number in self.order_check():
            for VALUE in self.window:
                if VALUE.seq_num == order_number:
                    return VALUE
        return None

    def door_extractor(self, order_ACK_value):
        if order_ACK_value in self.order_check():
            rate_to_parse = ((order_ACK_value - self.current_seq_start) % self.max_seq_num) + 1
            rating_done = [num % self.max_seq_num for num in range(self.current_seq_start, self.current_seq_start + rate_to_parse)]
            adjacent_value = (self.current_seq_start + rate_to_parse) % self.max_seq_num
            new_value = min(len(self.data), self.data_index + rate_to_parse)
            self.current_seq_start = adjacent_value
            self.window = [packet for packet in self.data[self.data_index : new_value + 1]]
            self.data_index = new_value
            return rating_done
        if self.data_index == len(self.data):
            self.complete = True
        return []

    def order_check(self):
        correct_values = [num % self.max_seq_num for num in range(self.current_seq_start, self.current_seq_start + self.window_size)]
        correct_length = len(self.data[self.data_index : min(self.data_index + self.window_size, len(self.data))])
        return correct_values[:correct_length]