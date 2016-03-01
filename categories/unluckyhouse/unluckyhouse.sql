CREATE TABLE unluckyhouse (
	id INTEGER PRIMARY KEY,
	age INTEGER,
	age_unit CHAR(1) DEFAULT 'Y',
	gender CHAR(1) DEFAULT 'F',
	initative CHAR(1) DEFAULT 'S',
	approach VARCHAR(20),
	news TEXT,
	area VARCHAR(10),
	address VARCHAR(255),
	datetime DATETIME,
	state INTEGER DEFAULT 0,
	lat DOUBLE DEFAULT 25.0,
	lng DOUBLE DEFAULT 119.5,
	mtime DATETIME DEFAULT (datetime('now', 'localtime'))
);