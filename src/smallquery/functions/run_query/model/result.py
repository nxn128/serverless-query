class Result:
    """
    Results data model
    """

    def __init__(self, data, exec_time):
        self._data = data
        self._exec_time = exec_time

    @property
    def data(self):
        """
        Query result data
        """
        return self._data

    @property
    def exec_time(self):
        """
        Query execution time
        """
        return self._exec_time
