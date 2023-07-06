from django.shortcuts import render
from django.http import HttpResponse
import sys
import os
import json
# Create your views here.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
import main

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


def getFolderList(request):
    unique_id=request.GET.get('unique_id',None)
    lazy_file_hash=request.GET.get('lazy_file_hash',None)
    content = main.childs(unique_id=unique_id,lazy_file_hash=lazy_file_hash)
    dic={
        'files': content[0],
        'folders': content[1]
    }
    return HttpResponse(json.dumps(dic))

