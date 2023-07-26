from django.urls import path
from . import views


urlpatterns = [   
    path('getFolderListAtDepth', views.getFolderListAtDepth, name='getFolderListAtDepth'),
    path('getFolderList',views.getFolderList,name="getFolderList"),
    path('db_search',views.getParent,name="db_search"),
    path('upload',views.upload,name='upload file or folder'),
    path('unique_id_is_up',views.unique_id_is_up,name="unique_id_is_up"),
    path('download',views.download,name='download'),
    path('search_query',views.searchQuery,name="api call for search operation"),
    path('progress',views.reveive_progress,name="receive progress"),
    path('dashboard_entries',views.getDashboardEntries,name='dashboard entries'),
    
]