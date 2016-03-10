import sys
import logging
#import cx_Oracle

class SpatialSearch(object):
    def __init__(self, identity):
        self.identity = identity
        logging.debug('identity: '+self.identity)

    def searchGranules(self, offset, rows, west, south, east, north):
        logging.debug('w='+str(west)+',s='+str(south)+',e='+str(east)+',n='+str(north))

        ids = []
        resultCount = 0
        connection = None
        '''
        try:
            connection = cx_Oracle.connect(self.identity)
            cursor = connection.cursor()
            refCursor = connection.cursor()

            westValue = cursor.var(cx_Oracle.NUMBER)
            westValue.setvalue(0, west)
            southValue = cursor.var(cx_Oracle.NUMBER)
            southValue.setvalue(0, south)
            eastValue = cursor.var(cx_Oracle.NUMBER)
            eastValue.setvalue(0, east)
            northValue = cursor.var(cx_Oracle.NUMBER)
            northValue.setvalue(0, north)
            offsetValue = cursor.var(cx_Oracle.NUMBER)
            offsetValue.setvalue(0, offset + 1)
            rowsValue = cursor.var(cx_Oracle.NUMBER)
            rowsValue.setvalue(0, rows)

            cursor.execute(
                'select inventory.searchGranuleSpatialCount(:south,:west,:north,:east) FROM dual',
                {'south': southValue, 'west': westValue, 'north': northValue, 'east': eastValue}
            )
            result = cursor.fetchone()
            if result is None:
                raise Exception('Failed to get count from inventory.searchGranuleSpatialCount.')
            else:
                resultCount = int(result[0])

            cursor.callproc(
                'Inventory.searchGSpatial',
                [southValue, westValue, northValue, eastValue, offsetValue, rowsValue, refCursor]
            )

            logging.debug('rowcount: '+str(cursor.rowcount))
            logging.debug('ref rowcount: '+str(refCursor.rowcount))

            row = refCursor.next()
            while row:
                ids.append(row[0])
                row = refCursor.next()
        except StopIteration:
            pass
        except BaseException as detail:
            print 'ouch', detail
            logging.error('Failed to search granules: '+str(sys.exc_info()[0]))
        finally:
            if connection is not None:
                connection.close()
        '''
        return (ids, resultCount)
