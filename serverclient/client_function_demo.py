
#=====================================================================================
#
# Filename:  client_function_demo.py
#
# Description: This code builds a twisted-based client for requesting data.
#              The data is requested in two index: one is ID and the other is timestamp,
#              according to the table structure of database PostgreSQL.
#
#=====================================================================================
#from twisted.internet import pollreactor
#pollreactor.install()
#
from sys import stdout

from twisted.internet.protocol import Protocol, Factory, ClientFactory
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver
from twisted.protocols.basic import NetstringReceiver
from twisted.internet import defer
import cPickle as pickle
import time

from twisted.protocols import policies
# Ming: for the weird problem of pickled wrong attributes. the following lines need to be commented in python. 
# only works while in ipython.
#import IPython
#if IPython.__version__ == '0.12.1':
#    # setup for new version ipython
#    from IPython.core.debugger import Tracer; debug_here = Tracer()
#else:
#    # setup for old version ipython
#    from IPython.Debugger import Tracer; debug_here = Tracer()

#debug_here() # test Tracer() is working

start_time = dict()
response_time = dict()

class DataStruct(object):
    def __init__(self):
        self.topicname = ""
        self.typename = ""
        self.data = ""
        self.responseRequestedId = -1
        
class RequestStruct(object):
    def __init__(self):
        self.requestId = -1;
        self.requesttype = ""
        self.requestdata = ""
        self.requestpriority = -1

######### generic echo test, postgresql
class Echopq(NetstringReceiver):
    def __init__(self):
        self.MAX_LENGTH = 20000000
        print "Protocol initialized! MAX_LENGTH: ", self.MAX_LENGTH
    def stringReceived(self, data):
    #def dataReceived(self, data):
        print "Received data: ", len(data)
        #print "Received data: ", data
        key_data = DataStruct()
        #print data
        try:
           # debug_here()
            key_data = pickle.loads(data)
            self.factory.returnedTopic = key_data.topicname
            self.factory.returnedType =  key_data.typename
            self.factory.returnedData =  key_data.data;
            self.factory.returnedLength = len(key_data.data);
            # response Id and time
            self.factory.returnedId = key_data.responseRequestedId
            self.factory.returnedTime = time.time();

            print "Received responce for requested ID: ", key_data.responseRequestedId

            global response_time;
            response_time.update({key_data.responseRequestedId:time.time()})

            print "data registered!", key_data.typename, key_data.topicname
            self.factory.ready = True
        except:
            print "Wrong data"

        # update the responce time???
        #response_time.update({self.responseRequestedId:time.time()})
        #response_time.update({key_data.responseRequestedId:time.time()})
       # reactor.stop()
        #self.transport.loseConnection()
        #print "DO loseconnection"

        #TODO for Lujia: convert stringIO to ros message or other operations

    def mySendData(self, datap):
        #print "Checking for item property (id, timestamp, or others): ", data.requesttype
        #debug_here()
        _data = RequestStruct()
        _data = datap
        strdata = pickle.dumps(_data)
       # self.transport.write(strdata)
        self.sendString(strdata)

class EchoClientFactorypq(ClientFactory):
    def __init__(self):
        self.returnedData = "";
        self.returnedLength = 0;
        self.returnedTopic = "";
        self.returnedType = "";
        self.returnedTime = 0;
        self.returnedId = 0
        self.ready = False;
    def startedConnecting(self, connector):
        print "started to connect"
    def buildProtocol(self, addr):
        print "connected"
        # notice: p.factory need to be allocated specifically
        p = Echopq()
        p.factory = self
        self.protocol = p
        return p
    def connectionLost(self, connector, reason):
        print 'Lost connection. Reason: ', reason
    def clientConnectionLost(self, connector, reason):
        print 'Lost connection. Reason: ', reason
    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason: ', reason


def callback_pq(p, request, t):
    print "in %.2f second, asking for property "%t, request.requesttype
    reactor.callLater(t, p.mySendData, request)
    return 

# If the client is with the same IP of the server, then 
hostname = "localhost"
# If the client and server are not with the same IP, then 
#hostname = "192.168.56.1"
port = 8007
import sys

ask = 8
if len(sys.argv) > 1:
    #ask = int(sys.argv[1])
    hostname = sys.argv[1]

counter = 0

def process(endpoint, myfactory, access):
    global counter;
    global start_time
    print "Request by ID"
    req = RequestStruct()
    req.requestId = counter;
    req.requestpriority = 2;
    counter += 1;
    req.requesttype = "REQ_DATA_BY_ID"
    #ID 2346 /map
    req.requestdata = str(2346)
    #access.addCallback(callback_pq, req, 0.5 )
    start_time.update({req.requestId:time.time()})
    myfactory.protocol.mySendData(req)


#    print "Request by time"
#    req = RequestStruct()
#    req.requestId = counter;
#    counter += 1;
#    req.requesttype = "REQ_DATA_BY_TIMESTAMP"
#    req.requestdata = str(1332622613320852564)
#    #access.addCallback(callback_pq, req, 2.5 )
#    start_time.update({req.requestId:time.time()})
#    myfactory.protocol.mySendData(req)

    print "Request by time"
    req = RequestStruct()
    req.requestId = counter;
#    priority
    req.requestpriority = 5;
    counter += 1;
    req.requesttype = "REQ_DATA_BY_TIMESTAMP"
    # ID 310 topic: /map, 
    req.requestdata = str(1332622613320852564)
    #access.addCallback(callback_pq, req, 2.5 )
    start_time.update({req.requestId:time.time()})
    myfactory.protocol.mySendData(req)

    print "Request by ID"
    req = RequestStruct()
    req.requestId = counter;
    counter += 1
    req.requestpriority = 3;
    req.requesttype = "REQ_DATA_BY_ID"
    # ID 995 /map
    req.requestdata = str(995)
    #access.addCallback(callback_pq, req, 0.5 )
    start_time.update({req.requestId:time.time()})
    myfactory.protocol.mySendData(req)

    print "Request by time"
    req = RequestStruct()
    req.requestId = counter;
    counter += 1
#    priority
    req.requestpriority = 1;
    req.requesttype = "REQ_DATA_BY_TIMESTAMP"
    # ID 310 /map
    req.requestdata = str(1332622613320852564)
    #access.addCallback(callback_pq, req, 2.5 )
    start_time.update({req.requestId:time.time()})
    myfactory.protocol.mySendData(req)
#
    print "Request by ID"
    req = RequestStruct()
    req.requestId = counter;
    counter += 1
    req.requestpriority = 4;
    req.requesttype = "REQ_DATA_BY_TIMESTAMP"
    req.requesttype = "REQ_DATA_BY_ID"
    # ID 995 /map
    req.requestdata = str(995)
    #access.addCallback(callback_pq, req, 0.5 )
    start_time.update({req.requestId:time.time()})
    myfactory.protocol.mySendData(req)
#
    print "Request by time"
    req = RequestStruct()
    req.requestId = counter;
#    priority
    req.requestpriority = 6;
    counter += 1
    req.requesttype = "REQ_DATA_BY_TIMESTAMP"
    # ID 2346 /map 
    req.requestdata = str(1332622624329051355)
    #access.addCallback(callback_pq, req, 2.5 )
    start_time.update({req.requestId:time.time()})
    myfactory.protocol.mySendData(req)


def shutdownreactor(endpoint, myfactory, access):
    print "Length of start", len(start_time), " end", len(response_time)
    t = time.localtime()
    filename= "qos_logger_%d_%d_%d_%d_%d.log"%(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min)
    print "Now I shutdown. And write the log files: ", filename, " ." 
    fp = open("start_log", 'w')
    for s in start_time:
        fp.write("%d %f \n"%(s, start_time[s]))
    fp.close()

    fp = open("end_log", 'w')
    for s in response_time:
        fp.write("%f\t%f\n"%(response_time[s], response_time[s]-start_time[s]))
    fp.close()

    import os
    os.system('paste start_log end_log > %s'%filename)

    reactor.stop()

# main function 
print "Create connection to ", hostname, port
endpoint = TCP4ClientEndpoint(reactor, hostname, port) 

#unlimited_myfactory = EchoClientFactorypq()
#myfactory = policies.ThrottlingFactory(unlimited_myfactory, readLimit=100000000)

myfactory = EchoClientFactorypq()
access = endpoint.connect(myfactory) # Deferred


reactor.callLater(1, process, endpoint, myfactory, access);
reactor.callLater(50, shutdownreactor, endpoint, myfactory, access);
reactor.run()


