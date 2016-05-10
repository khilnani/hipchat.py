## hipchat.py

A python script to display unread hipchat rooms/conversations. 

On iOS, Hipchat notifications sometimes do not show, or it can be easy to miss one. This script allows you to perform a review of any unread notifications.

While designed for the iOS [Pythonista](http://omz-software.com/pythonista/) application, the script runs on any linux/mac os environment.

When run within iOS Pythonista, a native ui allows exploring
the unread messages. Linux/Mac OS display is limited to the terminal/console.

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
- Example. `python hipchat.py [ CACHE | DETAILS | NODETAILS | S3 ]`
  - `CACHE`: Use cached data, view recent info without calling apis. Each execution saves to cache.
  - `DETAILS`: Linux/Mac OS Only, auto show unread details.
  - `NODETAILS`: Linux/Mac OS Only, skip display of unread details.
  - `S3`: Use Amazon S3 instead of a local file to store cache. 
    - Uses default boto3 settings for AWS Credentials
        - See: http://boto3.readthedocs.io/en/latest/guide/configuration.html
    - Especially useful if you desire to setup the script to update S3 based on a cron,
        and use another instance to read from S3. 
    - This would provide faster views of unread messages at the cost of some latency due to cache interval.
    - Example: 
        - Cron at 5+ min interval `python hipchat.py S3 NODETAILS`
        - Read from S3: `python hipchat.py S3 CACHE`


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

### AWS Lambda

The main script, `hipchat.py` can also be run as a AWS Lambda function, with its output saved to S3. 
An API setup in the AWS API Gateway can then return the info saved in S3, presumably the most 
recent status (within 15 min, based on the event config below)

- This would provide faster views of unread messages at the cost of some latency due to cache interval.

> - This is effectively, the same as setting up a cron at 5+ min interval: `python hipchat.py S3 NODETAILS`
> - To read from S3: `python hipchat.py S3 CACHE`

- Create a Lambda function, with a scheduled event.
- To make things easier, select the blueprint: `lambda-canary` as below:
    - Configure Event source
        - Event source type: `CloudWatch Events - Schedule`
        - Rule name: `hipchatunread`
        - Schedule expression: `rate(15 minutes)`
    - Configure function
        - Name: `hipchat-unread`
        - Code: use the default
        - Runtime: `Python 2.7`
        - Handler: `lambda_function.lambda_handler`
        - Role: `Basic with DynamoDB`
        - Memory: `128` mb
        - Timeout: `3` min `0` sec
        - VPC: `No VPC`
- Once setup,
    - Setup a virtual environment using the `requirements.txt` package list
    - Run `bin/lambda-package.sh`
    - Upload `lambda.zip` 
        - Manually via the upload UI, or
        - Run `bin/lambda-deploy.sh`
    - Update
        - Handler: `hipchat.lambda_handler`
    - Run `Test`
    - If executed correctly, schedule/push to Production
- To read from the S3 cache 
    - Read from S3: `python hipchat.py S3 CACHE`
