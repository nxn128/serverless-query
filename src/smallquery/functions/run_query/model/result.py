class Result:
    def __init__(self, data, exec_time):
        self._data = data
        self._exec_time = exec_time

    @property
    def data(self):
        return self._data

    @property
    def exec_time(self):
        return self._exec_time
