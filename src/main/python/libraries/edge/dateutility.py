from datetime import date, datetime, timedelta
import dateutil.parser
import calendar
"""
Utility class for date and time conversion.
"""
class DateUtility(object):
    
    RFC_822_GMT_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"
    
    @staticmethod
    def convertTimeLongToIso(time):
        isoTime = ''
        try:
            isoTime = datetime.utcfromtimestamp(float(time) / 1000).isoformat() + 'Z'
        except ValueError:
            pass
        return isoTime
    
    @staticmethod
    def convertISOToUTCTimestamp(isoTime):
        try:
            #parse ISO date to datetime object
            dt = dateutil.parser.parse(isoTime)
            
            #return timestamp in milliseconds
            return calendar.timegm(dt.utctimetuple()) * 1000
        except:
            return None
    
    @staticmethod
    def pastDateRFC822(hoursAgo):
        return (datetime.utcnow() - timedelta(hours=hoursAgo)).strftime(DateUtility.RFC_822_GMT_FORMAT)
    
    @staticmethod
    def convertTimeLongToRFC822(time):
        return DateUtility.convertTimeLong(time, DateUtility.RFC_822_GMT_FORMAT)
    
    @staticmethod
    def convertTimeLong(time, format):
        strTime = ''
        try:
            strTime = datetime.utcfromtimestamp(float(time) / 1000).strftime(format)
        except ValueError:
            pass
        return strTime

    @staticmethod
    def convertISOTime(isoTime, format):
        try:
            #parse ISO date to datetime object
            dt = dateutil.parser.parse(isoTime)
            
            #return timestamp in specified format
            return dt.strftime(format)
        except:
            return None
