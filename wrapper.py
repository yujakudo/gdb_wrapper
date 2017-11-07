#!/usr/bin/env python
"""
Wrapper for executable like gdb
Usage: python3.exe wrapper.py FLAGS TARGET_ENCODING HOST_ENCODING TARGET [arguments...]
FLAGS: Flags to specify functions
    D:  Decode escaped string in quotation marks.
    L:  Log input and output to "log.txt".
    E:  Send input and output to the echo server to show
TARGET_ENCODING:	Encoding of target executable. e.g. UTF-8
HOST_ENCODING:		Encoding of host.
TARGET:     Target executable
arguments:  Arguments of target
"""

import os
import sys
import subprocess
import io
import threading
import win32file
import re

# Globals
FILE_LOG = None
H_PIPE = None
B_DECODE = False
PATTERN_LTR = re.compile(r'\\\"((\\\d\d\d|[\!-\~\s])+?)\\\"')
FLAGS = sys.argv[1].upper()
TARGET_ENCODING = sys.argv[2]
HOST_ENCODING = sys.argv[3]
IDX_COMMAND = 4

# Set globals as flags
if FLAGS.find('D')>=0:
    B_DECODE = True

if FLAGS.find('L')>=0:
    FILE_LOG = open(os.path.join(os.path.dirname(__file__), "log.txt"), 'wb')

if FLAGS.find('E')>=0:
    H_PIPE = win32file.CreateFile("\\\\.\\pipe\\wrapper_pipe",
        win32file.GENERIC_WRITE, 0, None,
        win32file.OPEN_EXISTING, 0, None)

# Change encoding of stdout.
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding=HOST_ENCODING)

def log(data):
    """ Log output to the  file """
    if FILE_LOG:
        if type(data) == str:
            data = data.encode(TARGET_ENCODING)
        FILE_LOG.write(data)

def oct_decode(match):
    """ Callback to convert escaped string """
    line =  match.group(1)
    data = bytearray()
    while len(line)>3:
        if line[0]=="\\" and "0"<=line[1] and line[1]<="9" and "0"<=line[2] and line[2]<="9" and "0"<=line[3] and line[3]<="9":
            data.append(int(line[1:4], 8))
            line = line[4:]
        elif line[0]=="\\":
            data.append(ord(line[1]))
            line = line[2:]
        else:
            data.append(ord(line[0]))
            line = line[1:]
    line = '\\\"' + data.decode(TARGET_ENCODING, "ignore") + '\\\"'
    return line

def output_str(data, echo=True):
    """ Output string or binary to stdout and/or server. """
    string = data
    # Convert escapsed string
    if B_DECODE:
        if type(data) != str:
            string = data.decode(TARGET_ENCODING)
        string = re.sub(PATTERN_LTR, oct_decode, string)
        data = string.encode(TARGET_ENCODING)
    else:
        if type(data) == str:
            data = data.encode(TARGET_ENCODING)
        else:
            string = data.decode(TARGET_ENCODING)
    # Log to file
    log(data)
    # Write to stdout with enoding of the host
    if echo:
        sys.stdout.write(string)
        sys.stdout.flush()
    # Send to the echo server
    if H_PIPE:
        win32file.WriteFile(H_PIPE, data)

def input_loop(proc):
    """ Input loop from stdin to target. """
    line = ""
    while 1:
        line = sys.stdin.readline()
        # vscode sends logout
        if line.strip()=="logout":
            line = "quit" + os.linesep
        data = line.encode(TARGET_ENCODING)
        output_str(data, False)
        proc.stdin.write(data)
        proc.stdin.flush()
        # gdb quit command.
        if line.strip()=="quit":
            break;

def output_loop(proc):
    """ Output loop from target to stdout. """
    line = ""
    while proc.returncode==None:
        line = proc.stdout.readline()
        output_str(line, True)
        proc.poll()

# Log the Python version and command line.
log("Python %d.%d\n" % (sys.version_info.major, sys.version_info.minor))
log("Target encoding:%s  Host encoding:%s  FLAGS: %s\n" % (TARGET_ENCODING, HOST_ENCODING, FLAGS))
log(" ".join(sys.argv[IDX_COMMAND:]) + "\n\n")

# Start target
target_proc = subprocess.Popen(sys.argv[IDX_COMMAND:], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

# Main loops
threading.Thread(target=input_loop, args=(target_proc,)).start()
output_loop(target_proc)

# Tarminate
target_proc.terminate()
if FILE_LOG:
    FILE_LOG.close()
