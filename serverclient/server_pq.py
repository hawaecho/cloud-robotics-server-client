
#=====================================================================================
#
# Filename:  server_pq.py
#
# Description: This code builds a twisted-based server for asynchronous managing requests.
#              A simple resource allocation algorithm is implemented.  
#              The implemented buffer is used to store frequent received requests which do
#              not need to be searched in the database. 
#
#=====================================================================================
import time
#from twisted.internet import pollreactor
#pollreactor.install()

from twisted.internet.protocol import Protocol, Factory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

from twisted.protocols.basic import LineReceiver
from twisted.protocols.basic import NetstringReceiver
import cPickle as pickle
#from IPython.Debugger import Tracer; debug_here = Tracer()
#import IPython
#if IPython.__version__ == '0.12.1':
#    # setup for new version ipython
#    from IPython.core.debugger import Tracer; debug_here = Tracer()
#else:
#    # setup for old version ipython
#    from IPython.Debugger import Tracer; debug_here = Tracer()


# basic protocol test
class Answer(LineReceiver):
    def __init__(self, answers):
        self.answers = answers
    def lineReceived(self, line):
        print "line received ", line
        self.sendLine(line)
        if self.answers.has_key(line):
            self.sendLine(self.answers[line])
        else:
            self.sendLine(self.answers[None])
    def connectionMade(self):
        print "Connection made"
        self.transport.write("Welcome to test.")
        self.sendLine("Welcome by sendLine.")
    def connectionLost(self,reason):
        print "Connection lost", reason
      #  self.transport.write("test connection lost")
      #  self.sendLine("Goodbye by sendLine.") 
        #never happen, since connection is lost already

class AnswerFactory(Factory):
    def buildProtocol(self, addr):
        print "Connection made. Build Answer protocol", addr
        answers = {"Hi": "Hi", None: "I don't understand"}
        return Answer(answers)

######## another group: generic protocol test
class Echo(Protocol):
    def __init__(self,factory):
        self.factory = factory
    def dataReceived(self, data):
        print "Received data: ", data
        self.transport.write(data)
    def connectionMade(self):
        self.transport.write("Welcome to test.")
    def connectionLost(self,reason):
        print "Connection lost for ", reason
        # should never happen
        self.transport.write("test connection lost")

class TestFactory(Factory):
    def buildProtocol(self, addr):
        print "Connection made. Build protocol"
        return Echo(self)

######## pq test ############
def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

#TODO : add more constraints to validate the input request

class DataStruct(object):
    def __init__(self):
        self.topicname = ""
        self.typename = ""
        self.data = ""
        self.responseRequestedId = -1

class RequestStruct(object):
    def __init__(self):
        self.requestId = -1
        self.requestpriority = -1
        self.requesttype = ""
        self.requestdata = ""
        self.requestpriority = -1
        
        #buffer struct
class BufferStruct(object):
    def __init__(self):
        self.bufferId = -1
        self.buffertype = ""
        self.bufferdata = ""

from topicdb import *

#protocal definition
class Echopq(NetstringReceiver):
#class Echopq(Protocol):
    def __init__(self,factory):
        self.factory = factory
#        self.db=TopicDB(dbname='mydb', host='localhost', user='dbcreator', passwd='nifti')
        self.db=TopicDB(dbname='mydb', host='143.89.47.129', user='dbcreator', passwd='nifti')
        self.table='public.topictable'
        print "Protocol for postgreSQL setup."

    def stringReceived(self, strrequest):
   # def dataReceived(self, strrequest):
#        print "Request raw: ", strrequest
        request = pickle.loads(strrequest)
        itemid = request.requestdata
        timestamp = request.requestdata
        requestDataId = request.requestId
        priority = request.requestpriority
        print "Requested type: ", request.requesttype;
        print "Requested itemid: ", itemid;
        print "Requested timestamp: ", timestamp;
        print "Requested ID: ", requestDataId
        print "Requested priority: ", priority

        self.factory.update_priority_list( priority )

        # start time
        s1 = time.time()


        #print "Current priority list length: ", len(self.factory.current_priority_list), self.factory.current_priority_list
        #if self.factory.is_lowest_priority( priority ):
        #    print "I am the winner. WOHO!"
        #    pass
        #else:
        #    time.sleep(1)
        #    while not self.factory.is_lowest_priority( priority ):
        #        print "I need to wait ......"
        #        time.sleep(1)
        
        if request.requesttype == "REQ_DATA_BY_ID":
            if not is_number(itemid):
                print "Wrong Input data, maybe quiting protocol"
                return
            print "Received requested item id: ", itemid

            out = None
            out = self.factory.get_object_from_factory_buffer(itemid, self.factory.buffer_by_id)

            #========================================= 
            # no buffer
            #========================================= 
            loid = self.db.query(("select target from topictable where id=%s;"%itemid).encode('ascii', 'ignore'))
            loid_int = loid.getresult()[0][0] #int number
            print "large object oid in database: ", loid_int #16456
            
            obj_str = self.db.retrieve_large_object(loid_int)

            tname = self.db.query(("select topic from topictable where id=%s"%itemid).encode('ascii', 'ignore'))
            print "Topic Name: ", tname.getresult()[0][0]
            ttname = self.db.query(("select type from topictable where id=%s"%itemid).encode('ascii', 'ignore'))
            print "Topic Type: ", ttname.getresult()[0][0]

            strtname = tname.getresult()[0][0]
            strttname = ttname.getresult()[0][0]

            out = DataStruct()
            out.topicname = strtname
            out.typename = strttname
            out.data = str(obj_str)
            out.responseRequestedId = requestDataId
                
            #========================================= 
            # buffer
            #========================================= 
            #found, out = self.factory.get_object_from_factory_buffer(itemid, self.factory.buffer_by_id)
            #if not found:
            #    loid = self.db.query(("select target from topictable where id=%s;"%itemid).encode('ascii', 'ignore'))
            #    loid_int = loid.getresult()[0][0] #int number
            #    print "large object oid in database: ", loid_int #16456
            #    
            #    obj_str = self.db.retrieve_large_object(loid_int)

            #    tname = self.db.query(("select topic from topictable where id=%s"%itemid).encode('ascii', 'ignore'))
            #    print "Topic Name: ", tname.getresult()[0][0]
            #    ttname = self.db.query(("select type from topictable where id=%s"%itemid).encode('ascii', 'ignore'))
            #    print "Topic Type: ", ttname.getresult()[0][0]

            #    strtname = tname.getresult()[0][0]
            #    strttname = ttname.getresult()[0][0]

            #    out = DataStruct()
            #    out.topicname = strtname
            #    out.typename = strttname
            #    out.data = str(obj_str)
            #    out.responseRequestedId = requestDataId
            #    
            #    # store the newly retrieved data to buffer
            #    self.factory.register_object_to_factory_buffer(itemid, out, self.factory.buffer_by_id)
            #else:
            #    print "********************************"
            #    print "The request item ID has been queried in the past!!!"
            #    print "********************************"
            #    out.responseRequestedId = requestDataId

            outstr = pickle.dumps(out)
            print "Send object. Size ",len(outstr), " Data size ", len(out.data)
            self.sendString(outstr)

        elif request.requesttype == "REQ_DATA_BY_TIMESTAMP":
            if not is_number(timestamp):
                print "Wrong Input data, maybe quiting protocol"
                return
            print "Received requested item timestamp: ", timestamp
            # 
            out = None

            #========================================= 
            # no buffer
            #========================================= 
            out = self.factory.get_object_from_factory_buffer(timestamp, self.factory.buffer_by_time)
            print timestamp

            loid = self.db.query(("select target from topictable where timestamp=%s;"%timestamp).encode('ascii', 'ignore'))
            if True:
                tmpresult = loid.getresult()
                print "=============================="
                print "loid.getresult()", tmpresult
                loid_int = tmpresult[0][0] #int number
            else:
                loid_int = loid.getresult()[0][0] #int number
            print "large object oid in database: ", loid_int #16456 #17378
            
            obj_str = self.db.retrieve_large_object(loid_int) # I believe, you have already known the error is in this line, right?

            tname = self.db.query(("select topic from topictable where timestamp=%s"%timestamp).encode('ascii', 'ignore'))
            print "Topic Name: ", tname.getresult()[0][0]
            ttname = self.db.query(("select type from topictable where timestamp=%s"%timestamp).encode('ascii', 'ignore'))
            print "Topic Type: ", ttname.getresult()[0][0]

            #debug_here()

            strtname = tname.getresult()[0][0]
            strttname = ttname.getresult()[0][0]

            out = DataStruct()
            out.topicname = strtname
            out.typename = strttname
            out.data = str(obj_str)
            out.responseRequestedId = requestDataId

            #========================================= 
            # buffer
            #========================================= 
           # found, out = self.factory.get_object_from_factory_buffer(timestamp, self.factory.buffer_by_time)
           # print timestamp

           # if not found:
           #     loid = self.db.query(("select target from topictable where timestamp=%s;"%timestamp).encode('ascii', 'ignore'))
           #     if True:
           #         tmpresult = loid.getresult()
           #         print "=============================="
           #         print "loid.getresult()", tmpresult
           #         loid_int = tmpresult[0][0] #int number
           #     else:
           #         loid_int = loid.getresult()[0][0] #int number
           #     print "large object oid in database: ", loid_int #16456
           #     
           #     obj_str = self.db.retrieve_large_object(loid_int)

           #     tname = self.db.query(("select topic from topictable where timestamp=%s"%timestamp).encode('ascii', 'ignore'))
           #     print "Topic Name: ", tname.getresult()[0][0]
           #     ttname = self.db.query(("select type from topictable where timestamp=%s"%timestamp).encode('ascii', 'ignore'))
           #     print "Topic Type: ", ttname.getresult()[0][0]

           #     strtname = tname.getresult()[0][0]
           #     strttname = ttname.getresult()[0][0]

           #     out = DataStruct()
           #     out.topicname = strtname
           #     out.typename = strttname
           #     out.data = str(obj_str)
           #     out.responseRequestedId = requestDataId
           #     # store the newly retrieved data to buffer
           #     self.factory.register_object_to_factory_buffer(timestamp, out, self.factory.buffer_by_time)
           # else:
           #     print "********************************"
           #     print "The request timestampe has been queried in the past!!!"
           #     print "********************************"
           #     out.responseRequestedId = requestDataId

            outstr = pickle.dumps(out)
            print "Send object. Size ",len(outstr), " Data size ", len(out.data)
            self.sendString(outstr)


        else:
            print "Not registed request type"
        print "Current number of clients: ", self.factory.numConnectedClient;
        print "Current list of clients: ", self.factory.listClientName
        #print "Lose connection from server side.."
        #self.transport.loseConnection()

#        time.sleep(5)
        # end of transmission

        ######################
        # PRIORITY MANAGEMENT
        ######################
        self.factory.current_priority_list.remove(priority)

        print "Time cost for priority ", priority, " is ",s1, " ", time.time(), " ", time.time()-s1



    def connectionMade(self):
        print("Welcome to pq database access. Please give the object id you wanted: \n >  ")
        self.factory.numConnectedClient += 1;
    def connectionLost(self,reason):
        print "Connection lost for ", reason
        self.factory.numConnectedClient -= 1;
        return

#factory definition
class TestFactorypq(Factory):
    def __init__(self):
        self.numConnectedClient = 0
        self.listClientName = []
        self.buffer_by_time = dict()
        self.buffer_by_id = dict()
        self.current_priority_list = []

    def buildProtocol(self, addr):
        print "Connection made. Build protocol for ", addr
        #debug_here()
        p = Echopq(self)

        p.factory = self
        self.protocol = p
        self.listClientName.append(addr.host)
        return p

    def get_object_from_factory_buffer(self, target, buffers):
        if buffers.has_key(target):
            return True, buffers[target]
        else:
            return False, None

    def register_object_to_factory_buffer(self, item, data, buffers):
        buffers[item] = data

    def update_priority_list( self, pri ):
        self.current_priority_list.append( pri )
#        try:
#            self.current_priority_list.index( pri )
#        except ValueError:
#            self.current_priority_list.append( pri )
#        else:
#            print "WARNING: priority exists!!"
#            sys.exit(0)

    def is_lowest_priority( self, pri ):
        try:
            self.current_priority_list.index( pri )
        except ValueError:
            print "ERROR: priority doesn't exist!!"
            sys.exit(0)
        # check the lowest
        self.current_priority_list.sort()
        if ( pri == self.current_priority_list[0] ): # is lowest
            return True
        else:
             return False

######### test
endpoint = TCP4ServerEndpoint(reactor, 8007)
endpoint.listen(TestFactorypq()) #tested ok # responce on id request, pong back large object as string

print "Service created..."
reactor.run()

#TODO: 
# add logging system: 
from twisted.python import log

# test by:
# telnet localhost 8007
# > 2

#OR:
# nc localhost 8007

# what about postgresql NOTIFY?

