"""
Wrapper for executable like gdb
Usage: python3.exe wrapper.py FLAGS TARGET_ENCODING HOST_ENCODING TARGET [arguments...]
FLAGS: Flags to specify functions
    D:  Decode escaped string in quotation marks.
    L:  Log input and output to "log.txt".
    E:  Send input and output to the echo server to show
    S:  Resolve string value in char array by casting extra command.
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
import storevar

# Globals
FILE_LOG = None
H_PIPE = None
B_DECODE = False
STOREVAR = None
REGX_LTR = re.compile(r'\\\"((\\\d\d\d|\\\\\\\"|\\\\.|[\s!#-\[\]-~])+)\\\"')

FLAGS = sys.argv[1].upper()
TARGET_ENCODING = sys.argv[2]
HOST_ENCODING = sys.argv[3]
IDX_COMMAND = 4
LOG_LOCK = threading.Lock()
INPUT_LOCK = threading.Lock()

# Set globals as flags
if FLAGS.find('D')>=0:
    B_DECODE = True
if FLAGS.find('L')>=0:
    FILE_LOG = open(os.path.join(os.path.dirname(__file__), "log.txt"), 'wb')
if FLAGS.find('E')>=0:
    H_PIPE = win32file.CreateFile(r'\\.\pipe\wrapper_pipe',
        win32file.GENERIC_WRITE, 0, None,
        win32file.OPEN_EXISTING, 0, None)
if FLAGS.find('S')>=0:
    STOREVAR = storevar.StoreVar()

# Change encoding of stdout.
STDOUT_ENCODER = io.TextIOWrapper(sys.stdout.buffer, encoding=HOST_ENCODING)

def oct_decode(match):
    """ Callback to convert escaped string """
    line =  match.group(1)
    data = bytearray()
    while len(line):
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

def decode_data(data):
    string = data.decode(TARGET_ENCODING)
    if B_DECODE:
        string = re.sub(REGX_LTR, oct_decode, string)
        #log(data)
    return string

def log(data):
    """ Output string or binary to file and/or server. """
    if type(data) == str:
        data = data.encode(TARGET_ENCODING)
    
    LOG_LOCK.acquire()
    if FILE_LOG:
        FILE_LOG.write(data)
    if H_PIPE:
        win32file.WriteFile(H_PIPE, data)
    LOG_LOCK.release()

def input_data(proc, data):
    log(data)
    INPUT_LOCK.acquire()
    proc.stdin.write(data)
    proc.stdin.flush()
    INPUT_LOCK.release()

def input_loop(proc):
    """ Input loop from stdin to target. """
    line = ""
    while 1:
        line = sys.stdin.readline()
        # vscode sends logout
        if line.strip()=="logout":
            line = "quit" + os.linesep
        if STOREVAR:
            STOREVAR.input_line(line)
        data = line.encode(TARGET_ENCODING)
        input_data(proc, data)
        # gdb quit command.
        if line.strip()=="quit":
            break

def output_loop(proc):
    """ Output loop from target to stdout. """
    while proc.returncode==None:
        data = proc.stdout.readline()
        string = decode_data(data)
        log(string)
        if STOREVAR:
            string = STOREVAR.output_line(string)
        if STOREVAR and string is None:
            query = STOREVAR.get_requery()
            input_data(proc, query.encode(TARGET_ENCODING))
        else:
            STDOUT_ENCODER.write(string)
            STDOUT_ENCODER.flush()
        proc.poll()

# if STOREVAR:
#     STOREVAR.set_log_func(log)

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
if H_PIPE:
    H_PIPE.Close()
if FILE_LOG:
    FILE_LOG.close()
