from pg import *

import cPickle as pickle

# first define functions to insert nodes and relations
def csv(l):
    return ",".join([str(s) for s in l])

def csv(l):
    return ",".join([str(s) for s in l])

class TopicDB:
    def __init__(self,dbname,host=None,user=None,passwd=None):
        # First prepare this experiment in the database
        self.conn = connect(dbname=dbname,host=host,\
                user=user,passwd=passwd)

    def query(self,q):
        return self.conn.query(q)

    def select_field(self, field, table):
        q="select %s from %s;"%(field, table)
        qr=self.conn.query(q)
        return qr.dictresult()

    def insert_with_id(self,table,idname,id,fields,values):
        query = "INSERT INTO %s (%s) VALUES (%s);" \
                % (table,csv(fields+[idname]),csv(values+[id]))
        # print query
        self.conn.query(query)
        return id

    def insert_topic(self,table,fields,values):
        query = "INSERT INTO %s (%s) VALUES (%d,'%s','%s',%d,%d);" \
                % (table,csv(fields),values[0], values[1], values[2], values[3], values[4])
        # print query
        self.conn.query(query)
        return

    def insert_large_object(self,buffer):
        self.conn.query("BEGIN")
        lohandle = self.conn.locreate(INV_WRITE)
        if lohandle:
            lohandle.open(INV_WRITE)
            lohandle.write(buffer)
            lohandle.close()
            self.conn.query("END")
            return lohandle.oid
        else:
            self.conn.query("ROLLBACK")
            raise IOError()

    def retrieve_large_object(self,oid):
        self.conn.query("BEGIN")
        lohandle = self.conn.getlo(oid)
        if lohandle:
            lohandle.open(INV_READ)
            size = lohandle.size()
            buffer = lohandle.read(size)
            lohandle.close()
            self.conn.query("END")
            return buffer
        else:
            self.conn.query("ROLLBACK")
            raise IOError()

    def retrieve_topic_by_index(self, index):
        loid = self.query("select target from topictable where id=%d;"%index)
        loid_int = loid.getresult()[0][0] #int number
        print "large object oid in database: ", loid_int
        ret_str_obj = self.retrieve_large_object(loid_int)
        return pickle.loads(ret_str_obj)

