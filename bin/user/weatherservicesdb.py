#!/usr/bin/python3
# Copyright (C) 2023 Johanna Roedenbeck

"""

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""

"""
    In order to display the readings provided by the weather services
    in diagrams or calculate aggregated values out of them, data have to
    saved into a database that WeeWX can process. For doing so, there
    are two things to consider:
    
    - Those data are subject to subsequent quality checks. So data 
      already provided can change afterwards. 
    
    - Additionally readings are provided with certain delay.
    
    - WeeWX requires all data to be of the same timestamp.
    
    For these reasons the readings are not saved by the methods of
    WeeWX but by the thread provided here.
    
    Unlike WeeWX this thread extends the database schema automatically
    if new observation types are seen. Please note, that WeeWX
    does not recognize them until restarted.
    
    Let this thread create the databases before referencing them
    in section `[DataBindings]` in weewx.conf.
"""

VERSION = "0.x"

import threading
import configobj
import os.path
import sqlite3
import time

if __name__ == '__main__':

    import sys
    sys.path.append('/usr/share/weewx')

    def logdbg(x):
        print('DEBUG',x)
    def loginf(x):
        print('INFO',x)
    def logerr(x):
        print('ERROR',x)

else:

    import weeutil.logger
    import logging
    log = logging.getLogger("user.DWD.db")

    def logdbg(msg):
        log.debug(msg)

    def loginf(msg):
        log.info(msg)

    def logerr(msg):
        log.error(msg)

import weewx
import weeutil.weeutil
import weewx.units

# deal with differences between python 2 and python 3
try:
    # Python 3
    import queue
except ImportError:
    # Python 2
    # noinspection PyUnresolvedReferences
    import Queue as queue

def sqlstr(x):
    if x is None: return 'NULL'
    return str(x)

class DatabaseThread(threading.Thread):

    def __init__(self, name, db_queue, db_pth, log_success, log_failure):
        """ create thread to save readings to a SQLITE database
        
            Args:
                name (str): thread name for logging
                db_queue (queue.Queue): queue to receive data to save
                db_pth (str): target directory
                log_success (boolean): log successful operation
                log_failure (boolean): log unsuccessful operation
            
            Returns:
                nothing
        """
        super(DatabaseThread,self).__init__(name=name)
        self.db_queue = db_queue
        self.db_pth = db_pth
        self.log_success = log_success
        self.log_failure = log_failure
        self.evt = threading.Event()
        self.running = True
        self.databases = dict()
        self.filenames = dict()
        logdbg("thread '%s': database path: %s" % (self.name,self.db_pth))

    def shutDown(self):
        """ request thread shutdown """
        self.running = False
        loginf("thread '%s': shutdown requested" % self.name)
        self.evt.set()

    def run(self):
        """ thread loop """
        loginf("thread '%s' starting" % self.name)
        try:
            while self.running:
                try:
                    reply = self.db_queue.get(timeout=1.5)
                except queue.Empty:
                    continue
                self.process_data(reply[0],reply[1],reply[2])
                #self.evt.wait(waiting)
        except Exception as e:
            logerr("thread '%s': main loop %s - %s" % (self.name,e.__class__.__name__,e))
        finally:
            self.close_db()
            loginf("thread '%s' stopped" % self.name)
    

    def open_create_db(self, provider, interval):
        """ open or create the database for a given interval """
        if interval not in self.databases:
            if provider.lower() in ('poi','cdc','zamg','openmeteo','met','radolanhg','radolanwn','radolanrv'):
                file = 'weatherservices-readings-%s-%s.sdb' % (self.name,interval)
            else:
                file = '%s.sdb' % provider
            file = os.path.join(self.db_pth, file)
            logdbg("thread '%s': database file %s" % (self.name,file))
            try:
                self.databases[interval] = sqlite3.connect(file)
                self.filenames[interval] = file
                cur = self.databases[interval].cursor()
                cur.execute('CREATE TABLE IF NOT EXISTS archive(`dateTime` INTEGER PRIMARY KEY NOT NULL, `usUnits` INTEGER NOT NULL, `interval` INTEGER)')
            except sqlite3.Error as e:
                if self.log_failure:
                    logerr("thread '%s': could not open or create database %s %s - %s" % (self.name,file,e.__class__.__name__,e))
        return self.databases.get(interval)

    
    def close_db(self):
        """ close open databases """
        for interval in self.databases:
            try:
                self.databases[interval].close()
            except sqlite3.Error as e:
                if self.log_failure:
                    logerr("thread '%s': error closing database '%s' %s %s" % (self.name,self.filenames.get(interval,'N/A'),e.__class__.__name__,e))


    def check_and_add_columns(self, con, data, logtext):
        """ check if required columns exist """
        required_columns = [key for key in data[-1] if key not in ('dateTime','interval','usUnits')]
        logdbg("check_and_add_columns(): required_columns = %s" % required_columns)
        try:
            cur = con.cursor()
            res = cur.execute('SELECT * from archive')
            #reply = res.fetchone()
            present_columns = [key[0] for key in res.description]
            new_columns = set(required_columns).difference(present_columns)
            if not new_columns:
                # empty set --> no column to add, all columns present already
                logdbg("check_and_add_columns(): columns already present")
                return True
            for column in new_columns:
                cur.execute('ALTER TABLE archive ADD COLUMN %s REAL' % column)
            con.commit()
            if self.log_success:
                loginf("thread '%s', %s: successfully added columns %s to database" % (self.name,logtext,new_columns))
            return True
        except sqlite3.Error as e:
            if self.log_failure:
                logerr("thread '%s', %s: error adding columns to database %s %s" % (self.name,logtext,e.__class__.__name__,e))
        return False
    
    def update_data(self, con, data, logtext):
        """ insert or update 
        
            Args:
                con(sqlite3.Connection): database connection
                data(list of dict): data to save
                
            Returns:
                nothing
        """
        try:
            inserted = 0
            updated = 0
            cur = con.cursor()
            for el in data:
                if 'dateTime' in el:
                    res = cur.execute('SELECT count(*) FROM archive WHERE `dateTime`=?',tuple((el['dateTime'],)))
                    reply = res.fetchone()
                    if reply and reply[0]:
                        # There is a row for that timestamp in the database.
                        colvals = ','.join(['`%s`=%s' % (key,sqlstr(val)) for key,val in el.items() if key not in ('dateTime','usUnits','interval',None)])
                        if not colvals: continue
                        sql = 'UPDATE archive SET %s WHERE `dateTime`=%s' % (colvals,el['dateTime'])
                    else:
                        # There is no row for that timestamp in the database.
                        cols = ','.join([key for key in el if key])
                        vals = ','.join([sqlstr(el[key]) for key in el if key])
                        sql = 'INSERT INTO archive (%s) VALUES (%s)' % (cols,vals)
                    if __name__ == '__main__':
                        logdbg(sql)
                    try:
                        cur.execute(sql)
                        if sql.startswith('INSERT'):
                            inserted += 1
                        else:
                            updated += 1
                    except sqlite3.Error as e:
                        if self.log_failure:
                            logerr("thread '%s', %s: error executing %s %s - %s" % (self.name,logtext,sql,e.__class__.__name__,e))
            con.commit()
            if self.log_success:
                loginf("thread '%s', %s: Added %s record%s and updated %s record%s" % (self.name,logtext,inserted,'' if inserted==1 else 's',updated,'' if updated==1 else 's'))
        except sqlite3.Error as e:
            if self.log_failure:
                logerr("thread '%s', %s: error updating data %s - %s" % (self.name,logtext,e.__class__.__name__,e))
    
    def process_data(self, datasource, prefix, data):
        """ process data

            Args:
                datasource(str): product name like CDC, POI, Radolan etc.
                prefix(str): observation type prefix
                data(list of dict of ValueTuple): data to convert
                
            Returns:
                nothing
        """
        interval = weewx.units.convert(data[0].get('interval'),'minute')[0]
        con = self.open_create_db(datasource, interval)
        x = self.convert(prefix, data)
        if prefix:
            logtxt = "prefix '%s'" % prefix
        elif datasource.startswith('Radolan'):
            logtxt = "product '%s'" % datasource[7:]
        else:
            logtxt = datasource
        if con and self.check_and_add_columns(con, x, logtxt):
            self.update_data(con, x, logtxt)
    
    def convert(self, prefix, data):
        """ convert data to the appropriate units and add prefix to the keys
        
            Args:
                prefix(str): observation type prefix
                data(list of dict of ValueTuple): data to convert
                
            Returns:
                list of dict: converted data
        """
        new_data = []
        for el in data:
            x = {'usUnits':weewx.METRIC}
            for key, val in el.items():
                try:
                    if key!='usUnits':
                        new_val = weewx.units.convertStd(val,weewx.METRIC)[0]
                        if key in ('dateTime','interval'):
                            new_key = key
                            new_val = weeutil.weeutil.to_int(new_val)
                        else:
                            if prefix:
                                new_key = prefix+key[0].upper()+key[1:]
                            else:
                                new_key = key
                            if val[1] and val[2]:
                                new_val = weeutil.weeutil.to_float(new_val)
                        x[new_key] = new_val
                except (AttributeError,TypeError,ValueError,LookupError) as e:
                    if self.log_failure:
                        logerr("thread '%s': error converting %s %s %s - %s" % (self.name,prefix,key,e.__class__.__name__,e))
            new_data.append(x)
        logdbg('convert(): %s' % new_data)
        return new_data


def databasecreatethread(name, config_dict):
    """ create database thread
        
        Args:
            name (str): thread name
            config_dict (configobj.ConfigObj): configuration dict
            
        Returns:
            queue.Queue: queue reference to use with databaseput()
            threading.Thread: thread reference
    """
    weewx_path = config_dict.get('WEEWX_ROOT')
    sqlite_path = config_dict.get('DatabaseTypes',configobj.ConfigObj()).get('SQLite',configobj.ConfigObj()).get('SQLITE_ROOT','.')
    if weewx_path:
        sqlite_path = os.path.join(weewx_path,sqlite_path)
    site_dict = weeutil.config.accumulateLeaves(config_dict.get('WeatherServices',configobj.ConfigObj()).get('current',configobj.ConfigObj()))
    log_success = weeutil.weeutil.to_bool(site_dict.get('log_success',True))
    log_failure = weeutil.weeutil.to_bool(site_dict.get('log_failure',True))
    save = weeutil.weeutil.to_bool(site_dict.get('save',True))
    if save:
        q = queue.Queue()
        db = DatabaseThread(name,q,sqlite_path,log_success,log_failure)
        db.start()
    else:
        q = None
        db = None
    return q, db


def databaseput(q, datasource, prefix, data):
    """ queue new data for saving
    
        Args:
            q (queue.Queue): queue to put data in
            prefix (str): column name prefix
            data (list of dict): data to save
        
        Returns:
            True in case of success, False otherwise
    """
    if q:
        try:
            # data has to be a list of dicts
            data[0].get('dateTime')
            # append the new item to the queue
            q.put((datasource, prefix, data))
            return True
        except queue.Full:
            # should not happen as long as the thread is alive
            pass
        except (AttributeError,TypeError,LookupError):
            # one or more parameters are not appropriate
            pass
    return False


if __name__ == '__main__':

    q, db = databasecreatethread('DWD-dbtest',configobj.ConfigObj())

    try:
        x = []
        while True:
            x.append({
                'dateTime':(time.time(),'unix_epoch','group_time'),
                'interval':(10,'minute','group_interval'),
                'outTemp':(28.5,'degree_C','group_temperature'),
                'outHumidity':(20.1,'degree_C','group_temperature'),
            })
            if len(x)>3:
                del(x[0])
            databaseput(q,'CDC','xx',x)
            print('---')
            time.sleep(5)
    except Exception as e:
        print('**MAIN**',e)
    except KeyboardInterrupt:
        print()
        print('**MAIN** CTRL-C pressed')

    db.shutDown()
    time.sleep(5)
