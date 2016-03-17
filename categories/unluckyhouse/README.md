### 工具程式
程式 | 用途
---- | ----
syncid.py | 取得最新的討論串 ID
autofill.py | 自動化資料整理程式
geocoding.py | 地址定位程式

### 資料屬性

#### SQLite 3 資料庫
tag | 用途
---- | ----
id | 台灣凶宅網主題編號
age | 年齡
age_unit | 嬰兒使用月、足歲使用年 (M:月、Y:年)
gender | 性別 (M:男、F:女)
initiative | 主動程度 (S:自殺、M:謀殺、A:意外)
approach | 死因 (墜樓、跳樓、燒炭、上吊、情殺、凶殺、受虐、灌漿 ...)
news | 最佳新聞連結 (優先性: 影片 > 道路照片 > 照片 > 無照片)
area | 區域 (直轄市、縣)
address | 事發地址 (通常是不完整地址)
datetime | 事發時間，使用 ISO 8601 格式台灣時間，含時區標記 +0800
state | 資料完整度 -3~3 (見下表)
lat | 緯度
lng | 經度
vplat | 觀察點緯度
vplng | 觀察點經度
vpazu | 觀察點方位角
mtime | 資料更新時間

##### 資料完整度 (state) 說明:
* 0: 取得主題 id，尚未蒐集資料
* 1: 資料已蒐集
* 2: 已定位
* 3: 已設定觀察點 (街景服務用)
* -1: 主題已下架
* -2: 非凶宅資訊
* -3: 定位困難

#### 僅 GeoJSON 使用
tag | 用途
---- | ----
title | 地標簡述
url | 台灣凶宅網連結
view | Google 街景連結
marker-color | 圖釘顏色，一律使用 #b00000
marker-symbol | 圖釘圖示，確定地點使用 danger，不確定地點使用

### 單筆資料範例
```json
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [經度, 緯度]
      },
      "properties": {
        "id": "0000",
        "url": "http://unluckyhouse.com/showthread.php?t=0000",
        "address": "地址",
        "event": "事件",
        "datetime": "日期",
        "marker-color": "#b00000",
        "marker-symbol": "danger"
      }
    }
```
