# gdb_wrapper
This is a patch for the problem that you can not watch the content of UTF-8 string variables when debugging with gdb and C/C++ extension for Visual Studio Code (vscode) on Windows.

## At first,
This document is written at the time of *C/C++ for Visual Studio Code (Microsoft) Version 0.14.0* released on **October 19, 2017**.

At first, please check "[display utf-8 characters on debug watch panel #918](https://github.com/Microsoft/vscode-cpptools/issues/918)" whether the issue was closed.
It might be resolved by just updating the extension (or updating gdb).

## Requirement
- Windows
- Python 3
- Python modules: win32pipe, win32file

## Demonstrated environment
- Windows10 64bit build 15063
- Visual Studio Code version 1.17.2
- C/C++ for Visual Studio Code version 0.14.0
- mingw-w64-x86_64-gdb 7.12.1-1
- Python version 3.5.2 in root directory of Miniconda3.5

This Python environment (or later version) has required modules, so recommended.

## How to use

### Placement
Place wrapper.bat, wrapper.py, and pserver.py in an any directory.

### Editing wrapper.bat
Edit 2 to 7 lines in wrapper.bat
```
@echo off
set TARGET="B:/msys64/mingw64/bin/gdb.exe"
set PYTHON3=python.exe
rem set FLAGS=DLE
set FLAGS=D
set TARGET_ENCODING=UTF-8
set HOST_ENCODING=CP932
```
You need editing three variables at least.
- `TARGET` : Path to gdb.exe
- `PYTHON3` : Path to python.exe
- `HOST_ENCODING` : Encoding acceptable for vscode

To watch Japanese strings, Leave `HOST_ENCODING` as `CP932`.
I don't know about other languages. You might need some trial and error.

Please see docstring in wrapper.py to see about `FLAGS`.

### Editing launch.json
Edit configurations for debugger in launch.json.
```
 :
"MIMode": "gdb",
"miDebuggerPath": "B:/path/to/gdb_wrapper/wrapper.bat",
"setupCommands": [
	{
		"description": "UTF-8",
		"text": "set charset UTF-8",
		"ignoreFailures": false
	},
	{
		"description": "7bit",
		"text": "set print sevenbit-strings on",
		"ignoreFailures": false
	},
	{
		"description": "Enable pretty-printing for gdb",
		"text": "-enable-pretty-printing",
		"ignoreFailures": false
	}
]
}
```

Write the path to wrapper.bat for `miDebuggerPath` instead of the path to gdb.
Add two commands to `set charset UTF-8` and `set print sevenbit-strings on` in `setupCommands`.

### Debugging
Do debug.

If you can not watch UTF-8 string variables well, rewrite `HOST_ENCODING` in wrapper.bat.

You can `set FLAGS=DE` to see communication between vscode and gdb in another window.
It may help you to watch content of variables temporarily.

That's all.