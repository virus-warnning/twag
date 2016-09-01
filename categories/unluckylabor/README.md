### 轉檔
```sh
iconv -f CP950 -t UTF-8 6531343989.csv unluckylabor.csv
sqlite3 -separator ',' unluckylabor.sqlite '.import unluckylabor.csv draft'
sqlite3 unluckylabor.sqlite '.schema'

CREATE TABLE draft(
  "公告日期" TEXT,
  "處分日期" TEXT,
  "處分字號" TEXT,
  "事業單位名稱/自然人姓名" TEXT,
  "事業單位代表人" TEXT,
  "違反勞動基準法條款" TEXT,
  "違反法規內容" TEXT,
  "備註" TEXT
);
```
* 其中處分字號可能重複，不要用來當主索引

### 目標格式
欄位名稱 | 型態 | 欄位用途
---- | ---- | ----
id | INTEGER | 主索引
exe_id | VARCHAR(25)| 處分字號
corperation | VARCHAR(25) | 資方
deatil | TEXT | 違反法規內容
ref_law | TEXT | 違反勞基法條款
boss | VARCHAR(10) | 事業單位代表人
exe_date | DATE | 處分日期 ISO 8601 (YYYY-MM-DD)
lat | DOUBLE | 緯度
lng | DOUBLE | 經度

### 資料來源

* 資料來源表依資料品質排序

地方政府 | 格式 | 數目 | 
---- | ---- | ---- | ----
[台北市政府](http://bola.gov.taipei/ct.asp?xItem=94627869&ctNode=76327&mp=116003) | PDF、CSV | >2000 |
[新北市政府](http://www.labor.ntpc.gov.tw/content/?parent_id=10433) | PDF、Excel | | 網頁翻到最後一頁才有載點，id 會跳
[台南市政府](http://www.tainan.gov.tw/labor/page.asp?nsub=M2A400) | Excel | |
[高雄市政府](http://labor.kcg.gov.tw/IllegalList.aspx?appname=IllegalList) | Excel | |
[基隆市政府](http://social.klcg.gov.tw/news/info_view.php?sid=417&dept_id=5&serno=20151210141036&page_num=1) | Excel | |
[嘉義市政府](http://www.chiayi.gov.tw/web/social/post.asp) | Excel | |
[宜蘭縣政府](http://labor.e-land.gov.tw/cp.aspx?n=A727524B27DA3181) | Excel | |
[新竹縣政府](http://labor.hsinchu.gov.tw/zh-tw/Duties/Detail/547/%E5%85%AC%E5%B8%83105%E5%B9%B43-4%E6%9C%88%E9%81%95%E5%8F%8D%E5%8B%9E%E5%8B%95%E5%9F%BA%E6%BA%96%E6%B3%95%E4%B9%8B%E4%BA%8B%E6%A5%AD%E5%96%AE%E4%BD%8D%E5%90%8D%E5%96%AE) | Excel | |
[苗栗縣政府](http://www.miaoli.gov.tw/labor_youth/normalIndex.php?forewordTypeID=0&frontTitleMenuID=4679) | PDF、Excel | |
[南投縣政府](http://www.nantou.gov.tw/big5/hotnewsdetail.asp?dptid=376480000AU130000&catetype=01&cid=1210&cid1=1694&mcid=84606) | Excel | |
[彰化縣政府](http://labor.chcg.gov.tw/07other/other01_con.asp?topsn=3197&data_id=14138) | Excel | |
[雲林縣政府](http://www4.yunlin.gov.tw/labor/home.jsp?mserno=200710140002&serno=200710140009&menudata=LaborMenu&contlink=ap/pubbulletin_view.jsp&dataserno=201403310006) | Excel | |
[嘉義縣政府](http://www.sabcc.gov.tw/informationlist.aspx?mid=248) | Excel、Calc | |
[屏東縣政府](http://www.pthg.gov.tw/planlab/Cus_PublicInfo_Detail.aspx?s=E452EBB48FCCFD71&n=9E2E4D61842FB8B2) | Excel | |
[台東縣政府](http://163.29.101.94/WebSite/Policy/information.aspx?menuid=mGlzPglzHMY%3d&dep=lW%2bfKiAxClc%3d&cate=cYTvoL0qNLc%3d&listall=1) | Excel | |
[花蓮縣政府](http://sa.hl.gov.tw/files/15-1037-44627,c3124-1.php) | PDF、Excel | |
[連江縣政府](http://www.matsu.gov.tw/2008web/news_cnt.php?id=2217&room=bbs) | Excel | |
[經濟部加工出口區總管理局](http://www.epza.gov.tw/list.aspx?pageid=4e5364e49d5b5094) | Excel | |
[新竹科學工業園區管理局](http://www.sipa.gov.tw/home.jsp?mserno=201001210016&serno=201001210016&menud%20ata=ChineseMenu&contlink=ap/download_view.jsp&dataserno=201504240001) | Calc | |
[桃園市政府](http://lhrb.tycg.gov.tw/home.jsp?id=373&parentpath=0%2C14%2C372&mcustomize=onemessages_view.jsp&dataserno=201509090001&aplistdn=ou=data,ou=lhrb4,ou=chlhr,ou=ap_root,o=tycg,c=tw&toolsflag=Y) | PDF | |
[台中市政府](http://www.labor.taichung.gov.tw/ct.asp?xItem=55333&ctNode=23053&mp=117010) | PDF | |
[新竹市政府](http://dep-labor.hccg.gov.tw/web/SelfPageSetup?command=display&pageID=21875&FP=D20000002106000002_2) | PDF | |
[澎湖縣政府](http://www.penghu.gov.tw/society/home.jsp?serno3=201302220001&mserno=201110140003&serno=201112150003&contlink=content/20130222113242.jsp&level2=Y) | Web | |
[中部科學園區管理局](http://www.ctsp.gov.tw/chinese/01news/10statistics_view.aspx?v=1&fr=529&no=538&sn=1198) | Web | |
[南部科學園區管理局](http://www.stsipa.gov.tw/web/WEB/Jsp/Page/cindex.jsp?frontTarget=DEFAULT&pageID=3985&thisRootID=206&PageNbr=1) | Web | |
[金門縣政府](http://web.kinmen.gov.tw/Layout/sub_F/AllInOne_Show.aspx?path=15316&guid=b42eee7c-e05c-40a5-ba98-761f9de353e5&lang=zh-tw) | (*.ashx) | |
