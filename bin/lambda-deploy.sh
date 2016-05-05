#!/bin/sh

aws lambda update-function-code \
    --function-name hipchat-unread \
    --zip-file fileb://lambda.zip
