# Common/SpyList.py

class SmartList(list):
    def __init__(self, callback, owner_name, data_type):
        super().__init__()
        self.callback = callback
        self.owner_name = owner_name
        self.data_type = data_type

    def append(self, item):
        super().append(item)

        if self.callback:
            self.callback(self.owner_name, item)

    def clear(self):
        super().clear()