from django.urls import path
from . import views


urlpatterns = [   
    path('getFolderListAtDepth', views.getFolderListAtDepth, name='getFolderListAtDepth'),
    path('getFolderList',views.getFolderList,name="getFolderList"),
    path('db_search',views.db_search,name="db_search"),
    path('upload',views.upload,name='upload file or folder'),
    path('unique_id_is_up',views.unique_id_is_up,name="unique_id_is_up"),
]