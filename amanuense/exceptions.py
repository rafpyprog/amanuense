class DiarioNotFoundOnDate(Exception):
    def __init__(self, date):
        self.message = 'Diario not found on date {0}.'.format(date)
