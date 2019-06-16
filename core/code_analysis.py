from model.common_model import *
from core.common_git import *
from core.datacollector import *
from core.common import *

# 代码分析
class CodeAnalysis:
    def __init__(self):
        manager = get_thread_task_queue('getcoude_queue')
        self.task_queue = manager.getcoude_queue()

    # 获取代码
    def get_code(self):
        for i in range(10):
            p = multiprocessing.Process(target=self._get_code_process, args=(self.task_queue, i,))
            p.start()
        oss_info = OsslibMetedata.select(OsslibMetedata.q.oss_git_url != "")
        for per_oss_info in oss_info:
            if per_oss_info.oss_git_url != '':
                trans_info = []
                trans_info.append(per_oss_info.oss_name)
                trans_info.append(per_oss_info.oss_git_url)
                trans_info.append(per_oss_info.oss_git_tool)
                trans_info.append(per_oss_info.id)
                self.task_queue.put(trans_info)
        p.join()


    @staticmethod
    def _get_code_process(q, i):
        while True:
            info = q.get()
            oss_name = info[0]
            oss_git_url = info[1]
            oss_git_tool = info[2]
            oss_id = info[3]
            return_info = -1
            if oss_git_tool == 'bit':
                return_info = get_repo_by_git('data/'+oss_name, 'git://git.code.sf.net' + oss_git_url)
            elif oss_git_tool == 'SVN':
                return_info = get_repo_by_svn('data/' + oss_name, 'svn://svn.code.sf.net' + oss_git_url)
            if return_info == 1:
                oss_info = OsslibMetedata.get(oss_id)
                oss_info.oss_local_path = 'data/' + oss_name

    def code_analysis(self):
        oss_info = OsslibMetedata.get(3023)
        prevdir = os.getcwd()
        #for per_oss_path in oss_info:
        if oss_info.oss_local_path != '':
            try:
                gitpath = oss_info.oss_local_path
                absgitpath = os.path.abspath(gitpath)
                data = GitDataCollector()
                data.collect(absgitpath)
                print(data.getTotalLOC())
            except BaseException as ex:
                print(ex)
                pass
            finally:
                os.chdir(prevdir)