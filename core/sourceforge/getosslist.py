from bs4 import BeautifulSoup
from core.common import *
from model.common_model import *
import json
import requests
from multiprocessing import freeze_support


class SourceForge:
    def __init__(self):
        manager = get_thread_task_queue('sourceforge_queue')
        self.task_queue = manager.sourceforge_queue()

    def get_oss_list(self, id):
        freeze_support()

        for i in range(10):
            p = multiprocessing.Process(target=self.get_info_from_api, args=(self.task_queue, i,))
            p.start()
        for index in range(1, 800):
            html_text = get_html_text('https://sourceforge.net/directory/os:windows/os:mac/os:linux/?page={index}'.format(index=index))
            self.get_oss_name(html_text, id)
        p.join()

    def get_oss_name(self, html_text, id):
        html = BeautifulSoup(html_text, 'lxml')
        li_list = html.select('div.off-canvas-content > div.l-two-column-page > div.l-content-column > section > ul > li')

        for per_li_list in li_list:
            li_list_a = per_li_list.select('div.result-heading > div > a')
            if len(li_list_a):
                li_list_a_href = li_list_a[0]['href']
                item = dict()
                item['oss_name'] = li_list_a_href.split('/')[2]
                item['community_from'] = id
                return_cursor = OsslibMetadata(**item)
                trans_info = []
                trans_info.append(item['oss_name'])
                trans_info.append(return_cursor.id)
                self.task_queue.put(trans_info)

    def get_info_from_api(self, q, i):
        while True:
            info = q.get()
            api_url = "https://sourceforge.net/rest/p/"+info[0]
            response = requests.get(url=api_url)
            text = response.text
            try:
                jsonobj = json.loads(text)
            except:
                continue
            if jsonobj['status'] == 'moved':
                true_repo_url = jsonobj['moved_to_url']
            else:
                oss_info = OsslibMetadata.get(info[1])
                oss_info.oss_description = jsonobj['short_description']
                oss_info.community_id = jsonobj['_id']
                oss_info.oss_homepage = jsonobj['external_homepage']
                oss_info.oss_repo_url = jsonobj['url']
                oss_info.oss_create_time = jsonobj['creation_date']
                if 'tools' in jsonobj:
                    for tools in jsonobj['tools']:
                        if tools["mount_point"] == 'code':
                            oss_info.oss_git_url = tools['url']
                            oss_info.oss_git_tool = tools['tool_label']


