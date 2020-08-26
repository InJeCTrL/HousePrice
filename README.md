# HousePrice

> 海量点可视化城市二手房房屋单价分布情况

## 介绍

在各大二手房交易平台上找不到按房屋每平米价格做海量点的可视化网页，所以用写了爬虫获取链家上的二手房数据，并用高德GeoAPI获取住宅对应的经纬度，使用flask作为服务器。

为什么不提供房产估价功能？
> 这个确实是考虑过了，做了很多尝试，也试了很多参数，都没办法使验证集收敛到合理范围，所以目前有关估价的部分都注释掉了，仅留下海量点可视化。

## 目录结构

```
 HousePrice
|   DataProcesser.py	# 包含爬虫类、经纬度类、解析类
|   Server.py			# 服务器
|   train.py			# 用于训练dataset_info(目前没用)
|   GetData.py			# 调用DataProcesser的类获取数据
|   map.html			# 地图页
```

## 使用方法

1. 修改GetData.py

   按个人需求修改城市名，并将```xxx```替换为高德GeoAPI的Appkey

```python
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
```

2. 运行GetData.py爬取数据

```shell
python GetData.py
```

3. 运行Server.py启动服务器

```shell
python Server.py
```

4. 浏览器查看网页

```shell
http://127.0.0.1:5555
```

