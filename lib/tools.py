#TODO
change dprint to dwriteln
put write and writeln statement
change order before, before text

import sys

def common_internals(text, before="<", after=""):
    if before != "":
        if before[0] == "(":
            after = ")"
        if before[0] == "[":
            after = "]"
        if before[0] == "<":
            after = ">"
        if before[0] == "{":
            after = "}"        
        if before[-1] == ":":
            before = before + '\n'
            if after == '':
                after = '\n===\n'
        elif (len(before) - len(after) > 0):
                before = before + ':'
        if after == '':
            before = '<' + before
            after = '>'

    return before + str(text) + after

def dwrite(*k):
    """dwrites prints without carrier feed
    dwrite("text", "") => text
    dwrite("text") => <text>
    dwrite("text","{") => {text}
    dwrite("text", "<msg) => <msg:text>
    dwrite("text","msg:") => msg:\ntext\n===
    """
    if debug:
        sys.stdout.write(common_internals(*k))


def dprint(*k):
    """
    dwrite("text", "") => text
    dwrite("text") => <text>
    dwrite("text","{") => {text}
    dwrite("text", "<msg) => <msg:text>
    dwrite("text","msg:") => msg:\ntext\n===
    """
    if debug:
        print(common_internals(*k))


def write(*k):
    sys.stdout.write(common_internals(*k))

def writeln(*k):
    print(common_internals(*k))

def debug_off()
    debug = False

def debug_on()
    debug = True

debug = True

if __name__ == "__main__":
    idname = "0055"
    dprint("text", "{")
    dprint("text", "{a")
    dprint("text", "{aabb")
    dprint("text", "b")
    dprint("text", "")
    dprint("text")
    dprint("text", "a", "b")
    dprint("text", "bracets with colon")
    dprint("line1\nline2\nline3", "msg")
    dprint("line1\nline2\nline3", "<msg")
    dprint("line1\nline2\nline3", "msg:")
    dprint("line1\nline2\nline3", "<msg:")
    dprint("line1\nline2\nline3", ":")

