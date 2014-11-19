#!/bin/bash
export LC_ALL="C"

OS=$(uname)
if [ "$OS" == "Darwin" ] ; then
	nosetests . 
	flake8 --ignore=E501 .
else
	watch -n 0.4 -- "nosetests . ; flake8 --ignore=E501 ."
fi
