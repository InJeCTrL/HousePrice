import DataProcesser

# 获取链家二手房数据 -> dataset.csv
s = DataProcesser.Spider("北京")
s.crawl()

# 添加链家二手房住宅经纬度(高德API) -> dataset_geo.csv
l = DataProcesser.LocParser("dataset.csv", "北京", "xxx")
l.generate()
'''
# 解析二手房信息字段用于训练 -> dataset_info.csv
i = DataProcesser.InfoParser("dataset_geo.csv")
i.generate()
'''