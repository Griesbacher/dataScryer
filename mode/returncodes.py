class Returncodes:
    OK = 0
    Warning = 1
    Critical = 2
    Unknown = 3

    @staticmethod
    def name(nr):
        return next(name for name, value in vars(Returncodes).items() if value == nr)
