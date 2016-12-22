#coding=utf-8
'''
想要爬取的关键字列表存在 szrb.txt

'''
import re
import chardet
from datetime import datetime, timedelta
from time import strftime, sleep
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
import urllib,urllib2
import json

oriurl = 'http://epaper.subaonet.com/'#报纸的根地址
paperName_list = ['szrb', 'gswb', 'cssb']


# 网上很多，可以看说明
from_addr = 'your email address'
password = 'your email password'
to_addr = ["dst email list"]
smtp_server = 'server'

def getupdatetime():
    html = getHtml(oriurl)
    #print html
    post_timetmp = re.findall(r'<td align="left" height="25" class="fz-14 pad-l-10 " >(.*?)</td>', html, re.S)
    post_times = [] #所有报纸更新时间

    for j in post_timetmp[:11]:
         post_times.append(j.decode('u8')[0:4]+j.decode('u8')[5:7]+j.decode('u8')[8:10])
    shortnames = re.findall(r'paperType=(.*?)" class="cor-red">',html,re.S)

    result ={}
    result['szrb'] = post_times[0]
    result['gswb'] =post_times[1]
    result['cssb'] = post_times[2]

    return result

	
# 网上截取的代码
def getHtml(url):
    try:
        html_1 = urllib2.urlopen(url).read()
        mychar = chardet.detect(html_1)
        bianma = mychar['encoding']
        if bianma == 'utf-8' or bianma == 'UTF-8':
           #html=html.decode('utf-8','ignore').encode('utf-8')
           html=html_1
           return html
        elif bianma == 'gbk' or bianma == 'GBK' :
             html =html_1.decode('gbk','ignore').encode('utf-8')
             return html
        elif bianma == 'gb2312' or bianma=='GB2312':
             html =html_1.decode('gb2312','ignore').encode('utf-8')
             return html
    except:
        pass

# 获取报纸的页数
def getPages(html):
    pages = re.findall(r'</a><a href="(.*?)".*?', html, re.S)
    last_page_len = len(pages[-1])
    if last_page_len==11:
        return int(pages[-1][5:7])
    if last_page_len==10:
        return int(pages[-1][5:6])
    if last_page_len==12:
        return int(pages[-1][5:8])

#获取标题,内容
def getTitleUrl(html,paperName,timeToday_str,day_str):
     result =[]
     titles = re.findall(r'<Area shape="polygon" coords=.*?href=.*?title="(.*?)"', html, re.S)
     # print titles
     urls = re.findall(r'Area shape=.*?href="(.*?)"', html,re.S)
     len_title = len(titles)
     len_urls = len(urls)

     if len_title==len_urls:
         for i in range(0,len_title):
             try:
                url_in =oriurl + paperName+'/html/'+timeToday_str[0:7]+'/'+day_str +'/'+ urls[i]
                # print url_in
                content= getContent(url_in)
                # content = getContent('http://epaper.subaonet.com/gswb/html/2015-12/13/content_326473.htm')
                # print content
                for each in open(r'szrb.txt'):
                    line = unicode(each.strip(), 'u8')
                    if content and line in content:
                        # print line
                        # print url_in
                        result.append((line, url_in))
             except:
                 pass
     return result

# 获取正文内容
def getContent(url):
     html = getHtml(url)
     try:
        content = re.findall(r'<div class="article-content fontSizeSmall mar-lr-6" style="border-top:1px #d4d2d3 solid; line-height:28px; padding:10px; font-size:14px">(.*?)</div>.*?<div class',html,re.S)
        return  unicode(content[0], 'utf-8')
     except:
        return
def craw(paper_name,timeToday_str,day_str):
    # url = oriurl + paperName+'/html/'+timeToday_str[0:7]+'/'+day_str +'/'+ 'node_'+'%s'%i+'.'+'htm'
    result =[]
    base_url =  oriurl + paper_name+'/html/'+timeToday_str[0:7]+'/'+day_str +'/'+ 'node_'+'%s'%2+'.'+'htm'
    print 'base_url:',base_url
    base_html = getHtml(base_url)
    # print 'base_html',base_html
    page_nums = getPages(base_html)

    for i in range(2,page_nums+1):
        url = oriurl + paper_name+'/html/'+timeToday_str[0:7]+'/'+day_str +'/'+ 'node_'+'%s'%i+'.'+'htm'
        html = getHtml(url)# 每个url去请求，得到html
        try:
            res = getTitleUrl(html,paper_name,timeToday_str,day_str)#每个html里得到标题，和每个新闻的url，然后拿到url后去寻找正文
            result.append(res)
        except:
            pass
    return result

###发送邮件
def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr(( \
        Header(name, 'utf-8').encode(), \
        addr.encode('utf-8') if isinstance(addr, unicode) else addr))

def sendemail(from_addr,to_addr_list,new_info,password,smtp_server):
    msg = MIMEText(new_info, 'plain', 'utf-8')
    msg['From'] = _format_addr(u'苏州报社<%s>' % from_addr)
    msg['To'] = _format_addr(u'随便什么都可以 <%s>' % to_addr)
    msg['Subject'] = Header(u'每日新闻', 'utf-8').encode()

    server = smtplib.SMTP(smtp_server, 25)
    server.set_debuglevel(1)
    server.login(from_addr, password)
    for each in to_addr_list:
        server.sendmail(from_addr, [each], msg.as_string())
    server.quit()

# def main(time_post):
def main(timeToday_str,day_str):
        result = []
    # if time_post.get('szrb')==timetodaystr:
        res_szrb = craw('szrb',timeToday_str,day_str)
        for each in res_szrb:
            if each :
                result.append(each)
    # if time_post.get('gswb')==timetodaystr:
        res_gswb = craw('gswb',timeToday_str,day_str)
        for each1 in res_gswb:
            if each1 :
                result.append(each1)
    # if time_post.get('cssb')==timetodaystr:
        res_cssb = craw('cssb',timeToday_str,day_str)
        for each2 in res_cssb:
            if each2 :
                result.append(each2)
        str = ' '
        for name_urls in result:
            for name_url in name_urls:
                name = name_url[0]
                url = name_url[1]
                str = str+name.encode('u8')+":"+url+'\n'
        return str
if __name__=='__main__':
    # 9点55去爬取一次
    dt = ['0955']
    while 1:
         if strftime("%H%M") in dt:
             try:
                timeToday = datetime.now()-timedelta(days=0) # 今天的时间
                timeToday_str = timeToday.strftime("%Y-%m%d")
                day_str = timeToday_str[7:9]
                print timeToday_str,day_str
                res_str =  main(timeToday_str,day_str)
                sendemail(from_addr, to_addr, res_str, password, smtp_server)
             except:
			     # 如果9点55没爬到，一个小时后再去爬一次
                 sleep(3600)
                 timeToday = datetime.now()-timedelta(days=0) # 今天的时间
                 timeToday_str = timeToday.strftime("%Y-%m%d")
                 day_str = timeToday_str[7:9]
                 print timeToday_str,day_str
                 res_str =  main(timeToday_str,day_str)
                 sendemail(from_addr, to_addr, res_str, password, smtp_server)
