#!/bin/bash

if [ -n "$PYTHONPATH" ]; then
    export PYTHONPATH=${PYTHONPATH}:${PWD}/libraries
else
    export PYTHONPATH=${PWD}/libraries
fi
