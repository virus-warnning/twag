### 資料屬性

#### 共用
tag | 用途
---- | ----
id | 台灣凶宅網 post 編號
age | 年齡
age_unit | 嬰兒使用月、足歲使用年 (M:月、Y:年)
gender | 性別 (M:男、F:女)
initiative | 主動程度 (S:自殺、M:謀殺、A:意外)
approach | 死亡方式 (墜樓、跳樓、燒炭、上吊、情殺、凶殺、受虐、灌漿 ...)
news | 最佳新聞連結 (有影片 > 有道路照片 > 有照片 > 無照片)
area | 區域 (直轄市、縣)
address | 事發地址 (通常是不完整地址)
datetime | 事發時間，使用 ISO 8601 格式台灣時間，含時區標記 +0800
state | 資料完整度 -2~2，0: 機器人蒐集到 id、1: 整理事件資訊、2: 補充精確座標、-1: 被檢舉下架、-2: 非凶宅資訊

#### 僅 GeoJSON 使用
tag | 用途
---- | ----
title | 地標簡述
url | 台灣凶宅網連結
marker-color | 圖釘顏色，一律使用 #b00000
marker-symbol | 圖釘圖示，確定地點使用 danger，不確定地點使用 

### 資料產出流程
#### 自動化增加資料
1. 先產出 id, url 欄位
1. marker-symbol 預設 cross
1. marker-color 預設 #b00000
1. address、event、news 欄位空白
1. coordinates 暫定 ```[119.5, 25.0]``` (在海上)

#### 人工確認新聞
1. 確認人 (年齡、性別)
1. 確認是發時間 (datetime)
1. 確認事件 (死亡方式)

#### 精確定位
1. 追蹤新聞照片或影片
1. 利用街景服務取得經緯度與方位角
1. 確定精確位置後 marker-symbol 改為 danger

#### 輸出
1. 從 SQLite 轉換為 GeoJSON

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
