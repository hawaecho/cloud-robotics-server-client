# mygit

This is a cloud server client infrastructure are based on Ubuntu system with pre-installation of Twisted, Python and PostgreSQL.

0. A brief description of the infrastructure:
- PostgreSQL is a powerful object-relational database management system, which is used for storing the robotic sensor data. The createdummy.sql is the PostgreSQL code for creating a table. The extract_data_from_bag.py is used for extract ros bag into a table in PostgreSQL with keeping the topicdb.py and topicdb.pyc in the same path. (A brief introduction: https://help.ubuntu.com/community/PostgreSQL )
- Twisted is an event-driven networking engine of web socket for server and client written in Python. server_pq.py and client_function_demo.py are my codes for building the cloud server and client based on twisted. There are some of my resource allocation algorithms in the aforementioned web socket codes. (A brief introduction: https://twistedmatrix.com/trac/  and a very useful Chinese tutorial http://turtlerbender007.appspot.com/twisted/index.html.)  The concept of reactor, factory and protocol should clear before you write your code based on
Twisted.
- ros bag
I gave you an example ros bag that I have used. You can change it by any of your bag. Please download the bag in the following link:
https://www.dropbox.com/s/8mkzmwpkhxr7oub/2012-03-24-21-56-50.bag?dl=0

1. Tool Installation Hints:
- Twisted:
sudo add-apt-repository ppa:twisted-dev/ppa
sudo apt-get update
sudo apt-get install python-twisted
- PostgreSQL:
sudo apt-get install postgresql postgresql-contrib
- pgAdmin III is a handy GUI for PostgreSQL, it is essential to beginners. To install it, type at the command line:   
sudo apt-get install pgadmin3
- git
sudo apt-get install git-core

2. Download the codes of my cloud server client codes use the following command.
git clone git://github.com/hawaecho/serverclient.git
I have described the code function in the corresponding  files of git.

3. Using steps:
- type "python server_pq.py" in a terminal,
- type "python client_function_demo.py "
Then you can get a log of received data information in the client side after it requested.
If you need extract your own ros bag, please first
- create the PostgreSQL table as my tutorial:
http://blog.csdn.net/hawaecho/article/details/17472489
- extract the bag into the PostgreSQL table:
python extract_data_from_bag.py

5. Reference paper of this infrastructure of cloud server and client:
- Lujia Wang, Ming Liu and Max Q.-H Meng, “Real-time Multi-sensor
Information Retrieval for Cloud Robotic Systems”, to appear in IEEE
Transactions on Automation Science and Engineering (T-ASE) volume 12,
number 2, in April 2015.
-  Lujia Wang, Ming Liu, Max Q.-H. Meng, Roland Siegwart, Towards Real-time Multi sensor Information Retrieval in Cloud Robotic System, IEEE International Conference on Multisensor Fusion and Information Integration (MFI), 2012,
- Lujia Wang, Ming Liu, Max Q.-H. Meng, Towards Cloud Robotic System: A Case Study of Online Co-localization for Fair Resource Competence, IEEE International Conference on Robotics and Biomimetics (ROBIO), 2012
(PS: Please cite these papers if you have used or compared the corresponding work.)
