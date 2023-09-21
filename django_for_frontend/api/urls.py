from django.urls import path
from . import views


urlpatterns = [   
    path('getFolderListAtDepth', views.FetchFiles.getFolderListAtDepth, name='getFolderListAtDepth'),
    path('getFolderList',views.FetchFiles.getFolderList,name="getFolderList"),
    path('db_search',views.FetchFiles.getParent,name="db_search"),
    path('upload',views.Upload.upload,name='upload file or folder'),
    path('unique_id_is_up',views.Download.unique_id_is_up,name="unique_id_is_up"),
    path('download',views.Download.download,name='download'),
    path('search_query',views.FetchFiles.searchQuery,name="api call for search operation"),
    path('progress',views.Download.receive_progress,name="receive progress"),
    path('dashboard_entries',views.Dashboard.getDashboardEntries,name='dashboard entries'),
    path('currentDownloads',views.Dashboard.getCurrentDownloads,name="get current downloads"),
    path('set_username',views.UserInfo.setUsername,name="set username"),
    path('cache',views.Cache_remover.main,name="log and temp_folder remover"),
    path('openFileLocation',views.open_file_loc,name="open file location"),
]