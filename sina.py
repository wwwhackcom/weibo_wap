
# coding: utf-8

# In[187]:


#-*-coding:utf-8-*-  
import requests
from lxml import etree
import time
import pickle


class Weibo:
    def __init__(self, userId, userName, content, picUrls=None, videoUrl=None):
        self.userId = userId
        self.userName = userName
        self.content = content
        self.commentCount = 0
        self.likeCount = 0
        self.postCount = 0
        self.picUrls = picUrls
        self.videoUrl = videoUrl
        
    def __repr__(self):
        return 'Weibo:{content:%s, picUrls:%s, like:%s, post:%s, comment:%s}\r\n'                 % (self.content, self.picUrls, self.likeCount, self.postCount, self.commentCount)
        

class Repost:
    def __init__(self, userId=None, userName=None, postContent=None, weibo=None):
        self.userId = userId
        self.userName = userName
        self.postContent = postContent
        self.postCnt = 0
        self.postLikeCnt = 0
        self.postCommentCnt = 0
        self.weibo = weibo
        self.datetime = 0
    
    def __repr__(self):
        return 'Repost:{postContent:%s, postCnt:%s, postLikeCnt:%s, postCommentCnt:%s, weibo:%r, datetime=%s}\r\n'                 % (self.postContent, self.postCnt, self.postLikeCnt, self.postCommentCnt, self.weibo, self.datetime)


def requestContent(url, cookies=None):
    data = requests.get(url, cookies=cookies)
    data.encode = "utf-8"
    content = data.content
    #print(data.text)
    trees = etree.HTML(content)
    return trees


def getMyWeibo(url, uId, uName, cookies):
    trs = requestContent(url, cookies)
    totalcount = int(trs.xpath('//*[@id="pagelist"]/form/div/input[1]/@value')[0])
    print(totalcount)
    time.sleep(2)
    posts = []
    
    for i in range(1, totalcount+1):
        s = requestContent(url + '?page=' + str(i), cookies)
        divs = s.xpath('//*[@class="c"][@id]')
        
        for div in divs:
            ret = 1
            try:
                orgId = div.xpath('./div[1]/span[@class="cmt"]/a/@href')[0]
            except IndexError as e:
                #print(e)
                ret = 0
            
            if (ret): #转发
                postContent = div.xpath('./div[2]/text()')[0]
                weiboPost = Repost(userId=uId, userName=uName, postContent=postContent)
                orgId = div.xpath('./div[1]/span[@class="cmt"]/a/@href')[0]
                orgName = div.xpath('./div[1]/span[@class="cmt"]/a/text()')[0]
                orgContent = div.xpath('./div[1]/span[@class="ctt"]/text()')[0]
                weibo = Weibo(orgId, orgName, orgContent)
                
                pic = div.xpath('./div[2]/a[1]/img')
                if (len(pic) > 0):  #转发有图
                    weiboPost.postLikeCnt = div.xpath('./div[3]/a[1]/text()')[0]
                    weiboPost.postCnt = div.xpath('./div[3]/a[2]/text()')[0]
                    weiboPost.postCommentCnt = div.xpath('./div[3]/a[3]/text()')[0]
                    weibo.likeCount = div.xpath('./div[2]/span[1]/text()')[0]
                    weibo.postCount = div.xpath('./div[2]/span[2]/text()')[0]
                    weibo.commentCount = div.xpath('./div[2]/a[3]/text()')[0]
                else:  #转发无图（或视频）
                    weiboPost.postLikeCnt = div.xpath('./div[2]/a[1]/text()')[0]
                    weiboPost.postCnt = div.xpath('./div[2]/a[2]/text()')[0]
                    weiboPost.postCommentCnt = div.xpath('./div[2]/a[3]/text()')[0]
                    weibo.likeCount = div.xpath('./div[1]/span[3]/text()')[0]
                    weibo.postCount = div.xpath('./div[1]/span[4]/text()')[0]
                    weibo.commentCount = div.xpath('./div[1]/a/text()')[0]
                    
                weiboPost.weibo = weibo
                weiboPost.datetime = div.xpath('//span[@class="ct"]/text()')[0]
                #print(weiboPost)
                
            else: #原创
                text = div.xpath('./div[1]/span/text()')
                weibo = Weibo(userId=uId, userName=uName, content=text[0])
                weiboPost = Repost(weibo=weibo)
                pic = div.xpath('./div[2]/a[1]/img/@src')
                if (len(pic) > 0):  #原创有图
                    weiboPost.weibo.picUrls = []
                    weibo.likeCount = div.xpath('./div[2]/a[3]/text()')[0]
                    weibo.postCount = div.xpath('./div[2]/a[4]/text()')[0]
                    weibo.commentCount = div.xpath('./div[2]/a[5]/text()')[0]
                    try:
                        picCount = div.xpath('./div[1]/a/text()')[0]
                        if (picCount.find("组图共") != -1):
                            pCnt = int(picCount[3:4])
                            picUrl = div.xpath('./div[1]/a/@href')[0]
                            
                            tr1 = requestContent(picUrl, cookies)
                            ds1 = tr1.xpath('/html/body/div')
                            for d1 in ds1:
                                t1 = d1.xpath('./a/text()')[0]
                                if (t1.find('原图') != -1):
                                    a1 = d1.xpath('./a/@href')[0]
                                    weiboPost.weibo.picUrls.append(a1)
                    except IndexError as e:
                        print(e)
                        
                else: #原创无图
                    weibo.likeCount = div.xpath('./div/a[1]/text()')[0]
                    weibo.postCount = div.xpath('./div/a[2]/text()')[0]
                    weibo.commentCount = div.xpath('./div/a[3]/text()')[0]
                    
                weiboPost.datetime = div.xpath('//span[@class="ct"]/text()')[0]
                #print(weiboPost.weibo)
        
        posts.append(weiboPost)
        time.sleep(1)
        
    return posts

def crawlAndSave(filename):
    cookies = {}
    ck = "SCF=AsyATdURFUwqR0ALNDVV3TpgCwAF_RMSdYLXbltyFQBdsIlVTPSqX3ip0ZvnxJicnwXAusL22_7-PdnbsURSG-U.; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhzxEwufGFeRC5BQvf27bS.5JpX5K-hUgL.Fo2NS0-fehnRSoM2dJLoI7DNUNUQqgSuqcv_; _T_WM=d94d65cac3f507b2c4410b7672f62b38; H5_INDEX=3; H5_INDEX_TITLE=wwwhackcom; SUB=_2A253QpMhDeRhGedJ7FcU8CbEzTuIHXVUzD1prDV6PUJbkdBeLUbAkW1NUdVbczHTB8ByP-9u6e-Mv16KFvQjyCKH; SUHB=0idq6FooN0f1lq; SSOLoginState=1514595185"
    for c in ck.split(';'):
        name,value = c.strip().split('=', 1)
        #print(name, value)
        cookies[name] = value
    #print(cookies)
    
    url = 'https://weibo.cn/1775508867/profile'
    ps = getMyWeibo(url, '1775508867', 'wwwhackcom', cookies)
    with open(filename,"wb+") as csvfile: 
        pickle.dump(ps, csvfile) # 序列化到文件

def readFile(filename):
    with open(filename,"rb+") as csvfile: 
        ps = pickle.load(csvfile) # 序列化到文件
    print(ps)
    
def mainFun():
    print("开始")
    filename = "tt.csv"
    #crawlAndSave(filename)
    readFile(filename)
    print("结束")

mainFun()

