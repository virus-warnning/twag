#!/usr/local/bin/python3
# coding: utf-8

import os
import re
import csv

## 新北市專用的列資料過濾器
def newtaipei_filter(row = None, ignore_error = True):
    if row is None:
        return ['dt_exe', 'doc_id', 'corp', 'boss', 'law', 'cnt_action', 'cnt_rule']

    # 日期格式轉西元 (以後會用到)
    dtstr = row[4]
    m = re.match('(\d+)[\./](\d+)[\./](\d+)', dtstr)
    if m is not None:
        dstr = '%4d-%02d-%02d' % (
            int(m.group(1)) + 1911,
            int(m.group(2)),
            int(m.group(3))
        )
    else:
        m = re.match('(\d{3})(\d{2})(\d{2})', dtstr)
        if m is not None:
            dstr = '%4d-%02d-%02d' % (
                int(m.group(1)) + 1911,
                int(m.group(2)),
                int(m.group(3))
            )
        else:
            print('無法辨識日期格式: %s' % dtstr)
            exit(0)

    # 負責人姓名處理
    # ------------------------------
    # 麻煩項目：
    # 全勝實業社(李博仕)
    # 楊秋桂(即小箖髮廊)
    # 新偉國際管理顧問股份有限公司顧卓群
    boss = ''
    corporation = row[1]

    if len(corporation) <= 3:
        boss = corporation
        corporation = ''

    if boss == '':
        m = re.match('(.+)\(([^\)]+)\)', corporation)
        if m is not None:
            if m.group(2)[0] == '即':
                boss = m.group(1)
                corporation = m.group(2)[1:]
            else:
                boss = m.group(2)
                corporation = m.group(1)

    if boss == '':
        m = re.match('(.+公司)(.{2,5})', corporation)
        if m is not None:
            boss = m.group(2)
            corporation = m.group(1)

    # 法條名稱簡化
    # 第24條 => 24
    # 第30條第2項 => 30-2
    law = re.sub('第(\d+)條', '\g<1>', row[2])
    law = re.sub('第(\d+)項', '-\g<1>', law)
    law = re.sub('[^\d\-\;]', '', law)

    doc_id = row[3]

    # 計數
    # 稽查次數與違反法條數
    action_cnt = 1
    if row[0] == '':
        action_cnt = 0
    rule_cnt = 1

    filtered = [
        dstr,
        doc_id,
        corporation,
        boss,
        law,
        action_cnt,
        rule_cnt
    ]
    return filtered

SRC_FILE = 'merged.csv'
DEST_FILE = 'history.csv'
IGNORE_ERROR = False

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
