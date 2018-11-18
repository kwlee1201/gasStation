# 載入環境
import findspark
findspark.init()
import pyspark
from pyspark.sql import SparkSession

# 載入函式庫
from pyspark.sql.functions import count
from pyspark.sql.functions import countDistinct
from pyspark.sql.functions import sum
from pyspark.sql.functions import desc
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# 來源路徑
inputPath = "/home/cpc/data/rawData"
# 來源資料
inputFile = "UBus215.csv"
# 完整路徑和資料
inputFull = inputPath + "/" + inputFile

# 讀入來源資料
df = sqlContext.read.csv(inputFull, encoding = 'utf-8', header = "true")

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
# RID, CTYPE, STDNO, PNO, UNT, LDATE, TDATE, QTY, STRNO, TNO,
# MRK3, MRK4, MRK5, TICKETNO, SHIP, CARNO, PNAME, TICKETTYPE, CUSAUNT, CUSMUNT,
# TTIME, CARDMNO, CTYPEMK, MILE, PRICE, CNO, BILLNO, ATYPE, ADATE, RDATE,
# MDATE, SID, YYMM, BPRICE, SPRICE, MK1, MK2, MK3, S3_SEQNO, ISLAND_NO,
# GUN_NO, EDC_VERSION

statColumn = ['PNO', 'TDATE', 'QTY']

# 取出特定欄位
pDf = df.select(statColumn)
# 分離日期欄位的年及月至新欄位
tDf = (pDf.withColumn('TDATEYEAR', pDf215Card['TDATE'].substr(1, 4))
.withColumn('TDATEMONTH', pDf215Card['TDATE'].substr(5, 2)))
