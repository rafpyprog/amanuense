class DiarioNotFoundOnDate(Exception):
    def __init__(self, date):
        self.message = f'Diario not found on date {date}.'
