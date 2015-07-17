#!/bin/sh
export OPENSHIFT_MONGODB_DB_URL=mongodb://localhost:27017/
export OPENSHIFT_APP_NAME=codenamez1
python2.7 app.py