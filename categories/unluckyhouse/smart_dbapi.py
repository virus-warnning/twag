# coding: utf-8
import sqlite3

def dict_factory(cursor, row):  
	d = {}  
	for idx, col in enumerate(cursor.description):
		d[col[0]] = row[idx]
	return d

def connect(dbname, dbtype='sqlite3', dbhost='127.0.0.1', dbport=5432):
	conn = False
	if dbtype == 'sqlite3':
		conn = sqlite3.connect(dbname)
		conn.row_factory = dict_factory
	return conn
