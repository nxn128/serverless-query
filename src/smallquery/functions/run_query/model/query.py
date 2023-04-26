class Query:
    """
    Query data model
    """
    MAX_ROWS = 1000

    def __init__(self, sql: str, limit: int):
        if not sql or not isinstance(sql, str):
            raise ValueError("Query is not defined or is not a string")

        self._sql = sql
        self._limit = min(int(limit), Query.MAX_ROWS)

    @property
    def sql(self) -> str:
        """
        SQL to execute
        """
        return self._sql

    @property
    def limit(self) -> int:
        """
        Max rows to return
        """
        return self._limit

    def as_dict(self) -> dict:
        """
        Returns class properties as dict
        """
        return {
            'query': self._sql,
            'limit': self._limit,
        }
