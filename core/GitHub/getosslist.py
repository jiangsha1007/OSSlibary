from bs4 import BeautifulSoup
from core.common import *
from model.common_model import *
import json
import requests
from core.request_header import *
import re


class GitHub:
    def __init__(self):
        manager = get_thread_task_queue('github_queue')
        self.task_queue = manager.github_queue()

    def get_oss_list(self, id):
        '''
        for i in range(10):
            p = multiprocessing.Process(target=self.get_info_from_api, args=(self.task_queue, i,))
            p.start()
        '''
        flag = True
        url = 'https://api.github.com/repositories'
        while flag:
            retrurn_info = get_html_json(url, getHeader())
            html_text = retrurn_info[0]
            header_text = retrurn_info[1]

            self.get_oss_name(html_text, id)
            listLink_next_url = re.findall(r'(?<=<).[^<]*(?=>; rel=\"next)', str(header_text))
            if len(listLink_next_url) > 0:
                url = listLink_next_url[0]
            else:
                flag = False

        #p.join()

    def get_oss_name(self, repos_data, id):
        for repos_per_data in repos_data:
            item = dict()
            item['oss_fullname'] = repos_per_data['full_name']
            item['oss_name'] = repos_per_data['name']
            item['oss_repo_url'] = repos_per_data['url']
            item['community_id'] = str(repos_per_data['id'])
            item['community_from'] = id
            item['oss_description'] = repos_per_data['description']

            repo_url = repos_per_data['url']
            repo_data = get_html_json(repo_url, getHeader())[0]
            try:
                item['oss_create_time'] = repo_data['created_at']
            except BaseException as e:
                item['oss_create_time'] = ''
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
            OsslibMetedata(**item)