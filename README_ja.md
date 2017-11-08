# gdb_wrapper
WindowsのVisual Studio Code (vscode)にて、C/C++拡張機能とgdbを使ってデバッグをした時に、UTF-8の文字列の変数が文字化け（或いは数字の羅列）になって見られない問題があります。
このツールは、その問題に対するパッチです。

## はじめに
この文は、Microsoftより**2017年10月19日**にリリースされた *C/C++ for Visual Studio Code Version 0.14.0* の時点で書かれています。

はじめに "[display utf-8 characters on debug watch panel #918](https://github.com/Microsoft/vscode-cpptools/issues/918)" を見て、問題がクローズしているかどうかを確認してください。
もしかしたら拡張機能、あるいはgdbをアップデートするだけで解決するかもしれません。

## 要求事項
- Windows
- Python 3
- Pythonモジュール: win32pipe, win32file

## 実績のある環境
- Windows10 64bit build 15063
- Visual Studio Code version 1.17.2
- C/C++ for Visual Studio Code version 0.14.0
- mingw-w64-x86_64-gdb 7.12.1-1
- Miniconda3のルートディレクトリにあるPython (version 3.5.2)

このPython環境（或はこれ以降のバージョン）には、必用な２つのモジュールが含まれていますので、おすすめです。

## 使い方

### 配置
4つのファイル（ wrapper.bat, *.py ）を、任意の同じディレクトリ内に配置します。

### wrapper.batの編集
wrapper.batの2行から6行を編集します。
```
@echo off
set TARGET="B:/msys64/mingw64/bin/gdb.exe"
set PYTHON3=python.exe
set FLAGS=DS
set TARGET_ENCODING=UTF-8
set HOST_ENCODING=CP932
```
少なくとも以下の３つの変数の編集が必要です。
- `TARGET` : gdb.exeへのパス
- `PYTHON3` : python.exeへのパス
- `HOST_ENCODING` : C/C++拡張が読めるエンコーディング

日本語の文字列を見るには、`HOST_ENCODING` は `CP932` のままにします。
他の言語についてはわかりません。もしかしたら、試行錯誤が必要かもしれません。

`FLAGS`については、wrapper.pyのdocstringを参照してください。

### launch.jsonの編集
launch.jsonの、デバッガの configuration を編集します。
```
 :
"MIMode": "gdb",
"miDebuggerPath": "B:/path/to/gdb_wrapper/wrapper.bat",
"setupCommands": [
	{
		"description": "target-charsetとhost-charsetをUTF-8に設定",
		"text": "set charset UTF-8",
		"ignoreFailures": false
	},
	{
		"description": "非ASCII文字を8進数表記にエスケープ",
		"text": "set print sevenbit-strings on",
		"ignoreFailures": false
	},
	{
		"description": "Enable pretty-printing for gdb",
		"text": "-enable-pretty-printing",
		"ignoreFailures": false
	}
]
```

`miDebuggerPath`に、gdbへのパスの代わりにwrapper.batへのパスを書きます。

`setupCommands`に、"`set charset UTF-8`" と "`set print sevenbit-strings on`" の2つのコマンドを追加します。

### デバッグ
デバッグしてみます。

もしUTF-8の文字列の変数がうまく見えない場合は、wrapper.bat の `HOST_ENCODING` を書き換えてみてください。

`set FLAGS=DSE` とすると、別ウィンドウでvscodeとgdbの通信内容を見ることができます。
一時的に文字列変数の中身を見るのにも役立つかもしれません。

以上。