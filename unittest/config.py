import os
# zmq_transport possible values:
#    'ipc' for unix/linux/bsd/mac computers
#    'tcp' for windows (single processor) computers, windows, unix clusters / clouds
#    'custom', config_custom_bind and config_custom_connect, must be defined
if os.name in ('posix', 'Darwin', 'java'):  # unix compatible
    zmq_transport = 'ipc'
    if os.name == 'java':
	import java.lang
	ver = java.lang.System.getProperty("os.name").lower()
	if not(ver == 'linux'):        
		print("Waring %s chosen on java/jython, it has not been tested on windows. "
        	"On error try to substitute with 'tcp'" % zmq_transport)
elif os.name in ('nt'):
    zmq_transport = 'tcp'
else:
    print("Os '%s' not recognized, defaulted to tcp (slow) for windows"
    " compatibility. Edit config.py to choose ipc if you use anything but"
    "windows and get this message. Please track the bug on Github." % os.name)
    zmq_transport = 'tcp'

print("transport protocol: %s" % zmq_transport)

config_tcp_bind = {
    'command_addresse': "tcp://*:5001",
    'ready': "tcp://*:5002",
    'frontend': "tcp://*:5003",
    'backend': "tcp://*:5004",
    'database': "tcp://*:5005",
    'logger': "tcp://*:5006",
    'group_backend': "tcp://*:5007"
}

config_tcp_connect = {
    'command_addresse': "tcp://localhost:5001",
    'ready': "tcp://localhost:5002",
    'frontend': "tcp://localhost:5003",
    'backend': "tcp://localhost:5004",
    'database': "tcp://localhost:5005",
    'logger': "tcp://localhost:5006",
    'group_backend': "tcp://localhost:5007"
}
