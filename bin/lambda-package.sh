#!/bin/sh

rm -rf ./lambda.zip

rm -rf ./target
mkdir ./target
cp ./hipchat.py ./target/
cp ./hipchat.conf ./target/
cp -r $VIRTUAL_ENV/lib/python2.7/site-packages/ ./target/

cd ./target/

zip -r9 ../lambda.zip *
