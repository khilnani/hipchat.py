## hipchat.py

A python script to display unread hipchat rooms/conversations.

While designed for the iOS [Pythonista](http://omz-software.com/pythonista/) application, the script runs on any linux/mac os environment.

When run within iOS Pythonista, a native ui allows exploring
the unread messages. Linux/Mac OS display is limited to the terminal/console

## Installation

- Download or clone the github repo, or:
  - Pythonista console: `import urllib2; exec urllib2.urlopen('http://khl.io/hipchat-py').read()`
  - Linux/Mac OS Terminal: `python -c "import urllib2; exec urllib2.urlopen('http://khl.io/hipchat-py').read()"`

## Configuration

- Rename `hipchat.sample.conf` to `hipchat.conf` and update values

## Usage

### Note

- When you run the script for the first time, it will request a Personal Access token to access Hipchat on your behalf
- *This scripts only requires read access.*
- Hipchat allows you set configure access permissions eg. read, write, admin.
- Get a personal access token from: https://www.hipchat.com/account/api

### Execution 

- Simply run this script in Pythonista, or in a Linux/Mac OS Terminal
- Example. `python hipchat.py [LASTRUN | DETAILS | NODETAILS]`
  - `LASTRUN`: Use cached data, view recent info without calling apis.
  - `DETAILS`: Linux/Mac OS Only, auto show unread details.
  - `NODETAILS`: Linux/Mac OS Only, skip display of unread details.

### Mac OS Automator

- Launch `/Applications/Automator`
- Create a new document of type *Service*
    - Save as something indicator, eg `hipchat-unread` (be a bit more creative)
        - The script will be saved to `/Users/USERNAME/Library/Services/hipchat-unread.workflow`
    - Configure (top ot the screen) to be: Service recieves `no input` in `any application`
- Add the following workflow action
  - `Utilities` / `Run AppleScript`
  ```javascript
on run {input, parameters}
	tell application "Terminal"
		activate
		if (the (count of the window) = 0) or ¬
			(the busy of window 1 = true) then
			tell application "System Events"
				keystroke "n" using command down
			end tell
		end if
		do script "cd DIR_WITH_SCRIPT && python hipchat.py" in window 1
	end tell
	return input
end run
  ```
- Launch `System Preferences` and navigate to `Keyboard` / `Shortcuts`
- Under `Services` locate your Service in the `General` category
- Assign a keyboard shortcut.