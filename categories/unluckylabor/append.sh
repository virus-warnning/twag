#!/bin/bash
DBFILE='unluckylabor.sqlite'

sqlite3 ${DBFILE} < append.sql
