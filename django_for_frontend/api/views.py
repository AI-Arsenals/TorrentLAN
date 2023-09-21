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

download_dick_lock=threading.Lock()
download_dic = {}
re_render = False


class Helper:

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
                l[i][5] = Helper.jsonify(l[i][5])
                size = float(l[i][5]['Size'])
                l[i][5]['Size'] = Helper.bytesConversion(size)
    
        return content


    def clamp(n, min, max):
        if n < min:
            return min
        elif n > max:
            return max
        else:
            return n



class FetchFiles:
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
        content=Helper.preprocess(content)
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
        content = Helper.preprocess(content)
        
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
            content[0][5] = Helper.jsonify(content[0][5])
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
                item[5]=Helper.jsonify(item[5])
                if(item[2]==1):
                    dic['files'].append(item)
                else:
                    dic['folders'].append(item)

        return HttpResponse(json.dumps(dic))

class Upload:
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






class Download:

    

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

        new_content = [AVAILABLE, (Helper.bytesConversion(TOTAL_SPEED) + '/s')]

        dic = {
            'is_available': bool(new_content[0]),
            'speed': new_content[1]
        }

        return HttpResponse(json.dumps(dic))


    @api_view(['POST'])
    def download(request):
        data = json.loads(request.body.decode())
        global download_dic
        global download_dick_lock
        data['percentage']=0
        download_dick_lock.acquire()
        download_dic[data['lazy_file_hash']] = data
        download_dick_lock.release()
        
        unique_id=None
        for id in data['unique_id']:
            content = main.uniqueid_is_up(id)
            if(content[0]):
                unique_id=id
                break

        if(unique_id==None):
            return JsonResponse({'status':False})


        content = main.download(data['unique_id'][0],data['lazy_file_hash'],data['table_name'],data['name'],data['file_location'],'http://127.0.0.1:8000/api/progress')
        print(content[0],type(content[0]))
        dic = {
            'status': content[0]
        }
        



        return HttpResponse(json.dumps(dic))


    @api_view(['GET'])
    def receive_progress(request):
        data=request.GET
        global download_dic
        global download_dick_lock
        global re_render
    
        lazy_file_hash = list(data.keys())[0]
        progress=0

        download_dick_lock.acquire()
        
        if(lazy_file_hash in download_dic):
            progress = float(data[lazy_file_hash])
            prev = download_dic[lazy_file_hash]['percentage']
            progress = Helper.clamp(progress,prev,100)

            if(progress==100):
                download_dic.pop(lazy_file_hash)
                re_render=True
                
            else:
                download_dic[lazy_file_hash]['percentage'] = progress

        

        
            # if download_dick_lock is acquired then release

        download_dick_lock.release()
        return JsonResponse({
            'lazy_file_hash': lazy_file_hash,
            'updated_progress': download_dic[lazy_file_hash]
        })

class Dashboard:
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
        global download_dick_lock
        global re_render
        dic={}
        download_dick_lock.acquire()
        dic['content'] = list(download_dic.values())
        dic['render'] = re_render
        re_render=False
        download_dick_lock.release()
        
        return JsonResponse(dic)

class UserInfo:
    @api_view(['GET'])
    def setUsername(request):
        data=request.GET.get('username')
        # print(data)
        status = main.set_username(data)
        dic={
            'status': status
        }
        return JsonResponse(dic)
    

class Cache_remover:

    
    
    @api_view(['GET'])
    def main(request):
        data=request.GET
        content=None
        if(data['action']=='size'):
            tmp_size = (main.remover.tmp_folder_size_fetcher())
            log_size = (main.remover.log_size_fetcher())
            content = [log_size,tmp_size]
        else:
            if(data['site']=='temp'):
                main.remover.tmp_folder_remover()
            elif(data['site']=='log'):
                main.remover.log_remover()
            content='/'

        print(content)
        return JsonResponse({'content':content})

@api_view(['POST'])
def open_file_loc(request):
    data=json.loads(request.body.decode())
    print(data)
    loc=data['location']
    main.file_location_opener(loc)
    return HttpResponse('done')

