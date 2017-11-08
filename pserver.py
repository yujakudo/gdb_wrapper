"""
Echo Server to show string.
Usage: python3.exe pserver.py ENCODING
ENCODING:	Encoding of incoming data
"""

import sys
import win32pipe, win32file

ENCODING = "UTF-8"
if len(sys.argv)>1:
    ENCODING = sys.argv[1]

H_PIPE = win32pipe.CreateNamedPipe(r'\\.\pipe\wrapper_pipe',
    win32pipe.PIPE_ACCESS_INBOUND,
    win32pipe.PIPE_TYPE_BYTE | win32pipe.PIPE_WAIT,
    1, 4096, 4096, 500, None)

win32pipe.ConnectNamedPipe(H_PIPE, None)

while 1:
    try:
        (rc, buff) = win32file.ReadFile(H_PIPE, 4096)
    except:
        break
    if rc==0:
        string = buff.decode(ENCODING, "ignore")
        sys.stdout.write(string)

H_PIPE.Close()
