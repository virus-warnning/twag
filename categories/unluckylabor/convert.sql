-- 匯入 CSV 為草稿
.separator ','
.import unluckylabor.csv draft

-- 目標格式
CREATE TABLE IF NOT EXISTS unluckylabor (
   id          INTEGER PRIMARY KEY,
   exe_id      VARCHAR(25),
   corperation VARCHAR(25),
   detail      TEXT,
   ref_law     TEXT,
   boss        VARCHAR(25),
   exe_date    DATE,
   lat         DOUBLE DEFAULT 0.0,
   lng         DOUBLE DEFAULT 0.0
);

-- 清空舊資料
DELETE FROM unluckylabor;

-- 對應到目標格式
-- 其中時間格式轉換如下
-- 1. 把 / 換成 -
-- 2. 年的前面補零，SQLite 只支援 YYYY-MM-DD 格式
-- 3. 年 +1911
INSERT INTO unluckylabor (
    exe_id,
    corperation,
    detail,
    ref_law,
    boss,
    exe_date
) SELECT
    `處分字號`,
    `事業單位名稱/自然人姓名`,
    `違反法規內容`,
    `違反勞動基準法條款`,
    `事業單位代表人`,
    date('0' || REPLACE(`處分日期`, '/', '-'), '+1911 years')
FROM draft ORDER BY `處分字號`;

-- 刪除草稿
DROP TABLE draft;
