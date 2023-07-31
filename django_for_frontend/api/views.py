from django.shortcuts import render
from django.http import HttpResponse,JsonResponse

from rest_framework.decorators import api_view
import sys
import os
import threading
import json
import queue

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

    processed_content={}
    content=list(content)
    print(content)
    for index,item in enumerate(content[0]):
        
        hash = item[8]
        
        if(hash in processed_content):
            processed_content[hash][7].append(item[7])
        else:
            temp=[]
            temp.append(item[7])
            item[7]=temp
            processed_content[hash] = item

    content[0] = list(processed_content.values())

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
    unique_ids = request.GET.get('unique_id', None)
    unique_ids = unique_ids.split(',')
    print(unique_ids)

    results = queue.Queue()

    threads = []
    def helper_unique_up(id, results):
        content = main.uniqueid_is_up(id)
        results.put(content)

    for id in unique_ids:
        thread = threading.Thread(target=helper_unique_up, args=(id, results))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    AVAILABLE = False
    TOTAL_SPEED = 0

    while not results.empty():
        top = results.get()
        AVAILABLE |= top[0]
        TOTAL_SPEED += top[1]

    new_content = [AVAILABLE, (bytesConversion(TOTAL_SPEED) + '/s')]

    dic = {
        'is_available': bool(new_content[0]),
        'speed': new_content[1]
    }

    return HttpResponse(json.dumps(dic))


@api_view(['POST'])
def download(request):
    data = json.loads(request.body.decode())
    global download_dic
    data['percentage']=0
    download_dic[data['lazy_file_hash']] = data
    

    for d in data:
        print(d,type(data[d]))


    content = main.download(data['unique_id'][0],data['lazy_file_hash'],data['table_name'],data['name'],"data/Normal/Games",'http://127.0.0.1:8000/api/progress')
    print(content[0],type(content[0]))
    dic = {
        'status': content[0]
    }
    



    return HttpResponse(json.dumps(dic))


@api_view(['GET'])
def receive_progress(request):
    data=request.GET
    global download_dic
   
    lazy_file_hash = list(data.keys())[0]
    progress = float(data[lazy_file_hash])

    try:
        prev = download_dic[lazy_file_hash]['percentage']
        progress = clamp(progress,prev,100)

        if(progress==100):
            download_dic.pop(lazy_file_hash)
        else:
            download_dic[lazy_file_hash]['percentage'] = progress
    
    except:
        return HttpResponse("Something went wrong")



    
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

  

    


    dic['content'] = content
    return JsonResponse(dic)


@api_view(['GET'])
def getCurrentDownloads(request):
    global download_dic
    dic={}
    dic['content'] = list(download_dic.values())
    
    return JsonResponse(dic)



    

    

    