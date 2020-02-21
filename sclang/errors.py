class Error(Exception):
    pass


class LoadingError(Error):
    def __str__(self):
        if self.__cause__:
            return str(self.__cause__)
        return super().__str__(self)
