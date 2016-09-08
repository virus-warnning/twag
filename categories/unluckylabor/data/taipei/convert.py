#!/usr/local/bin/python3
# coding: utf-8

import os
import re
import csv

## 台北市專用的列資料過濾器
def taipei_filter(row = None, ignore_error = True):
    if row is None:
        return ['dt_exe', 'doc_id', 'corp', 'boss', 'law', 'cnt_action', 'cnt_rule']

    # 日期格式轉西元
    m = re.match('(\d+)/(\d+)/(\d+)', row[1])
    if m is not None:
        dstr = '%4d-%02d-%02d' % (
            int(m.group(1)) + 1911,
            int(m.group(2)),
            int(m.group(3))
        )
    else:
        exit(0)

    # 負責人姓名處理
    # ------------------------------
    # 蔡瑞玲（即大華聯合會計師事務所）
    # 太平洋野菜工房科技股份有限公司張君豪
    # 陳鉅洲（即大裕合署會計師事務所
    # 蒲正一〈即五福煤氣行〉
    # 徐淑琴（翠亨村名廈管理委員會）
    boss = row[4]
    corporation = row[3]
    if boss is '':
        m = re.match('(.+)[〈（\(]即?(.+)[\)）〉]', row[3])
        if m is not None:
            boss = m.group(1)
            corporation = m.group(2)
        else:
            m = re.match('(\w+有限公司)(\w+)', row[3])
            if m is not None:
                boss = m.group(2)
                corporation = m.group(1)
            else:
                if len(row[3]) <= 3:
                    boss = row[3]
                    corporation = ''
                else:
                    is_org = False
                    for s in ['公司', '基金會', '商行', '醫院', '診所', '飯店', '幼兒園', '分院', '所']:
                        if row[3].endswith(s):
                            is_org = True
                            break

                    if not is_org and not ignore_error:
                        return False

    # 法條名稱簡化
    # 第24條 => 24
    # 第30條第2項 => 30-2
    law = re.sub('第(\d+)條', '\g<1>', row[5])
    law = re.sub('第(\d+)項', '-\g<1>', law)
    law = re.sub('[^\d\-\;]', '', law)

    # 計數
    # 稽查次數與違反法條數
    action_cnt = 1
    rule_cnt = law.count(';') + 1

    filtered = [
        dstr,
        row[2],
        corporation,
        boss,
        law,
        action_cnt,
        rule_cnt
    ]
    return filtered

SRC_FILE = '683113371043.csv'
UTF8_FILE = 'temp.csv'
DEST_FILE = 'history.csv'
IGNORE_ERROR = True

cmd = 'iconv -f CP950 -t UTF-8 %s > %s' % (SRC_FILE, UTF8_FILE)
os.system(cmd)

ci = open(UTF8_FILE, 'r', encoding='utf-8')
co = open(DEST_FILE, 'w', encoding='utf-8')
r = csv.reader(ci)
w = csv.writer(co)

i = 0
for row in r:
    if i > 0:
        filtered = taipei_filter(row, IGNORE_ERROR)
        if filtered != False:
            w.writerow(filtered)
        else:
            print('事業名稱解析失敗 %d %s' % (i, row[3]))
    else:
        w.writerow(taipei_filter())
    i = i + 1

co.close()
ci.close()

cmd = 'rm -f %s' % UTF8_FILE
os.system(cmd)
