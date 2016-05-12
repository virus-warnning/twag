### 台灣人文地理資料整合

##### 資料範疇
* 與 OpenStreetMap 授權可能衝突
* 資料具有決策參考價值
* 資料具有歷史考證價值

##### 資料蒐集標準
* 通通變成 SQLite，有效資料轉為 [GeoJSON](https://en.wikipedia.org/wiki/GeoJSON)
* 確保資料中立性，避免因果關係與評論
* 描述僅限人事時地物與資料來源
* 地，使用 WGS84 座標
* 時，使用 ISO 8601 格式
* 人，遵循個資法避免使用姓名，公共事件除外
* 事物，下標處理
* 資料來源，盡可能使用 URL
 
##### 現有資料
資料類型 | 資料來源 | 網址 | 授權
---- | ---- | ---- | ----
非自然死亡 | 台灣凶宅網 | [HTML](http://unluckyhouse.com/showthread.php?t=7281) / [RSS 2.0](http://unluckyhouse.com/external.php) | ?
台北市違反勞基法事業名單 | 台北市政府勞動局 | [CSV](http://bola.gov.taipei/ct.asp?xItem=94627869&ctNode=76327&mp=116003) |
地籍資料 | 內政部 | [系統](http://easymap.land.moi.gov.tw/R02/Index) | ?
實價登錄 | 內政部 | [CSV](http://plvr.land.moi.gov.tw/DownloadOpenData) | [政1](http://data.gov.tw/?q=principle)
易發生婦幼被害犯罪地點 | 內政部 | [CSV](http://data.moi.gov.tw/MoiOD/Data/DataDetail.aspx?oid=DBB18796-8A89-4917-B4AB-D0AF26FAFEDC) | [政1](http://data.gov.tw/?q=principle)
土地段名代碼 | 內政部 | [XML](http://data.moi.gov.tw/MoiOD/Data/DataDetail.aspx?oid=151BCC68-3185-4D80-A3DE-88F2F647B445) | [政1](http://data.gov.tw/?q=principle)
台灣地區地名資料| 內政部 | [CSV](http://data.moi.gov.tw/MoiOD/Data/DataDetail.aspx?oid=72BA3432-7B07-4FF4-86AA-FD9213006920) | [政1](http://data.gov.tw/?q=principle)
地政事務所轄區圖 TWD97 121 分帶 | 內政部 | [SHP](http://data.moi.gov.tw/MoiOD/Data/DataDetail.aspx?oid=45B8A9CF-A2D0-4EC2-9168-BF96CD3C5CEB) | [政1](http://data.gov.tw/?q=principle)
台北市公托 | 台北市資訊局 | [XML](http://data.taipei/opendata/datalist/datasetMeta?oid=01ac5a1d-dfc3-44c7-84a7-6d76bcb2879b) | [政1](http://data.gov.tw/?q=principle)
台北市私托 | 台北市資訊局 | [XML](http://data.taipei/opendata/datalist/datasetMeta?oid=081df75e-85c7-464c-b125-546920911c5c) | [政1](http://data.gov.tw/?q=principle)

##### 有人做了
資料類型 | 資料來源 | 網址 | 授權
---- | ---- | ---- | ----
KMT 黨產 | kmt-exposed | [GeoJSON](https://github.com/kmt-exposed/kmt-exposed.github.io/tree/master/data) | CC0
台北市建物模型 GeoJSON | sheethub | [GeoJSON](https://github.com/sheethub/tpe3d/tree/master/geojsons) | [政1](http://data.gov.tw/?q=principle)

##### 願望
* 賄選事件

##### 輔助資源
* [GeoJSON 效果預覽](http://geojson.io/)
* [針對 Leaflet 最佳化](http://leafletjs.com/examples/geojson.html)
* [針對 Mapbox 最佳化](https://www.mapbox.com/help/markers/#customizing-markers)
* [marker-symbol 可用項目](https://www.mapbox.com/maki/)
