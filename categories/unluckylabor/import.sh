#!/bin/bash
DBFILE='unluckylabor.sqlite'

rm -f ${DBFILE}
sqlite3 ${DBFILE} < import.sql
