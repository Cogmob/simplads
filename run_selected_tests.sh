#!/bin/bash
echo 'running selected tests'
nosetests --with-progressive . -a 's'
