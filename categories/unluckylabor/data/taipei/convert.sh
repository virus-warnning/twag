#!/bin/bash

if [ -f unluckylabor.csv ]; then
    rm -f unluckylabor.csv
fi

iconv -f 'CP950' -t 'UTF-8' 6531343989.csv > unluckylabor.csv
sqlite3 unluckylabor.sqlite '.read convert.sql'
