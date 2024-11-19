import threading
from collections import deque


class DataBuffer:
    def __init__(self, name):
        self.buffer_name = name
        self.reader_num = 0
        self.last_reader_index_list = []
        self.buffer = deque()
        self.data_buffer_index = 0
        self.condition = threading.Condition()
        self.finish_label = False

    def register_reader(self):
        with self.condition:
            reader_index = self.reader_num
            self.reader_num += 1
            self.last_reader_index_list.append(-1)
        return reader_index

    def add_data(self, data):
        with self.condition:
            if data is None:
                self.finish_label = True
            else:
                index = self.data_buffer_index
                self.data_buffer_index += 1
                self.buffer.append((index, data))
            self.condition.notify_all()

    def get_data(self, reader_index):
        """
        get data one by one
        :param reader_index:
        :return:
        """
        with self.condition:
            while (not self.buffer) or ((self.buffer[-1][0] is not None) and
                                        (self.buffer[-1][0] <= self.last_reader_index_list[reader_index])):
                if self.finish_label:
                    return None, None
                self.condition.wait()
            for index, data in self.buffer:
                if index == self.last_reader_index_list[reader_index] + 1:
                    self.last_reader_index_list[reader_index] = index
                    self._remove_data()
                    return index, data
            print(f"{reader_index}: Wrong index: {index}")
            return -1, None

    def get_last_data(self, reader_index):
        with self.condition:
            while (not self.buffer) or ((self.buffer[-1][0] is not None) and
                                        (self.buffer[-1][0] <= self.last_reader_index_list[reader_index])):
                if self.finish_label:
                    return None, None
                self.condition.wait()
            index, data = self.buffer[-1]
            self.last_reader_index_list[reader_index] = index
            self._remove_data()
        return index, data

    def get_data_by_index(self, reader_index, target_index):
        with self.condition:
            while not self.buffer:
                if self.finish_label:
                    return None, None
                self.condition.wait()
            for index, data in self.buffer:
                if index == target_index:
                    self.last_reader_index_list[reader_index] = index
                    self._remove_data()
                    return index, data
            else:
                return -1, None

    def _remove_data(self):
        while self.buffer and self.buffer[0][0] <= min(self.last_reader_index_list):
            self.buffer.popleft()
