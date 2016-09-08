-- 新建資料庫
CREATE TABLE IF NOT EXISTS unluckylabor (
   id         INTEGER PRIMARY KEY, -- 流水號
   gov        VARCHAR(5),          -- 地方政府代碼
   exe_id     VARCHAR(25),         -- 公文編號
   exe_date   DATE,                -- 執行日期
   law_id     VARCHAR(25),         -- 法條編號
   law_detail TEXT,                -- 法條內容
   corp       VARCHAR(25),         -- 公司名稱
   corp_addr  VARCHAR(100),        -- 公司地址
   corp_boss  VARCHAR(25),         -- 負責人
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

