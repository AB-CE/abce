import os
if os.name in ('posix', 'Darwin'):  # unix compatible
    zmq_transport = 'ipc'  # possible values:
                                #    'ipc' for unix/linux/bsd/mac computers
                                #    'tcp' for windows (single processor) computers, windows, unix clusters / clouds
else:
    zmq_transport = 'tcp'  # possible values:
                            #    'ipc' for unix/linux/bsd/mac computers
                            #    'tcp' for windows (single processor) computers, windows, unix clusters / clouds
    if not(os.name in ('nt')):
        print("Os not recognized, defaulted to tcp (slow) for windows"
        " compatibility. Edit config.py to choose ipc if you use anything but"
        "windows and get this message. Please track the bug on Github.")

config_tcp = {
    'command_addresse': "tcp://localhost:5001",
    'ready': "tcp://localhost:5002",
    'frontend': "tcp://localhost:5003",
    'backend': "tcp://localhost:5004",
    'database': "tcp://localhost:5005",
    'logger': "tcp://localhost:5006",
    'group_backend': "tcp://localhost:5007"
}

#agent_language can be 'python' or 'java' (or equivalently 'jython')
agent_language = 'java'
