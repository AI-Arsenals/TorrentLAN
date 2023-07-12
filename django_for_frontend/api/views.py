from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
import sys
import os
import json
# Create your views here.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
import main


@api_view(['GET'])
def getFolderListAtDepth(request):
    depth=request.GET.get('depth',None)
    folder=request.GET.get('folder',None)
    if(folder=='none'):
        folder=None

    temp=request.GET.get("depth", None)
    print(temp)
    
    content=main.rows_at_depth(depth=int(depth),folder_name=folder)
    dic={}
    dic['files']=content[0]
    dic['folders']=content[1]
    return HttpResponse(json.dumps(dic))


@api_view(['GET'])
def getFolderList(request):
    unique_id=request.GET.get('unique_id',None)
    lazy_file_hash=request.GET.get('lazy_file_hash',None)
    content = main.childs(unique_id=unique_id,lazy_file_hash=lazy_file_hash)
    dic={
        'files': content[0],
        'folders': content[1]
    }
    return HttpResponse(json.dumps(dic))


@api_view(['GET'])
def db_search(request):
    query_dict=request.GET
    # print(type(query_dict))
    content=main.db_seacrh(list(query_dict.keys()),list(query_dict.values()))

    dic={'content':content}
    return HttpResponse(json.dumps(dic))


@api_view(['POST'])
def upload(request):
   
    data=json.loads(request.body.decode())
    print(data['source_path'])
    main.upload(data['source_path'],'./data/Normal/Games')
    return HttpResponse('uploading file')
    

