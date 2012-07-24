Using Amazon Elastic Cloud Server
=================================

1. Create an amazon ec2 account

2. Launch an ubuntu instance

3. Open two bash / command lines. On for your local computer one to login to the server

4. In the management console find your server address

(replace the addesses below with ubuntu@your_server_string.compute.amazonaws.com)


Log on the amazon server::

 ssh -i ./ec2/ec2.pem ubuntu@ec2-79-125-32-99.eu-west-1.compute.amazonaws.com

on amazon ec2 ubuntu server::

 mkdir cce
 mkdir abce
 mkdir abce/lib

on local computer::

 SPATH="ubuntu@ec2-79-125-32-99.eu-west-1.compute.amazonaws.com"
 scp -r -i ./ec2/ec2.pem ./abce/lib/*.py  $SPATH:~/abce/lib/
 scp -r -i ./ec2/ec2.pem ./cce/*.py  $SPATH:~/cce/
 scp -r -i ./ec2/ec2.pem ./cce/*.csv  $SPATH:~/cce/


To shut down your ubuntu instance from the command line::

 sudo shutdown -P now
