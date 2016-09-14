#!/usr/local/bin/python3
# coding: utf-8

import os
import re
import csv

## 新北市專用的列資料過濾器
def kaohsiung_filter(row = None, ignore_error = True):
    if row is None:
        return ['dt_exe', 'doc_id', 'corp', 'boss', 'law', 'cnt_action', 'cnt_rule']

    # 日期格式轉西元 (以後會用到)
    m = re.match('(\d+)/(\d+)/(\d+)', row[4])
    if m is not None:
        dstr = '%4d-%02d-%02d' % (
            int(m.group(1)) + 1911,
            int(m.group(2)),
            int(m.group(3))
        )
    else:
        exit(0)

    # 法條名稱簡化
    # 第24條 => 24
    # 第30條第2項 => 30-2
    law = re.sub('第(\d+)條', '\g<1>', row[2])
    law = re.sub('第(\d+)項', '-\g<1>', law)
    law = re.sub('[^\d\-\;]', '', law)

    # 計數
    # 稽查次數與違反法條數
    action_cnt = 1
    rule_cnt = law.count(';') + 1

    # 不用計算的欄位對應
    doc_id = row[3]
    corp   = row[1]
    boss   = ''

    filtered = [
        dstr,
        doc_id,
        corp,
        boss,
        law,
        action_cnt,
        rule_cnt
    ]
    return filtered

SRC_FILE = 'merged.csv'
DEST_FILE = 'history.csv'
IGNORE_ERROR = True

ci = open(SRC_FILE, 'r', encoding='utf-8')
co = open(DEST_FILE, 'w', encoding='utf-8')
r = csv.reader(ci)
w = csv.writer(co)

i = 0
curr_row = None
for row in r:
    if i > 0:
        if row[0] == '':
            curr_row[2] = '%s;%s' % (curr_row[2], row[2])
        else:
            if curr_row is not None:
                filtered = kaohsiung_filter(curr_row, IGNORE_ERROR)
                if filtered != False:
                    w.writerow(filtered)
                else:
                    print('事業名稱解析失敗 %d %s' % (i, row[3]))
            curr_row = row
    else:
        w.writerow(kaohsiung_filter())
    i = i + 1

# 處理最後一筆
filtered = kaohsiung_filter(curr_row, IGNORE_ERROR)
if filtered != False:
    w.writerow(filtered)
else:
    print('事業名稱解析失敗 %d %s' % (i, row[3]))

co.close()
ci.close()
