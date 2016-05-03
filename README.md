## hipchat.py

A python script to display unread hipchat rooms/conversations.

While designed for the iOS [Pythonista](http://omz-software.com/pythonista/) application, the script runs on any linux/mac os environment.

When run within iOS Pythonista, a native ui allows exploring
the unread messages. Linux/Mac OS display is limited to the terminal/console

### Configuration

- Rename `hipchat.sample.conf` to `hipchat.conf` and update values

### Usage

- When you run the script for the first time, it will request a Personal Access token
to access Hipchat on your behalf
- *This scripts only requires read access.*
- Hipchat allows you set configure access permissions eg. read, write, admin.
- Get a personal access token from: https://www.hipchat.com/account/api

iOS / Pythonista
- Simple run this script in Pythonista.

Linux/Mac OS
- Run this script in a linux/os x terminal.

## Installation

- Download or clone the github repo, or:
  - Pythonista console: `import urllib2; exec urllib2.urlopen('http://khl.io/hipchat-py').read()`
  - Linux/Mac OS Terminal: `python -c "import urllib2; exec urllib2.urlopen('http://khl.io/hipchat-py').read()"`