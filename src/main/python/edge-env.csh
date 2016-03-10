#!/bin/csh

if $?PYTHONPATH then
    setenv PYTHONPATH ${PYTHONPATH}:${PWD}/libraries
else
    setenv PYTHONPATH ${PWD}/libraries
endif
