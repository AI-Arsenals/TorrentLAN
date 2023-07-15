from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
import sys
import os
import json
# Create your views here.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
import main

def jsonify(s):
    return json.loads(s.replace("'",'"'))

def preprocess(content):

    units = ['B','KB','MB','GB','TB']

    for l in content:
        for i in range(len(l)):
            l[i][5] = jsonify(l[i][5])
            size = float(l[i][5]['Size'])
            unit = 0
            while(1024<=size):
                size/=1024
                unit+=1
            
            size = round(size,2)

            l[i][5]['Size'] = str(size) + units[unit]
    
    return content




@api_view(['GET'])
def getFolderListAtDepth(request):
    depth=request.GET.get('depth',None)
    folder=request.GET.get('folder',None)
    if(folder=='none'):
        folder=None

    temp=request.GET.get("depth", None)
    
    
    content=main.rows_at_depth(depth=int(depth),folder_name=folder)
    content=preprocess(content)
    dic={}
    dic['files']=content[0]
    dic['folders']=content[1]
    return HttpResponse(json.dumps(dic))


@api_view(['GET'])
def getFolderList(request):
    
    unique_id=request.GET.get('unique_id',None)
    lazy_file_hash=request.GET.get('lazy_file_hash',None)
    content = main.childs(unique_id=unique_id,lazy_file_hash=lazy_file_hash)

    content = preprocess(content)
    
    dic={
        'files': content[0],
        'folders': content[1]
    }
    return HttpResponse(json.dumps(dic))


@api_view(['GET'])
def db_search(request):
    query_dict=request.GET
    # print(type(query_dict))
    content=main.db_search(list(query_dict.keys()),list(query_dict.values()))
    content[0][5] = jsonify(content[0][5])
    dic={'content':content}
    return HttpResponse(json.dumps(dic))


@api_view(['POST'])
def upload(request):
   
    data=json.loads(request.body.decode())
    print(data['source_path'])
    for index,item in  enumerate(data['dest_path']):
        data['dest_path'][index] = os.path.realpath(item)

    print(data['dest_path'])
    # main.upload(os.path.realpath(data['source_path']),os.path.realpath('./data/Normal/'+data['dest_path']))
    return HttpResponse('uploading file')
    

