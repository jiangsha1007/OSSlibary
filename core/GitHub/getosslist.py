from bs4 import BeautifulSoup
from core.common import *
from model.common_model import *
import json
import requests
from core.request_header import *
import re
import time
import base64


class GitHub:
    def __init__(self):
        manager = get_thread_task_queue('github_queue')
        self.task_queue = manager.github_queue()

    def get_oss_list(self, id):
        flag = True
        index = 0
        url = 'https://api.github.com/repositories?since=900000'
        while flag:
            '''
            params = 'query {' \
                     'repository (owner:"jiangsha1007",name:"OSSlibary")' \
                                                                      "{" \
                                                                      "name" \
                                                                      "}" \
                                                                      "}"
            retrurn_info = get_graphql('https://api.github.com/graphql', params, getHeader())
            print(retrurn_info)
            exit(0)
            
            '''
            try:
                retrurn_info = get_html_json(url, getHeader())
            except BaseException as ex:
                continue
            html_text = retrurn_info[0]
            header_text = retrurn_info[1]
            self.task_queue.put(html_text)
            listLink_next_url = re.findall(r'(?<=<).[^<]*(?=>; rel=\"next)', str(header_text))
            if len(listLink_next_url) > 0 and index <1:
                url = listLink_next_url[0]
            else:
                flag = False
            index += 1
        for i in range(20):
            p = multiprocessing.Process(target=self.get_oss_name, args=(self.task_queue, i,))
            p.start()
        p.join()

    def get_oss_name(self, q, id):
        while(True):
            repos_data = q.get()
            for repos_per_data in repos_data:
                if(OsslibMetadata.select(OsslibMetadata.q.oss_fullname == repos_per_data['full_name']).count() > 0 ):
                    continue
                item = dict()
                print(repos_per_data['id'])
                item['oss_fullname'] = repos_per_data['full_name']
                item['oss_name'] = repos_per_data['name']
                item['oss_repo_url'] = repos_per_data['url']
                item['community_id'] = repos_per_data['id']
                item['community_from'] = id
                item['oss_description'] = repos_per_data['description']

                repo_url = repos_per_data['url']
                try:
                    repo_data = get_html_json(repo_url, getHeader())[0]
                except:
                    continue
                try:
                    item['oss_create_time'] = repo_data['created_at']
                except BaseException as e:
                    item['oss_create_time'] = ''
                try:
                    item['oss_owner_id'] = int(repo_data['owner']['id'])
                except BaseException as ex:
                    item['oss_owner_id'] = 0
                try:
                    item['oss_owner_type'] = repo_data['owner']['type']
                except BaseException as ex:
                    item['oss_owner_type'] = ''
                try:
                    item['oss_size'] = int(repo_data['size'])
                except BaseException as ex:
                    item['oss_size'] = 0
                try:
                    item['oss_star'] = repo_data['stargazers_count']
                except BaseException as ex:
                    item['oss_star'] = 0
                if item['oss_star'] < 50:
                    continue
                try:
                    item['oss_main_language'] = repo_data['language']
                except BaseException as ex:
                    item['oss_main_language'] = ''
                try:
                    item['oss_homepage'] = repo_data['homepage']
                except BaseException as e:
                    item['oss_homepage'] = ''
                try:
                    item['oss_license'] = repo_data['license']['name']
                except BaseException as e:
                    item['oss_license'] = ''
                try:
                    item['oss_git_url'] = repo_data['clone_url']
                    item['oss_git_tool'] = 'Git'
                except BaseException as e:
                    item['oss_git_url'] = ''
                    item['oss_git_tool'] = ''
                try:
                    item['has_wiki'] = int(repo_data['has_wiki'])
                except BaseException as ex:
                    item['has_wiki'] = 0

                item['oss_lastupdate_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                readmeinfo = get_html_json(repos_per_data['url'] + "/readme", getHeader())[0]
                if len(readmeinfo) > 0 :
                    try:
                        readme =readmeinfo['content']
                        item['readme'] = str(base64.b64decode(readme), encoding="utf-8").replace('\r' ,'').replace('\n','').replace('\t','')
                        print(item['readme'])
                    except:
                        item['readme'] = ''

                OsslibMetadata(**item)
                topics_data = get_html_json(repos_per_data['url'] + "/topics", getHeader())[0]
                if len(topics_data) > 0:
                    topic_items = dict()
                    try:
                        for topic_name in topics_data['names']:
                            topic_items['oss_id'] = int(repos_per_data['id'])
                            topic_items['topic'] = topic_name
                            if (OsslibTopic.select(AND(OsslibTopic.q.oss_id == int(repos_per_data['id']),
                                                             OsslibTopic.q.topic == topic_name)).count() > 0):
                                pass
                            else:
                                OsslibTopic(**topic_items)
                    except BaseException as ex:
                        print(str(repos_per_data['id'])+'-' + str(ex))

    def updatereadme(self):
        oss_info = OsslibMetadata.select(OR(OsslibMetadata.q.readme =='',OsslibMetadata.q.readme ==None))
        for per_oss_info in oss_info:
            print(per_oss_info.community_id)
            item = dict()
            #item.update(id=per_oss_info.id)
            repo_url = "https://api.github.com/repos/" + per_oss_info.oss_fullname
            per_oss_info.oss_repo_url=repo_url
            try:
                readmeinfo = get_html_json(repo_url + "/readme", getHeader())[0]
            except:
                continue
            if len(readmeinfo) > 0:
                try:
                    readme = readmeinfo['content']
                    per_oss_info.readme = str(base64.b64decode(readme), encoding="utf-8").replace('\r', '').replace('\n',
                                                                                                               '').replace(
                        '\t', '')
                    print(per_oss_info['readme'])
                except:
                    pass
            #OsslibMetedata(**item)