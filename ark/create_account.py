import json
import logging
import random
import re
import urllib
from typing import List
import time
import MySQLdb
import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession

current_account = 'company1'
fb = 'b'
print(urllib.parse)
def use_logging(func, **kwargs):
    def wrapper():
        logging.warn("%s is running" % func.__name__)
        return func()
    return wrapper

def login(session_id, **kwargs) -> requests.Response:
    return helper.get_session().post(backend_url + session_id + "/Member/DoLogin", data=kwargs, headers=req_headers)

def add_member(session_id, payload)->requests.Response:
    return helper.get_session().post(backend_url + session_id + "/Member/AddMember", data=payload, headers=req_headers)

def add_member2(session_id, **kwargs) -> requests.Response:
    return helper.get_session().post(backend_url + session_id + "/Member/AddMember", data=kwargs, headers=req_headers)

def get_member_list(session_id,**kwargs)-> requests.Response:
    return helper.get_session().get(backend_url_in_game + session_id + "/Member/GetMemberList",params=kwargs , headers=req_headers)
    
def get_lower_members(session_id, **kwargs) -> requests.Response:
    return helper.get_session().get(backend_url+ session_id + "/Member/GetLowerMembers",params=kwargs , headers=req_headers)

def get_member_data(session_id, **kwargs) -> requests.Response:
    return helper.get_session().get(backend_url + session_id + "/Member/GetMemberData",params=kwargs , headers=req_headers)

 
#with MySQLdb.connect(host="192.168.50.208",
#    user="root", passwd="123456", db="FzCompany1") as db_conn:


class Node():
    def __init__(self, value, level, parent):
        self.value = value         
        self.childs = []
        self.level = level
        self.parent = None


    
def dfs_traversal(root: Node):
    if not root:
        return
    dfs_traversal(root.lchild)
    
    
def build_nry_branch_accounts(session_id, current_level, parent_id, max_level, branch, credit, queue):
    def get_account_name(level, index) -> str:
        #example : L06_000033
        return 'L{:02d}_{:06d}'.format(level, index)
    def get_last_account_index(level)->int:
        res = sql_get_simple_last_member_account(level)
        print(res[4:])
        return 0 if not res else int(res[4:])
    def find_new_account_name(level) -> str:
        return get_account_name(level, get_last_account_index(level)+1)

    if current_level > max_level:
        return
    if not queue:
        return
    new_account_name = queue.pop(0)
    #new_account_name = find_new_account_name(current_level)
    
    new_member = new_member_creator(current_level, parent_id, '1', new_account_name, random_string(6), '123fff', [credit,credit,credit])
    r = add_member(session_id, new_member)
    last_account_index = get_last_account_index(current_level)
    print(r.request.body, r.json())
    while r.json()['Status'] == 2 and r.json()['Data'] == '此账号已存在，请更换账号':
        last_account_index += 1
        new_account_name = get_account_name(current_level, last_account_index)
        new_member = new_member_creator(current_level, parent_id, '1', new_account_name, random_string(6), '123fff', [credit,credit,credit])
        r = add_member(session_id, new_member)
        print(r.request.body, r.json())


    if r.json()['Status'] == 1 and current_level < max_level :        
        new_parent_id = sql_get_simple_member_id(new_account_name) 
        for i in range(branch):
            queue.append(get_account_name(current_level+1, get_last_account_index(current_level + 1) + 1) )
            build_nry_branch_accounts(session_id, current_level + 1, new_parent_id, max_level, branch, credit // branch, queue)


def random_string(string_length=10):
    import string
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(string_length))
    


def query_sql(sql):
    db_conn = MySQLdb.connect(host="192.168.50.208", user="root", passwd="123456", db="FzCompany1", charset="utf8")
    cursor = db_conn.cursor()
    cursor.execute(sql)    
    results = cursor.fetchall()
    return results


navi_url = "http://navigation.com/"
backend_url = "http://b1.bfz.com:82/"
backend_url_in_game = "http://1b1.bfz.com:84/"
req_headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'Accept': 'application/json, text/javascript',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-TW,en-US;q=0.7,ja;q=0.3',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache'
    }

def sql_get_simple_last_member_account(level) -> str:
    # example: L06_000033
    sql = 'SELECT M.Account FROM Member AS M WHERE M.MemberLevel= \"{}\"  AND M.Account LIKE \"L{:02d}\_%\" ORDER BY M.MemberID DESC LIMIT 1'.format(level,level)
    query = query_sql(sql)
    return query[0][0] if query else None

def sql_get_simple_member_id(account:str)->str:
    sql = 'SELECT M.MemberId FROM Member AS M where M.Account = \'{}\''.format(account)
    query = query_sql(sql)
    return query[0][0] if query else None

def sql_get_members_from_parent_id(parent_id:str)->List:
    sql = 'SELECT M.MemberId FROM Member AS M where M.ParentId = \'{}\''.format(parent_id)
    query = query_sql(sql)
    return query if query else None

def sql_get_simple_member_account_from_id(member_id: str) -> str:
    sql = 'SELECT M.Account FROM Member AS M where M.MemberId = \'{}\''.format(member_id)
    query = query_sql(sql)
    return query[0][0] if query else None

class SessionHelper():
    def __init__(self):
        pass
    
    def set_session(self, session):
        self.session = session
    
    def get_session(self):
        return self.session

    def set_session(self, session):
        self.session = session

helper = SessionHelper()
def new_member_creator(member_level,parent_id,money_type,account,nick_name,login_pwd,credit:List[int]):    
    payload=f'Member={{"MemberLevel":"{member_level}","ParentId":"{parent_id}","MoneyType":"{money_type}","Account":"{account}","NickName":"{nick_name}","LoginPwd":"{login_pwd}","MustChangePwd":"0","MemberCredits":[{{"GroupId":1,"Amount":"{credit[0]}"}},{{"GroupId":2,"Amount":"{credit[1]}"}},{{"GroupId":3,"Amount":"{credit[2]}"}}]}}'
    #payload='Member={"MemberLevel":"1","ParentId":"0","MoneyType":"1","Account":"test11111","Nickname":"test11111","LoginPwd":"123fff","MemberCredits":[{"GroupId":1,"Amount":"1"},{"GroupId":2,"Amount":"1"},{"GroupId":3,"Amount":"1"}]}'
    return payload

def new_member_creator2(member_level,parent_id,money_type,account,nick_name,login_pwd,credit:List[int]):
    return f'{{MemberLevel":"{member_level}","ParentId":"{parent_id}","MoneyType":"{money_type}","Account":"{account}","NickName":"{nick_name}","LoginPwd":"{login_pwd}","MemberCredits":[{{"GroupId":1,"Amount":"{credit[0]}"}},{{"GroupId":2,"Amount":"{credit[1]}"}},{{"GroupId":3,"Amount":"{credit[2]}"}}]}}'


def main():
    with HTMLSession() as session:
        helper.set_session(session)
        r = session.get(navi_url + "App/TestSpeed", params={"SafeCode": "222"}, headers=req_headers)
        r.encoding = 'utf-8'
        links=[]
        for i in r.html.absolute_links:
            links.append(i)
        token = re.findall(re.compile('Token=([^="]+)'), links[0])[0]
        r = session.get(links[random.randint(0, 8)])
        session_id = re.findall(re.compile('var\sSID\s=\s"([^"]*)";'), r.text)[0]
        r = login(session_id, account="company1", password="123fff", token=token)
        #print(r.request.body)
        #print(r.text)
        token = r.json()['Data']['Token']    
        r = session.get(url=backend_url + session_id + "/App/Index", headers=req_headers)    
        r = session.head(url=backend_url_in_game + "App/Index", params={'Token': token}, headers=req_headers)
        if not 'Location' in r.headers.keys():
            exit(1)

        location = r.headers['Location']
        
        session_id_in = re.findall(re.compile('\/([^"A]+)\/'), location)[0]
        r = session.get(url=backend_url_in_game + location[1:], headers=req_headers)
        r = session.get(backend_url_in_game  + session_id_in + "/Member/GetMemberList", params={'memberlevel': '1', 'status': ''})
        #payload = new_member_creator('2', sql_get_simple_member_id('company1'), '1', 'L1_0000025', 'abcd12', '123fff', [100, 100, 100])
        #print(payload)
        req_headers.update({'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'})
        #r = add_member(session_id, payload)
        #print(r.request.body)
        #print(r.json())
        #r = session.get(backend_url_in_game + session_id_in + "/Member/GetMemberList", params={'memberlevel': '1', 'status': ''})
        #r = get_member_list(session_id_in, memberlevel='2', status='')
        
        #r = get_lower_members(session_id, memberlevel='2', create_level='2', pagesize='20')
        #r = get_member_data(session_id, MemberId='29')
        
        
        level = 1
        branch = 2
        max_level = 11
        credit = 1000000000
        parent_id = "0"
        
        
        for i in range(5):
            build_nry_branch_accounts(session_id,level,parent_id,max_level,branch,credit,['L01_{:06d}'.format(i+9)])
        




    

class Game_client:
    def __init__(self, **kwargs):        
        for k, v in kwargs.items():
            print(k, v)
        self.data = kwargs
        
    def print_kwargs(self,**kwargs):
        print(kwargs)

    def print_args(self,*args):
        print(args)

    def do_login(self, method='/Member/DoLogin', session=None, params=None):
        if not session:
            if not data['session']:
                session = HTMLSession()
                self.data['session'] = session
            else:
                session = data['session']
        session.post(self.data['base_url'] + method, params=params)
    
    #def close(self):
        #self.data['session'].close()

#mylist =['jack',"Shark", 4.5]
#a=Game_client(base_url=backend_url, fun={'a':True})
#a.close()

if __name__ == "__main__":
    
    main()
    #print (sql_get_simple_last_member_account(1))
