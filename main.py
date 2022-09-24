from bs4 import BeautifulSoup
import requests
import time
import json
from datetime import datetime
import pandas as pd
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

'''
 crawler
 각 사이트마다 검색조건을 통해 게시물을 수집함
 ex) keyword = '강아지', site = 다음 블로그, startDate(수집시작일) = 2021-01-01, endDate(수집종료일) = 2021-04-20 
    ---> 다음블로그에서 2021-01-01 ~ 2021-04-20 기간 사이의 "강아지"가 들어간 게시물을 모두 수집하는 조건
    ---> 검색조건에 따라 url설정
'''
class Crawler:
    def __init__(self):
        self.keyword = 'ㅇㅎ' #수집 키워드
        self.site = '디시인사이드' # 수집 사이트
        self.startDate = '' #수집 시작일
        self.endDate = '' #수집 종료일
        self.url = 'https://search.dcinside.com/post/p/{page}/q/{keyword}' # 수집할 게시물리스트(게시판) url (검색조건(keyword, site, startDate, endDate)에 따라 설정)
        self.postUrls = []  # 게시판에서 게시물 url들을 담아 리턴할 리스트

    # 데이터에서 html tag 제외
    def delrn(self, text):
        return text.replace("\t","").replace("\n","").replace("\r","").lstrip().rstrip()

    def getList(self)-> list:

        lastPage = 120
        print('[ - ] lastPage = ', lastPage)
        #---

        # 첫페이지부터 마지막페이지까지
        for page in range(1, lastPage+1):
            res = requests.get(self.url.format(page=page,keyword=self.keyword), verify=False)
            print('[ * ] page -> '+ str(page) )
            dc = BeautifulSoup(res.text, 'html.parser')
            postlist = dc.find('ul',{'class':'sch_result_list'})


            # 게시물 리스트 url 가져오기 <사이트마다 태그변경 또는 소스코드 수정 필요>
            for a in postlist.findAll('a',{'class':'tit_txt'}):
                postInfor = {
                             'url': a.get('href'),
                             'crawled':False, # getPost()에서 해당url에서 게시물 상세정보를 가져왔는지 확인할 플래그
                            }
                # 수집되지 않은 url이면 append
                exist = next((item for item in self.postUrls if item['url'] == postInfor['url']), None)
                if type(exist) != dict: self.postUrls.append(postInfor)
                else: break
            break       
        print('[ - ] lenPostUrls = ', len(self.postUrls))


    def getPost(self)-> list:
        # 게시물 상세정보 수집 
        for post in self.postUrls:
            header = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9','Accept-Encoding': 'gzip, deflate, br','Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7','Connection': 'keep-alive','Cookie': 'wif_adx_pause=true; PHPSESSID=09bf96cbc8fe9b48a723f946145d117e; ci_c=a1d6eef54495bd458533ad7cb5e5f95f; adfit_sdk_id=bfb05359-a8d0-492c-b66b-df5e59f81371; __utma=118540316.1181677633.1619595048.1619595048.1619595048.1; __utmc=118540316; __utmz=118540316.1619595048.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); alarm_popup=1; _ga=GA1.2.1181677633.1619595048; _gid=GA1.2.1479690822.1619595461; __gads=ID=a0ba745170591a30:T=1619597263:S=ALNI_MbE1LzJyRVP9IBS-nuP9_5Q7josCQ; join_tip_box=Y; dable_uid=26071785.1619597316585; ck_lately_gall=Ao%7Cx7%7C1wo%7C1En%7Cxj; gallRecom=MjAyMS0wNC0yOCAxNzoxNDo1NS80MzU5ZTIxMjgwMmRjYjRjNWQxMmIzODcwM2I1MDQ0ZTg2ZDAxMjVlOGI1YzE0NzNjMTZiYTFjNTU3OGRhZjE2; service_code=21ac6d96ad152e8f15a05b7350a2475909d19bcedeba9d4face8115e9bc1fe4391cb7d15b902b36ee3a3efe4d783859b7ada787166d1b5da46363149a75871f7b22a0e2756fc54be0abe7be6c5591afcde6e44f101d3b7dcb49c5ccf700ae5f3180bab9b9dfd2cb7b330f862c0d60e45945eecd6ee6b1253bd5a843f7b7e2367112576834098eb7323bc986183f4c9e002c1647294ecd899e221fda4495e5a6a676bfbb5944cd04be25edfb0d32b9de63d1819a31da4a91fb82cf5a601c8d6a9787a125c4996d7211032; last_alarm=1619597896; wcs_bt=f92eaecbc22aac:1619597958; __utmt=1; __utmb=118540316.44.10.1619595048; _gat=1','Host': 'gall.dcinside.com','Referer': post["url"],'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"','sec-ch-ua-mobile': '?0','Sec-Fetch-Dest': 'document','Sec-Fetch-Mode': 'navigate','Sec-Fetch-Site': 'same-origin','Sec-Fetch-User': '?1','Upgrade-Insecure-Requests': '1','User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'}
            req = requests.get(post['url'], verify=False, headers=header)
            time.sleep(1)
            print('[ * ] post req -> '+post['url'])
            req.encoding='utf-8'
            soup = BeautifulSoup(req.text, 'html.parser')


            # --- 게시물의 제목/내용/작성자아이디/작성자닉네임/작성일자 등을 가져옴 <사이트마다 태그변경 또는 소스코드 수정 필요>
            post['title'] = self.delrn(soup.find('span',{'class':'title_subject'}).text)
            post['Content'] = self.delrn(soup.find('div',{'class':'write_div'}).text)
            userdata = soup.find('div',{'class':'gall_writer ub-writer'})
            if userdata['data-uid'] != "":
                post['userid'] = userdata['data-uid']
            else:
                try:
                    post['userid'] = userdata.find('span',{'class':'ip'}).text.replace("(","").replace(")","")
                except:
                    post['userid'] = ""
            post['username'] = soup.find('span',{'class':'nickname'}).text
            post['datePublished'] = datetime.strptime(soup.find('span',{'class':'gall_date'}).text, '%Y.%m.%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
            post['dateScraped'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 이미지가 있다면
            post['img'] = []
            try:
                for img in soup.find('ul',{'class':'appending_file'}).findAll('li'):
                    post['img'].append(img.find('a')["href"])
            except:None
            like = int(soup.find('p',{'class':'up_num font_red'}).text)
            try:
                hate = int(soup.find('p',{'class':'down_num'}).text)
            except:
                hate = 0
            post['like'] = like
            post['hate'] = hate
            # like(좋아요수) / hate(싫어요수) / reply(댓글수) / thumbnail(썸네일) 이 존재하면 수집

            # ---댓글을 수집해야하는 사이트면
            post['CmtCnt'] = None
            post['Comments'] = []
            
            year = datetime.strptime(soup.find('span',{'class':'gall_date'}).text, '%Y.%m.%d %H:%M:%S').strftime('%Y')


            gtype = post['url'].split('/')[3]
            if gtype == 'mini' : 
                gtype = 'MI'
                headers = {'Accept': 'application/json, text/javascript, */*; q=0.01','Accept-Encoding': 'gzip, deflate, br','Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7','Connection': 'keep-alive','Content-Length': '113','Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8','Cookie': 'PHPSESSID=a37824aa828d27826970ed60112355cf; adfit_sdk_id=31e09920-a32b-41f9-96f7-38970033af38; _ga=GA1.2.2133373173.1618563699; trc_cookie_storage=taboola%2520global%253Auser-id%3Df09a585a-0ee9-466c-862f-02230653baa8-tuct772d7f2; __utmc=118540316; alarm_popup=1; _cc_id=f01de2eefd3aa48f1455de3a2abc520a; remember_secret=%2FTp%2FBrq2hi; _gid=GA1.2.466498421.1619591177; panoramaId_expiry=1620196883665; panoramaId=4ee1931e0e4f687116c3f1e86f704945a7029e097245d2a79a9b59d45e34c0f6; ci_c=7fde5010d1d96a7ec8d12f3dc0988cbe; __utmz=118540316.1619659369.14.9.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utma=118540316.2133373173.1618563699.1619659369.1619673862.15; join_tip_box=Y; ck_lately_gall=1wo%7C7X%7C1QC%7CbP%7C1En; wcs_bt=f92eaecbc22aac:1619678252; __utmt=1; __utmb=118540316.60.10.1619673862; _gat_gtag_UA_10723182_19=1; last_alarm=1619678262; gallRecom=MjAyMS0wNC0yOSAxNTozODoyMS8yNjYwNTBkMTc3MzI1MDliNDczMTlkZDFhZGUxOGViZDk1MmRmOGYxZmExZjcyNTVjOTJkY2E4YzVlNjk1OWEy; service_code=21ac6d96ad152e8f15a05b7350a2475909d19bcedeba9d4face8115e9bc1fe421a74e2edae594abc9cf3097a880985800f0fffc1a9736bdd37dc07d95a1e26f91ebd843b46004a9c5a93a642645c7161f040d97f2c3214433758bd29a489a31605c4ee9eb06804c5123ab0bed16360db82bd3a9864c3a0f0e0995dbf3c25420acdedee4442eb7a327b34a53cc08ff4fa15f4bfc4c2c7a031dd8da3aafbf2123ac4d529d5e0406fbbc6c2b28c563ad37283cd8f54e63dd8004f84663e635dec2913d92df7e2; sf_ck_tst=test','Host': 'gall.dcinside.com','Origin': 'https://gall.dcinside.com','Referer': post['url'],'Sec-Fetch-Dest': 'empty','Sec-Fetch-Mode': 'cors','Sec-Fetch-Site': 'same-origin','User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36','X-Requested-With': 'XMLHttpRequest'}
            elif gtype == 'mgallery' : 
                gtype = 'M'
                headers = {'Accept': 'application/json, text/javascript, */*; q=0.01','Accept-Encoding': 'gzip, deflate, br','Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7','Connection': 'keep-alive','Content-Length': '110','Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8','Cookie': 'PHPSESSID=a37824aa828d27826970ed60112355cf; adfit_sdk_id=31e09920-a32b-41f9-96f7-38970033af38; _ga=GA1.2.2133373173.1618563699; trc_cookie_storage=taboola%2520global%253Auser-id%3Df09a585a-0ee9-466c-862f-02230653baa8-tuct772d7f2; __utmc=118540316; alarm_popup=1; _cc_id=f01de2eefd3aa48f1455de3a2abc520a; remember_secret=%2FTp%2FBrq2hi; _gid=GA1.2.466498421.1619591177; panoramaId_expiry=1620196883665; panoramaId=4ee1931e0e4f687116c3f1e86f704945a7029e097245d2a79a9b59d45e34c0f6; ci_c=7fde5010d1d96a7ec8d12f3dc0988cbe; last_alarm=1619658349; wcs_bt=f92eaecbc22aac:1619659368; __utmz=118540316.1619659369.14.9.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utma=118540316.2133373173.1618563699.1619600627.1619659369.14; __utmt=1; __utmb=118540316.2.10.1619659369; ck_lately_gall=5UL%7CbP%7C51g%7Cxj%7C5Lr; gallRecom=MjAyMS0wNC0yOSAxMDoyMzowMC8xOWNkZWNjNzNiZDZkZTFkZDNhZmJmNzg2ZWE0ZDhiZDY1ZDBhYjc4MjQyYzViYTg2NDU2MDExMzZlMTZlODVh; service_code=21ac6d96ad152e8f15a05b7350a2475909d19bcedeba9d4face8115e9bc1fe421a74e2edae594abc9cf3097a880985800f0fffc1a9736bdd37dc07d95a1e26f91ebd843b46004a9c5a93a642645c7161f040d97f2c3214433758bd29a489a31605c4ec9eb06c199b0c75eeefd02168d0af0f1ac11ef58a7d6836022c05c20cafd632b426bd36583f9655c570171cc153fba8091dcd72048f0ffe2601e6da31d9d44b6207d7ea789987a4ab6e53bb52b1af544d9d08ab4ac215103c26648f69a72ebca2; sf_ck_tst=test','Host': 'gall.dcinside.com','Origin': 'https://gall.dcinside.com','Referer': post['url'],'Sec-Fetch-Dest': 'empty','Sec-Fetch-Mode': 'cors','Sec-Fetch-Site': 'same-origin','User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36','X-Requested-With': 'XMLHttpRequest'}
            else : 
                gtype = 'G'
                headers = {'Accept': 'application/json, text/javascript, */*; q=0.01','Accept-Encoding': 'gzip, deflate, br','Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7','Connection': 'keep-alive','Content-Length': '110','Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8','Cookie': 'PHPSESSID=a37824aa828d27826970ed60112355cf; adfit_sdk_id=31e09920-a32b-41f9-96f7-38970033af38; _ga=GA1.2.2133373173.1618563699; trc_cookie_storage=taboola%2520global%253Auser-id%3Df09a585a-0ee9-466c-862f-02230653baa8-tuct772d7f2; __utmc=118540316; alarm_popup=1; _cc_id=f01de2eefd3aa48f1455de3a2abc520a; remember_secret=%2FTp%2FBrq2hi; _gid=GA1.2.466498421.1619591177; panoramaId_expiry=1620196883665; panoramaId=4ee1931e0e4f687116c3f1e86f704945a7029e097245d2a79a9b59d45e34c0f6; ci_c=7fde5010d1d96a7ec8d12f3dc0988cbe; last_alarm=1619658349; wcs_bt=f92eaecbc22aac:1619659368; __utmz=118540316.1619659369.14.9.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utma=118540316.2133373173.1618563699.1619600627.1619659369.14; __utmt=1; __utmb=118540316.2.10.1619659369; ck_lately_gall=5UL%7CbP%7C51g%7Cxj%7C5Lr; gallRecom=MjAyMS0wNC0yOSAxMDoyMzowMC8xOWNkZWNjNzNiZDZkZTFkZDNhZmJmNzg2ZWE0ZDhiZDY1ZDBhYjc4MjQyYzViYTg2NDU2MDExMzZlMTZlODVh; service_code=21ac6d96ad152e8f15a05b7350a2475909d19bcedeba9d4face8115e9bc1fe421a74e2edae594abc9cf3097a880985800f0fffc1a9736bdd37dc07d95a1e26f91ebd843b46004a9c5a93a642645c7161f040d97f2c3214433758bd29a489a31605c4ec9eb06c199b0c75eeefd02168d0af0f1ac11ef58a7d6836022c05c20cafd632b426bd36583f9655c570171cc153fba8091dcd72048f0ffe2601e6da31d9d44b6207d7ea789987a4ab6e53bb52b1af544d9d08ab4ac215103c26648f69a72ebca2; sf_ck_tst=test','Host': 'gall.dcinside.com','Origin': 'https://gall.dcinside.com','Referer': post['url'],'Sec-Fetch-Dest': 'empty','Sec-Fetch-Mode': 'cors','Sec-Fetch-Site': 'same-origin','User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36','X-Requested-With': 'XMLHttpRequest'}
            urls = post['url'].split('=')
            gall = urls[-2].replace('&no','')
            num = urls[-1]
            data = {
                    'id' : gall,
                    'no':num,
                    'cmt_id': gall,
                    'cmt_no':num,
                    'e_s_n_o':'3eabc219ebdd65fe3eef84e1',
                    'comment_page':'1',
                    'sort':'',
                    '_GALLTYPE_':gtype,
                    }
            res = requests.post('https://gall.dcinside.com/board/comment/', data=data, headers = headers)
            res.encoding = 'UTF-8'

            replycounter = 0
            cmtnum = 0
            if res.json()['comments'] == None : continue


            for cmt in res.json()['comments']:

                
                if cmt['name'] != '댓글돌이':
                    if 'video' in cmt['memo'] : memo = cmt['memo'].split("this, '")[1].split("'")[0]
                    elif 'dccon' in cmt['memo'] : memo = cmt['memo'].split('src="')[1].split('"')[0]
                    else : memo = cmt['memo'] 
                    if cmt['depth'] == 0:
                        if 'dccon' in cmt['memo'] : memo = cmt['memo'].split('src="')[1].split('"')[0]
                        else : memo = cmt['memo']
                        if cmt['user_id'] == "" : cid = cmt['ip']
                        else: cid = cmt['user_id']
                        try:
                            datec = datetime.strptime(year+cmt['reg_date'], '%Y%m.%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            datec = datetime.strptime(cmt['reg_date'],'%Y.%m.%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')

                        commentInfor = {'userid': cid,
                                        'username': cmt['name'] ,
                                        'datePublished': datec,
                                        'Content': memo,
                                        'reCmtCnt' : 0,
                                        'reComments':[],
                                        'no': cmtnum,
                                        }
                        cmtnum = cmtnum + 1
                        post['Comments'].append(commentInfor)
                        replycounter = replycounter+1
                    if cmt['depth'] == 1:
                        if 'dccon' in cmt['memo'] : memo = cmt['memo'].split('src="')[1].split('"')[0]
                        else : memo = cmt['memo']
                        if cmt['user_id'] == "" : cid = cmt['ip']
                        else: cid = cmt['user_id']
                        try:
                            datecr = datetime.strptime(year+cmt['reg_date'], '%Y%m.%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            datecr = datetime.strptime(cmt['reg_date'],'%Y.%m.%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                        cmtrnum = cmtnum - 1
                        reComments = {'userid': cid,
                                        'username': cmt['name'] ,
                                        'datePublished': datecr,
                                        'Content': memo,
                                        'no': cmtrnum
                                    }
                        replycounter = replycounter+1
                        for comments in post['Comments']:
                            if int(comments['no']) == int(reComments['no']):
                                comments['reCmtCnt'] = comments['reCmtCnt']+1
                                comments['reComments'].append(reComments)
                                del reComments['no']   
            for comment in post['Comments']: del comment['no']    


                

            # 해당 url 게시물 크롤링 완료
            post['CmtCnt'] = replycounter
            post['crawled'] = True
       

    def getCSV(self):
        today = datetime.now().now().strftime("%Y%m%d%H%M")
        pd.DataFrame(self.postUrls).to_csv(today+self.keyword+"_"+self.site+".csv", encoding='utf-8-sig')
        print('[ * ] getCSV terminated')


if __name__=="__main__":   
    # 크롤러
    c = Crawler()

    # getList -> list (게시물 url 수집)
    c.getList()

    # getPost-> list (게시물 url로부터 게시물 상세정보 수집)
    c.getPost()

    # CSV로 출력
    c.getCSV()