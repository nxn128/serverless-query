class Upload:
    """
    Upload data model
    """

    def __init__(self, from_url: str, to_path: int):
        if not from_url or not isinstance(from_url, str):
            raise ValueError('from_url is not defined or is not a string')
        if not to_path or not isinstance(to_path, str):
            raise ValueError('to_path is not defined or is not a string')

        self._from_url = from_url
        self._to_path = to_path

    @property
    def from_url(self) -> str:
        """
        External public url used as data source
        """
        return self._from_url

    @property
    def to_path(self) -> int:
        """
        Path/filename.ext under the data bucket in S3 where data will be copied
        """
        return self._to_path

    def as_dict(self) -> dict:
        """
        Returns class properties as dict
        """
        return {
            'from_url': self._from_url,
            'to_path': self._to_path,
        }
