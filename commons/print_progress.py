import sys

prev_len = 0

def console_strlen(msg):
	clen = 0
	for ch in msg:
		if ord(ch) < 128:
			clen = clen + 1
		else:
			clen = clen + 2
	return clen

def print_progress(msg):
	global prev_len
	print('\r' + ' ' * prev_len),
	prev_len = console_strlen(msg)
	print('\r' + msg),
	sys.stdout.flush()
