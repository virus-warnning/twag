#!/usr/local/bin/python3
# coding: utf-8

import os
import re
import csv

## 新北市專用的列資料過濾器
def newtaipei_filter(row = None, ignore_error = True):
    if row is None:
        return ['date', 'doc_id', 'corporation', 'boss', 'law', 'action_cnt', 'rule_cnt']

    # 日期格式轉西元 (以後會用到)
    '''
    m = re.match('(\d+)/(\d+)/(\d+)', row[1])
    if m is not None:
        dstr = '%4d-%02d-%02d' % (
            int(m.group(1)) + 1911,
            int(m.group(2)),
            int(m.group(3))
        )
    else:
        exit(0)
    '''
    dstr = row[5]

    # 負責人姓名處理
    # ------------------------------
    # 麻煩項目：
    # 陳立禹【即新北市私立國泰老人長期照顧中心(養護型)】
    # 顏美麗(即新北市私立可爾威德幼兒園)（代表人：顏美麗）
    boss = ''
    corporation = row[1]
    if boss is '':
        m = re.match('(.+)[〈（\(]即(.+)[\)）〉]', corporation)
        if m is not None:
            boss = m.group(1)
            corporation = m.group(2)
        else:
            m = re.match('(.+)[(（]代表人[：:](.+)[）)]', corporation)
            if m is not None:
                boss = m.group(2)
                corporation = m.group(1)
            else:
                # 保留偵錯設計
                pass

    # 法條名稱簡化
    # 第24條 => 24
    # 第30條第2項 => 30-2
    law = re.sub('第(\d+)條', '\g<1>', row[2])
    law = re.sub('第(\d+)項', '-\g<1>', law)
    law = re.sub('[^\d\-]', '', law)

    # 計數
    # 稽查次數與違反法條數
    action_cnt = 1
    if row[0] == '':
        action_cnt = 0
    rule_cnt = 1

    filtered = [
        dstr,
        row[4],
        corporation,
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
for row in r:
    if i > 0:
        filtered = newtaipei_filter(row, IGNORE_ERROR)
        if filtered != False:
            w.writerow(filtered)
        else:
            print('事業名稱解析失敗 %d %s' % (i, row[3]))
    else:
        w.writerow(newtaipei_filter())
    i = i + 1

co.close()
ci.close()
