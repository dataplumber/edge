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
    
    @staticmethod
    def convertISOTimeToEpoch(isoTime, format):
        try:
            #parse ISO date to datetime object
            dt = dateutil.parser.parse(isoTime)

            # note that this method is OS dependent - the %s specifier is not standard in python
            # Soo.. this should be corrected with a statement like the one below
            # The issue with the statemet below is one is time zone aware and the other not
            # By making both UTC the difference should succeed and comply with standard python practice
            return int(dt.strftime('%s'))
#            return int((dt - datetime.datetime(1970,1,1)).total_seconds())
        except Exception:
            return None


if __name__ == '__main__':
    t = "2015-05-02T00:00:00Z"
    d = DateUtility()
    print d.convertISOTimeToEpoch(t, "%Y-%M-%DT%h:%m:%sZ")

