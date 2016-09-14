-- 匯入各行政區資料
.separator ','

/*
.import data/taipei/history.csv taipei
INSERT INTO unluckylabor (
   gov, doc_id, dt_exe, law, corp, boss, cnt_action, cnt_rule
) SELECT
   '臺北市', doc_id, dt_exe, law, corp, boss, cnt_action, cnt_rule
FROM taipei;
DROP TABLE IF EXISTS taipei;

.import data/newtaipei/history.csv newtaipei
INSERT INTO unluckylabor (
   gov, doc_id, dt_exe, law, corp, boss, cnt_action, cnt_rule
) SELECT
   '新北市', doc_id, dt_exe, law, corp, boss, cnt_action, cnt_rule
FROM newtaipei;
DROP TABLE IF EXISTS newtaipei;
*/

.import data/kaohsiung/history.csv kaohsiung
INSERT INTO unluckylabor (
   gov, doc_id, dt_exe, law, corp, boss, cnt_action, cnt_rule
) SELECT
   '高雄市', doc_id, dt_exe, law, corp, boss, cnt_action, cnt_rule
FROM kaohsiung;
DROP TABLE IF EXISTS kaohsiung;
