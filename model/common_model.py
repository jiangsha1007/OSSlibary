from sqlobject import *
from conf import config_operate
uri = config_operate.get_dbconfig_uri()
sqlhub.processConnection = connectionForURI(uri)


# oss community api
class OsslibCommunityApi(SQLObject):
    community_name = StringCol(length=50, notNone=True)
    get_oss_list_api = StringCol(length=255, notNone=True)
    get_oss_single_api = StringCol(length=255, notNone=True)
    git_api = StringCol(length=255)


class OsslibMetedata(SQLObject):
    community_id = StringCol(length=50,)
    community_from = IntCol(length=11)
    oss_name = StringCol(length=50)
    oss_fullname = StringCol(length=100, unique=True)
    oss_create_time = StringCol(length=50)
    oss_git_url = StringCol(length=200)
    oss_git_tool = StringCol(length=30)
    oss_repo_url = StringCol(length=200)
    oss_homepage = StringCol(length=100)
    oss_license = StringCol(length=100)
    oss_description = StringCol(length=5000)
    oss_local_path = StringCol(length=50)
    oss_line_count = IntCol(length=50)
    oss_developer_count = IntCol(length=50)
    oss_file_count = IntCol(length=50)
    oss_commit_count = IntCol(length=50)
    oss_lastupdate_time = StringCol(length=50)

