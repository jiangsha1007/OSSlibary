from git import Repo
import os
import svn
def get_repo_by_git(loacal_path, git_url):
    #Repo.init(loacal_path)  # 创建一个git文件夹
    try:
        clone_repo = Repo.clone_from(git_url, loacal_path)
        return 1
    except:
        try:
            os.rmdir(loacal_path)
        except:
            pass
        return -1

def get_repo_by_svn(loacal_path, svn_url):
    #Repo.init(loacal_path)  # 创建一个git文件夹
    try:
        r = svn.remote.RemoteClient(svn_url)
        r.checkout(loacal_path)
        return 1
    except BaseException as ex:
        print(ex)
        try:
            os.rmdir(loacal_path)
        except:
            pass
        return -1
