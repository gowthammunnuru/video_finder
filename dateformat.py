import datetime

class FancyDateTimeDelta(object):
    """
    Format the date / time difference between the supplied date and
    the current time using approximate measurement boundaries
    """

    def __init__(self, dt):
        dt = datetime.datetime.strptime(dt, '%Y-%m-%d')
        now = datetime.datetime.now()
        delta = now - dt
        self.year = delta.days / 365
        self.month = delta.days / 30 - (12 * self.year)
        if self.year > 0:
            self.day = 0
        else: 
            self.day = delta.days % 30
        self.hour = delta.seconds / 3600
        self.minute = delta.seconds / 60 - (60 * self.hour)
        self.final_val = self.format()
    
    def format(self):
        fmt = []
        for period in ['year', 'month', 'day']:
            value = getattr(self, period)
            if value:
                if value > 1:
                    period += "s"
                fmt.append("%s %s" % (value, period))
        return ", ".join(fmt) + " ago"

# d = datetime.datetime.strptime("2016-1-25", '%Y-%m-%d')
# FancyDateTimeDelta(d)

class FancyTimeDelta(object):
    """
    Format the date / time difference between the supplied date and
    the current time using approximate measurement boundaries
    """

    def __init__(self, dt):
        dt = dt.split(':')
        self.hr = dt[0]
        self.min = dt[1]
        self.sec = dt[2]
        self.final_val = self.format()
    
    def format(self):
        fmt = []
        for period in ['hr', 'min', 'sec']:
            value = getattr(self, period)            
            if value!="0":
                fmt.append("%s %s" % (value, period))
        return ".".join(fmt)

# d = '0:54:27'
# FancyTimeDelta(d)