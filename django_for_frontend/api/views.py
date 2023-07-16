from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
import main

def jsonify(s):
    return json.loads(s.replace("'",'"'))


def bytesConversion(size):
    units = ['B','KB','MB','GB','TB']

    unit = 0
    while(1024<=size):
        size/=1024
        unit+=1
    
    size = round(size,2)

    out = str(size) + units[unit]
    return out



def preprocess(content):

    units = ['B','KB','MB','GB','TB']

    for l in content:
        for i in range(len(l)):
            l[i][5] = jsonify(l[i][5])
            size = float(l[i][5]['Size'])
            l[i][5]['Size'] = bytesConversion(size)
    
    return content




@api_view(['GET'])
def getFolderListAtDepth(request):

    dic={
        "Status": 200,
        'files':[],
        'folders':[]
    }
    depth=request.GET.get('depth',None)
    folder=request.GET.get('folder',None)
    if(folder=='none'):
        folder=None

    temp=request.GET.get("depth", None)
    
    
    content=main.rows_at_depth(depth=int(depth),folder_name=folder)
    if(content[0]==False or content[1]==False):
        dic["Status"] = 404
        return HttpResponse(json.dumps(dic))
    content=preprocess(content)
    dic['files']=content[0]
    dic['folders']=content[1]
    return HttpResponse(json.dumps(dic))


@api_view(['GET'])
def getFolderList(request):
    
    dic={
        'Status': 200,
        'files': [],
        'folders': []
    }
    unique_id=request.GET.get('unique_id',None)
    lazy_file_hash=request.GET.get('lazy_file_hash',None)
    content = main.childs(unique_id=unique_id,lazy_file_hash=lazy_file_hash)
    if(content[0]==False or content[1]==False):
        dic["Status"] = 404
        return HttpResponse(json.dumps(dic))
    content = preprocess(content)
    
    dic['files'] = content[0]
    dic['folders']=content[1]
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
   
    dic={

         "Status": 201, #all symlink created successfully
        'successful_uploads':[]

    }
    data=json.loads(request.body.decode())
    
    content = main.upload(data['source_path'],os.path.realpath('./data/Normal/'+data['dest_path']))
    if(content[0]):
        dic['Status']=500

    dic['successful_uploads'] = content[1]
    return HttpResponse(json.dumps(dic))

    
@api_view(['GET'])
def getDashboard(request):
    data=main.dashboard_fxns.fetch_dashboard_db()
    return HttpResponse(data)

@api_view(['GET'])
def getDashboard_cache():
    return HttpResponse(main.dashboard_fxns.cache_fetcher())

@api_view(['POST'])
def updateDashboard_cache(request):
    main.dashboard_fxns.cache_updater(request.body.decode())
    return HttpResponse('updated')



@api_view(['GET'])
def unique_id_is_up(request):
    unique_id = request.GET.get('unique_id',None)
    content = main.uniqueid_is_up(unique_id)

    content[1] = bytesConversion(content[1] + '/s')

    dic={
        'is_available': content[0],
        'speed': content[1]
    }

    return HttpResponse(json.dumps(dic))