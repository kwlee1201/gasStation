# 載入函式庫
from pyspark.sql.functions import count
from pyspark.sql.functions import countDistinct
from pyspark.sql.functions import sum
from pyspark.sql import functions as F
from pyspark.sql.window import Window

#
# 加油站服務類型站數統計表
#

# 來源路徑
inputPath = "/home/mywh/data/rawData"
# 來源資料
inputFile = "infoCpcGasStation.csv"
# 完整路徑和資料
inputFull = inputPath + "/" + inputFile

# 讀入來源資料
df = sqlContext.read.csv(inputFull, encoding = 'utf-8', header = "true")

# 表列要統計的欄位名稱
statColumn = ['類別', '縣市', '服務中心', '營業中', '國道高速公路',
              '無鉛92', '無鉛95', '無鉛98', '酒精汽油', '煤油', '超柴',
              '會員卡', '刷卡自助', '自助柴油站', '電子發票', '悠遊卡', '一卡通', 'HappyCash',
              '洗車類別']

# 
for idxCol in range(len(df.columns)):
  # 判斷是否要進行分類計數
  if (df.columns[idxCol] in statColumn):
    #
    df.columns[idxCol]
    # df.select(df[idxCol]).distinct().count()
    # 列出所有記錄
    for idxRow in df.groupBy(df.columns[idxCol]).agg(count(df.columns[idxCol])).collect():
      idxRow

#
# 車隊卡
#

# 來源路徑
inputPath = "/home/mywh/data/rawData"
# 來源資料
inputFile = "215Card.csv"
# 完整路徑和資料
inputFull = inputPath + "/" + inputFile
# 讀入來源資料
df215Card = sqlContext.read.csv(inputFull, encoding = 'utf-8', header = "true")

# 油品項目
# 113F 1209800	98無鉛汽油	
# 113F 1209500	95無鉛汽油
# 113F 1209200	92無鉛汽油	
# 113F 1229500	酒精汽油
# 113F 5100100	超級柴油	
# 113F 5100700	海運輕柴油	
# 113F 5100800  海運重柴油
productColumn = ['113F 1209800', '113F 1209500', '113F 1209200',
                 '113F 1229500',
                 '113F 5100100',
                 '113F 5100700' , '113F 5100800']

#
# 年度月油品（汽油/柴油）銷售總量
#

# 表列要統計的欄位名稱
statColumn = ['PNO', 'TDATE', 'QTY']

# 取出特定欄位
pDf215Card = df215Card.select(statColumn)
# 分離日期欄位的年及月至新欄位
tDf215Card = (pDf215Card.withColumn('TDATEYEAR', pDf215Card['TDATE'].substr(1, 4))
                        .withColumn('TDATEMONTH', pDf215Card['TDATE'].substr(5, 2)))

# 群組欄位
groupColumn = ['TDATEYEAR', 'TDATEMONTH', 'PNO']
# 第一次計算（汽油及柴油的各自總銷量）：根據｛產品｝欄位，計算｛年｝｛月｝的［汽油、柴油］的各自總銷量
firstGroupDf215Card = (tDf215Card
                       .where(tDf215Card.PNO.contains(productColumn[0]) |
                              tDf215Card.PNO.contains(productColumn[1]) |
                              tDf215Card.PNO.contains(productColumn[2]) |
                              tDf215Card.PNO.contains(productColumn[3]) |
                              tDf215Card.PNO.contains(productColumn[4]))
                       .groupBy(groupColumn)
                       .agg(sum(tDf215Card.QTY.cast('float')).alias('firstQty'))
                       .orderBy(groupColumn))
# 第二次計算（汽油及柴油的月總銷量）：根據［汽油、柴油］的各自總銷量欄位，計算｛年｝｛月｝的［汽油、柴油］的總銷量
secondGroupDf215Card = (firstGroupDf215Card
                        .groupBy(groupColumn[0], groupColumn[1])
                        .agg(sum(firstGroupDf215Card.firstQty.cast('float')).alias('secondQty'))
                        .orderBy(groupColumn[0], groupColumn[1]))

# 第三次計算（汽油及柴油的年總銷量）：根據［汽油、柴油］的各自總銷量欄位，計算｛年｝的［汽油、柴油］的總銷量
thirdGroupDf215Card = (secondGroupDf215Card
                       .groupBy(groupColumn[0])
                       .agg(sum(secondGroupDf215Card.secondQty.cast('float')).alias('thirdQty'))
                       .orderBy(groupColumn[0]))

# 印出結果
for idxRow in (tDf215Card
               .where(tDf215Card.PNO.contains(productColumn[0]) |
                      tDf215Card.PNO.contains(productColumn[1]) |
                      tDf215Card.PNO.contains(productColumn[2]) |
                      tDf215Card.PNO.contains(productColumn[3]) |
                      tDf215Card.PNO.contains(productColumn[4]))
               .groupBy(firstGroupColumn)
               .agg(sum(tDf215Card.QTY.cast('float')).alias('aQty'))
               .orderBy(firstGroupColumn)
               .collect()):
  idxRow

# 根據｛年｝｛月｝欄位，計算［汽油］的總銷量
# 印出結果
for idxRow in (tDf215Card
               .where(tDf215Card.PNO.contains(productColumn[0]) |
                      tDf215Card.PNO.contains(productColumn[1]) |
                      tDf215Card.PNO.contains(productColumn[2]) |
                      tDf215Card.PNO.contains(productColumn[3]))
               .groupBy(firstGroupColumn)
               .agg(sum(tDf215Card.QTY.cast('float')).alias('aQty'))
               .orderBy(firstGroupColumn)
               .collect()):
  idxRow

# 根據｛年｝｛月｝欄位，計算［柴油］的總銷量
# 印出結果
for idxRow in (tDf215Card
               .where(tDf215Card.PNO.contains(productColumn[4]))
               .groupBy(firstGroupColumn)
               .agg(sum(tDf215Card.QTY.cast('float')).alias('aQty'))
               .orderBy(firstGroupColumn)
               .collect()):
  idxRow

#
# 同期｛全部｜汽油｜柴油｝銷售總量
#

# 群組欄位
groupColumn = ['TDATEYEAR', 'TDATEMONTH']
# 根據｛年｝｛月｝［油品］欄位，計算 計算［全部］的總銷量
for idxRow in tDf215Card.groupBy(groupColumn).agg(sum(tDf215Card.QTY.cast('float'))).orderBy(groupColumn).collect():
  idxRow
# 根據｛年｝｛月｝欄位，計算［汽油］的總銷量
# 根據｛年｝｛月｝欄位，計算［柴油］的總銷量

#
# 去年度/本年度同期銷量差異
#

# 表列要統計的欄位名稱
statColumn = ['CUSAUNT', 'PNO', 'TDATE', 'QTY']
# 取出特定欄位
pDf215Card = df215Card.select(statColumn)
#
tDf215Card = (pDf215Card.withColumn('TDATEYEAR', pDf215Card['TDATE'].substr(1, 4))
                        .withColumn('TDATEMONTH', pDf215Card['TDATE'].substr(5, 2)))

# 群組欄位
groupColumn = ['CUSAUNT', 'TDATEYEAR', 'TDATEMONTH', 'PNO']
# 根據｛企業客戶｝｛年｝｛月｝欄位，計算［汽油］的總銷量
for idxRow in tDf215Card.groupBy(groupColumn).agg(sum(tDf215Card.QTY.cast('float'))).orderBy(groupColumn).collect():
  idxRow
  
#
# 去年度/本年度同期累計銷量差異
#

#
# 銷量佔所有企業客戶比例
#

#
# 年度自營站與加盟站銷量比重
#

#
# 銷量佔比前10大加油站
#

# 表列要統計的欄位名稱
statColumn = ['CUSAUNT', 'STDNO', 'TDATE', 'QTY']
# 取出特定欄位
pDf215Card = df215Card.select(statColumn)
#
tDf215Card = (pDf215Card.withColumn('TDATEYEAR', pDf215Card['TDATE'].substr(1, 4))
                        .withColumn('TDATEMONTH', pDf215Card['TDATE'].substr(5, 2)))

# 群組欄位
groupColumn = ['CUSAUNT', 'STDNO', 'TDATEYEAR', 'TDATEMONTH']
# 根據｛企業客戶｝｛加油站代號｝｛年｝｛月｝欄位，計算［全部］的總銷量
for idxRow in tDf215Card.groupBy(groupColumn).agg(sum(tDf215Card.QTY.cast('float'))).orderBy(groupColumn).collect():
  idxRow

#
# 與去年同期車隊卡差異
#

#
# 未使用代碼
#

# 根據 年、月、油品 欄位，計算 某年某月特定油品 次數
for idxRow in tDf215Card.groupBy(groupColumn).agg(count('PNO')).orderBy(groupColumn).collect():
  idxRow
