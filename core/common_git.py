from git import Repo
import os
import svn.remote
import svn.local

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

        #r = svn.local.LocalClient('F:/code/python/OSSlib/data/cloverefiboot')
        #info = r.info()

        r = svn.remote.RemoteClient(svn_url)
        os.mkdir(loacal_path)
        dir = "F:/code/python/OSSlib/"+loacal_path
        r.checkout(dir)
        return 1
    except BaseException as ex:
        print(ex)
        try:
            pass
            os.rmdir(loacal_path)
        except:
            pass
        return -1
