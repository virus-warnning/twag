-- 新建資料庫
CREATE TABLE IF NOT EXISTS unluckylabor (
   id         INTEGER PRIMARY KEY, -- 流水號
   gov        VARCHAR(5),          -- 地方政府代碼
   doc_id     VARCHAR(25),         -- 公文編號 (會重複!!)
   dt_exe     DATE,                -- 執行日期
   law        VARCHAR(25),         -- 法條編號
   corp       VARCHAR(25),         -- 公司名稱
   addr       VARCHAR(100),        -- 公司地址
   boss       VARCHAR(25),         -- 負責人
   cnt_action INTEGER,             -- 稽查行動計數
   cnt_rule   INTEGER,             -- 觸犯法條計數
   lat        DOUBLE DEFAULT 0.0,  -- 緯度
   lng        DOUBLE DEFAULT 0.0   -- 經度
);

-- 清空舊資料
DELETE FROM unluckylabor;
DROP TABLE IF EXISTS taipei;
DROP TABLE IF EXISTS newtaipei;

-- 匯入各行政區資料
.separator ','
.import data/taipei/history.csv taipei
.import data/newtaipei/history.csv newtaipei

-- 合併各行政區資料
INSERT INTO unluckylabor (
   gov, doc_id, dt_exe, law, corp, boss, cnt_action, cnt_rule
) SELECT
   'taipei', doc_id, dt_exe, law, corp, boss, cnt_action, cnt_rule
FROM taipei;

INSERT INTO unluckylabor (
   gov, doc_id, dt_exe, law, corp, boss, cnt_action, cnt_rule
) SELECT
   'newtaipei', doc_id, dt_exe, law, corp, boss, cnt_action, cnt_rule
FROM newtaipei;
