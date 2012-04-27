""" common definitions for worldengine and agentengine """
def agent_name(group_name, idn):
    """
    given a group name and a id-number it returns the
    agent_name. a message send to the agent_name, will
    be received by this individual agent
    """
    return group_name + '_' + str(idn) + ':'

def group_address(group_name):
    """
    returns a string that is useable to addresses every agent of the group.
    it returns "group_name:"
    """
    return group_name + ':'
