### 資料屬性

tag | 用途
---- | ----
age | 年齡
gender | 性別
event | 事件 (墜樓、跳樓、燒炭、上吊、情殺、凶殺、受虐、其他)
news | 新聞連結
url | 台灣凶宅網連結
address | 事發地址 (通常是不完整地址)
datetime | 事發時間，使用 ISO 8601 格式台灣時間
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
