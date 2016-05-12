### 轉檔
```!sh
iconv -f CP950 -t UTF-8 6531343989.csv unluckylabor.csv
sqlite3 -separator ',' unluckylabor.sqlite '.import unluckylabor.csv draft'
sqlite3 unluckylabor.sqlite '.schema'

CREATE TABLE draft(
  "公告日期" TEXT,
  "處分日期" TEXT,
  "處分字號" TEXT,
  "事業單位名稱/自然人姓名" TEXT,
  "事業單位代表人" TEXT,
  "違反勞動基準法條款" TEXT,
  "違反法規內容" TEXT,
  "備註" TEXT
);
```
