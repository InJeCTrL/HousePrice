import requests
import bs4
import json
import time
import pandas as pd
import socket
import random
import re
from fake_useragent import UserAgent

class Spider:
    def __init__(self, city):
        ''' 爬取链家二手房数据
        city:       城市中文名(eg. 北京)
        '''
        # 标记初始化
        self.__initialized = False
        socket.setdefaulttimeout(60)
        # 随机UA
        self.__ua = UserAgent()
        # 城市中文名
        self.__city = city
        tDomain = self.__getDomainURL()
        if not tDomain[0] or not tDomain[0].find(".fang.lianjia.com") == -1:
            print("city name error or no second-hand data for this city")
            return
        # 省份名称
        self.__province = tDomain[1]
        # 域名网址
        self.__domainURL = tDomain[0][:-1]
        self.__header = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Connection": "keep-alive",
            "Host": self.__domainURL[8:],
            "User-Agent": ""
            }
        # 数据表头
        self.__dataset = pd.DataFrame(columns=["title", "link", "position", "houseinfo", "totalprice", "unitPrice"])
        # 用于爬取数据的URL列表
        self.__FinalURL = []
        self.__initialized = True

    def __getNotMobileUA(self):
        l = ["Android", "iPhone", "iPod", "iPad", "Windows Phone", "MQQBrowser"]
        tua = self.__ua.random
        while True:
            ok = True
            for li in l:
                if tua.find(li) != -1:
                    tua = self.__ua.random
                    ok = False
                    break
            if ok:
                break
        return tua

    def __getDomainURL(self):
        ''' 获取城市中文名对应的域名和省份名称
        '''
        page = self.__getbs4page("https://www.lianjia.com/city", False)
        citynode = page.find_all("div", attrs = {'class': 'city_recommend'})[2].find("a", text = self.__city)
        if citynode:
            return [citynode.get("href"), citynode.parent.parent.previous_sibling.previous_sibling.get_text().replace('\n', '').replace(' ', '')]
        else:
            return [None, None]

    def __getbs4page(self, URL, UseHeader = True):
        ''' 获取bs4解析后网页
        URL:       网页地址
        '''
        while True:
            try:
                if UseHeader:
                    self.__header["User-Agent"] = self.__getNotMobileUA()
                    response = requests.get(URL, headers = self.__header, timeout = 50)
                else:
                    response = requests.get(URL, timeout = 50)
                break
            except:
                print("Net Error")
        retdata = response.text
        response.close()
        page = bs4.BeautifulSoup(retdata, 'html.parser')
        # time.sleep(random.uniform(1, 6))
        return page

    def __getReqURLList(self):
        ''' 获取需要爬取的最终URL列表
        '''
        FirstList = []
        SecondList = []
        # 获取一级地域URL
        print("start fetching first menu")
        page = self.__getbs4page(self.__domainURL + "/ershoufang")
        areanode = page.find("div", attrs = {'class': 'm-filter'}).find("div", attrs = {'data-role': 'ershoufang'})
        for firstarea in areanode.find_all("a"):
            FirstList.append(self.__domainURL + firstarea.get("href"))
        print("first menu done")
        # 获取二级地域URL
        print("start fetching second menu")
        for firsturl in FirstList:
            page = self.__getbs4page(firsturl)
            areanode = page.find("div", attrs = {'class': 'm-filter'}).find("div", attrs = {'data-role': 'ershoufang'}).find_all("div")
            if len(areanode) == 1:
                if firsturl not in SecondList:
                    SecondList.append(firsturl)
            else:
                for secondarea in areanode[1].find_all("a"):
                    tURL = self.__domainURL + secondarea.get("href")
                    if tURL not in SecondList:
                        SecondList.append(tURL)
        print("second menu done")
        # 二级地域URL转最终URL列表
        print("start processing second menu by house count")
        n_second = len(SecondList)
        for index, secondurl in enumerate(SecondList):
            print("处理 %d / %d" % (index + 1, n_second))
            page = self.__getbs4page(secondurl)
            n_house = int(page.find("h2", attrs = {'class': 'total fl'}).find("span").get_text())
            # 大于3000套房, 按面积划分
            if n_house > 3000:
                self.__FinalURL.append(secondurl + "a1")
                self.__FinalURL.append(secondurl + "a2")
                self.__FinalURL.append(secondurl + "a3")
                self.__FinalURL.append(secondurl + "a4")
                self.__FinalURL.append(secondurl + "a5")
                self.__FinalURL.append(secondurl + "a6")
                self.__FinalURL.append(secondurl + "a7")
                self.__FinalURL.append(secondurl + "a8")
            # 1-3000套房, 直接可用
            elif n_house > 0:
                self.__FinalURL.append(secondurl)
        print("process second menu done")

    def crawl(self):
        ''' 开始获取
        '''
        if not self.__initialized:
            print("Initializing failed")
        else:
            print("get URL list...")
            self.__getReqURLList()
            n_url = len(self.__FinalURL)
            print("OK (len: %d)" % (n_url))
            print("Crawler Running...")
            for index, url in enumerate(self.__FinalURL):
                curPage = 1
                while True:
                    while True:
                        try:
                            page = self.__getbs4page(url + "pg" + str(curPage))
                            areanodes = page.find("div", attrs = {'class': 'm-filter'}).find("div", attrs = {'data-role': 'ershoufang'}).find_all("div")
                            addr_pre = self.__province + areanodes[0].find("a", attrs = {'class': 'selected'}).get_text()
                            addr_pre += areanodes[1].find("a", attrs = {'class': 'selected'}).get_text() if len(areanodes) > 1 else ""
                            pagedata = json.loads(page.find("div", attrs = {'class': 'page-box house-lst-page-box'}).get("page-data"))
                            total_page = pagedata["totalPage"]
                            curPage = pagedata["curPage"]
                            break
                        except:
                            continue
                    print("[" + str(index + 1) + " / " + str(n_url) + " URL] - [" + str(curPage) + " / " + str(total_page) + " Page]")
                    for info in page.find_all("div", attrs = {'class': 'info clear'}):
                        titlenode = info.find("a")
                        link = titlenode.get("href")
                        title = titlenode.get_text().replace(',', '，').replace('\n', ' ')
                        position = addr_pre + info.find("div", attrs = {'class': 'positionInfo'}).find_all("a")[0].get_text()
                        houseinfo = info.find("div", attrs = {'class': 'houseInfo'}).get_text().replace('\n', '')
                        totalprice = info.find("div", attrs = {'class': 'totalPrice'}).get_text()
                        unitPrice = info.find("div", attrs = {'class': 'unitPrice'}).get("data-price")
                        self.__dataset = self.__dataset.append({"title": title, "link": link, "position": position, 
                                                            "houseinfo": houseinfo, "totalprice": totalprice, "unitPrice": unitPrice},
                                                           ignore_index = True)
                    curPage += 1
                    time.sleep(random.uniform(1, 6))
                    if curPage > total_page:
                        break
            self.__dataset.to_csv("dataset.csv", index = None)
            print("dataset Saved")

class InfoParser:
    def __init__(self, file_path):
        ''' 解析信息条目并生成带有各信息列的CSV数据集
        file_path:      二手房数据集文件路径
        '''
        self.__file_path = file_path
        self.__initialized = False
        try:
            self.__dataset = pd.read_csv(file_path)
            self.__initialized = True
        except:
            print("Loading dataset error")
    def generate(self):
        ''' 生成目标CSV
        '''
        if self.__initialized:
            print("Start generating")
            dataset_info = pd.DataFrame()
            """
            info = self.__dataset["houseinfo"]
            dict = {}
            for s in info:
                aaa = s.split("|")
                if len(aaa) >= 5:
                    #aaa[4] = aaa[4][:aaa[4].index("(")] if aaa[4].find("(") != -1 else aaa[4]
                    dict[aaa[3]] = dict.get(aaa[3], 0) + 1
                else:
                    print(aaa)
            print(dict)
            """
            for irow, row_info in enumerate(self.__dataset["houseinfo"]):
                parts = row_info.split("|")
                full_hit = 0
                for part in parts:
                    part = part.strip()
                    # x室y厅
                    if part.find("室") != -1:
                        xy = re.findall(r"\d+", part)
                        if not xy or len(xy) != 2:
                            break
                        nRoom = xy[0]
                        nHall = xy[1]
                        full_hit += 1
                    # 房屋面积
                    elif part.find("平米") != -1:
                        s = re.findall(r"\d+\.?\d*", part)
                        if not s or len(s) != 1:
                            break
                        Square = s[0]
                        full_hit += 1
                    # 装修程度
                    elif part in ["毛坯", "简装", "精装"]:
                        if part == "毛坯":
                            deco = 1
                        elif part == "简装":
                            deco = 2
                        elif part == "精装":
                            deco = 3
                        full_hit += 1
                    # 所在楼层和总楼层数
                    elif any(f in part for f in ["高楼层", "中楼层", "低楼层", "顶层", "底层"]):
                        if part.startswith("高楼层"):
                            floor = 1
                        elif part.startswith("中楼层"):
                            floor = 2
                        elif part.startswith("低楼层"):
                            floor = 3
                        elif part.startswith("顶层"):
                            floor = 4
                        elif part.startswith("底层"):
                            floor = 5
                        tf = re.findall(r"\d+", part)
                        if not tf or len(tf) != 1:
                            break
                        Totalfloor = tf[0]
                        full_hit += 1
                    # 楼栋类型
                    elif part in ["塔楼", "板楼", "板塔结合", "平房"]:
                        if part == "塔楼":
                            btype = 1
                        elif part == "板楼":
                            btype = 2
                        elif part == "板塔结合":
                            btype = 3
                        elif part == "平房":
                            btype = 4
                        full_hit += 1
                    # 朝向
                    elif any(p in part for p in ["东", "南", "西", "北"]):
                        FaceScore = 0
                        faces = part.split(" ")
                        for face in faces:
                            if face == "东":
                                FaceScore += 1
                            elif face == "南":
                                FaceScore += 2
                            elif face == "西":
                                FaceScore += 4
                            elif face == "北":
                                FaceScore += 8
                            elif face == "东北":
                                FaceScore += 16
                            elif face == "西北":
                                FaceScore += 32
                            elif face == "东南":
                                FaceScore += 64
                            elif face == "西南":
                                FaceScore += 128
                        full_hit += 1
                if full_hit == 6:
                    dataset_info = dataset_info.append({"nRoom": nRoom, "nHall": nHall, "Square": Square, 
                                                        "Face": FaceScore,
                                                        "Decoration": deco, "floor": floor, 
                                                        "Totalfloor": Totalfloor, "btype": btype,
                                                        "lat": self.__dataset.loc[irow, "lat"],
                                                        "lnt": self.__dataset.loc[irow, "lnt"], 
                                                        "unitPrice": self.__dataset.loc[irow, "unitPrice"]},
                                                       ignore_index = True)
            dataset_info.to_csv("dataset_info.csv", index = None)
            print("dataset_info Saved")
        else:
            print("Initializing failed")

class LocParser:
    def __init__(self, file_path, city, ak):
        ''' 由二手房数据生成带有经纬度的CSV数据集
        file_path:      二手房数据集文件路径
        city:           城市名 (eg. 北京)
        ak:             高德apikey
        '''
        self.__file_path = file_path
        self.__city = city
        self.__ak = ak
        self.__initialized = False
        try:
            self.__dataset = pd.read_csv(file_path)
            self.__initialized = True
        except:
            print("Loading dataset error")
    def generate(self):
        ''' 生成目标CSV
        '''
        if self.__initialized:
            print("Start generating")
            dataset_geo = pd.DataFrame()
            szData = len(self.__dataset)
            for i in range(0, szData, 10):
                print(str(i + 1) + " / " + str(szData))
                ads = ""
                for j in range(i, min(i + 10, szData)):
                    ads += self.__dataset.iloc[j]['position'] + '|'
                ads = ads[:-1]
                response = requests.get("https://restapi.amap.com/v3/geocode/geo?key=" + self.__ak + "&batch=true&city=" + self.__city + "&address=" + ads)
                retdata = response.text
                response.close()
                retjson = json.loads(retdata)
                geolist = retjson["geocodes"]
                for j in range(len(geolist)):
                    if not len(geolist[j]["location"]) == 0:
                        latlnt = geolist[j]["location"].split(',')
                        self.__dataset.loc[i + j, 'lat'] = latlnt[1]
                        self.__dataset.loc[i + j, 'lnt'] = latlnt[0]
                        dataset_geo = dataset_geo.append(self.__dataset.iloc[i + j])
                    else:
                        print("UNKNOWN GEO")
            dataset_geo.to_csv("dataset_geo.csv", index = None)
            print("dataset_geo Saved")
        else:
            print("Initializing failed")
    