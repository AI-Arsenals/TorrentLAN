from django.shortcuts import render
from django.http import HttpResponse,JsonResponse

from rest_framework.decorators import api_view
import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
import main


download_dic = {}

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


def clamp(n, min, max):
    if n < min:
        return min
    elif n > max:
        return max
    else:
        return n




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
def getParent(request):
    query_dict=request.GET
    dic={'Status': 200}
    # print(type(query_dict))
    content=main.db_search(list(query_dict.keys()),list(query_dict.values()))

    if(content==False):
        dic['Status']=500
    else:
        content[0][5] = jsonify(content[0][5])
    dic['content'] = content
    return HttpResponse(json.dumps(dic))


def searchQuery(request):
    query_dict=request.GET
    dic={'Status':200, 'files':[],'folders':[]}

    content=main.db_search(list(query_dict.keys()),list(query_dict.values()))
    print(content)
    if(content==False):
        dic['Status']=500



    else:
        for item in content:
            if(item[0]<0 or item[3]==1):
                continue
            item[5]=jsonify(item[5])
            if(item[2]==1):
                dic['files'].append(item)
            else:
                dic['folders'].append(item)

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
    print('content',content)
    new_content = [content[0],(bytesConversion(content[1])+'/s')]

    dic={
        'is_available': bool(new_content[0]),
        'speed': new_content[1]
    }

    return HttpResponse(json.dumps(dic))


@api_view(['POST'])
def download(request):
    data = json.loads(request.body.decode())
    global download_dic
    data['progress']=0
    download_dic[data['lazy_file_hash']] = list(data.values())
    content = main.download(data['unique_id'],data['lazy_file_hash'],data['table_name'],data['name'],data['file_loc'],f'http://127.0.0.1:8000/api/progress')
    print(download_dic)
    dic = {
        'staus': 1
    }

    return HttpResponse(json.dumps(dic))


@api_view(['GET'])
def reveive_progress(request):
    data=request.GET
    global download_dic
   
    lazy_file_hash = list(data.keys())[0]
    progress = float(data[lazy_file_hash])

    print(download_dic)
    prev = download_dic[lazy_file_hash][-1]
    print('prev',prev)
    download_dic[lazy_file_hash][-1] = clamp(progress,prev,100)


    
    return JsonResponse({
        'lazy_file_hash': lazy_file_hash,
        'updated_progress': download_dic[lazy_file_hash]
    })


@api_view(['GET'])
def getDashboardEntries(request):
    content = main.fetch_all_entries()

    dic={
        'Status':200

    }

    if(content==False):
        dic['Status']=500

    # else:
    #     for i in range(len(content)):
    #         content[i] = jsonify(content[i])


    dic['content'] = content
    return JsonResponse(dic)



    

    

    