# =========================================================
#   File name: extract_data_from_bag.py
#  Description: This code is used to extract a rosbag into 
#               table of PostgreSQL
#
# =========================================================
#!/usr/bin/python
#test: extract_data_from_bag.py 2012-03-24-21-56-50.bag 

import roslib; roslib.load_manifest('rosbag')
import rosbag

from topicdb import *

import cPickle as pickle

import StringIO

def extract_dict_from_bag(bagfile):
    bag = rosbag.Bag(bagfile, 'r')
    messages = bag.read_messages()
    # write topics into dictionary
    data = dict(enumerate(messages))
    #set of topic
    #ss=set([c.topic for c in bag._get_connections()])
    return data, len(data)


if __name__ == '__main__':
    import sys
    if len(sys.argv) ==1:
        print "Usage: ./extract_data_from_bag.py <bagname.bag>"
        sys.exit(1)
    else:
        data,num_topic = extract_dict_from_bag(sys.argv[1]);
        print num_topic, " topics included in bag file ", sys.argv[1] 
        # all data are saved in dictionary <data>, indexed: topic, msg, t

    # init database access
    db=TopicDB(dbname='worlddb', host='localhost', user='dbcreator', passwd='nifti')
    print "Connected to database."
    table='public.topictable'

    # test to insert the first 3 item to database
    #for i in range(num_topic):
    for i in range(10):
        topic = str(data[i][0])
        msg = data[i][1]
        #serialize data
        obj=StringIO.StringIO()
        msg.serialize(obj)
        t = int(str(data[i][2]))

        #large object for binary saving, using pickled dumped string
        obj_id = db.insert_large_object(pickle.dumps(obj));
        obj.close()
        # write data to database
        db.insert_topic(table, ['id','topic','type','timestamp', 'target'],
                    [i,topic, msg._type, t, obj_id]);

    print "Bag saved to database table", table

    # read back large object by index
    index = 0# CAREFUL!! In this example, only 'nav_msgs' is loaded. The topic types are limited.
    loid = db.query("select target from topictable where id=%d;"%index)
    loid_int = loid.getresult()[0][0] #int number
    print "large object oid in database: ", loid_int
    # get the object from database
    obj_str=db.retrieve_large_object(loid_int) # CAREFUL!! In this example, only 'nav_msgs' is loaded. The topic types are limited.
    # catcher
    out_ser=StringIO.StringIO()
    # load the serialized object as string
    out_ser=pickle.loads(obj_str)
    # initialized a new message object according to topic type
    # if type==TYPENAME: out=TYPENAME();
    roslib.load_manifest('nav_msgs')
    from nav_msgs.msg import MapMetaData
    out=MapMetaData()
    out_ser.read()
    out.deserialize(out_ser.buf)
    print out

    #test to read stuff back
    print db.select_field('topic', table)
    

#check bag_helper.py for more information and hints
# x=data[i][1] will retrieve a message object, which is good.
# object is saved by pickle string convertion: dumps and loads
