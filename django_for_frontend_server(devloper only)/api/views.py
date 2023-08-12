import main
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from rest_framework.decorators import api_view
import sys
import os
import threading
import json
import queue

sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..')))

download_dick_lock = threading.Lock()
download_dic = {}
re_render = False


class Helper:

    def jsonify(s):
        return json.loads(s.replace("'", '"'))

    def bytesConversion(size):
        units = ['B', 'KB', 'MB', 'GB', 'TB']

        unit = 0
        while (1024 <= size):
            size /= 1024
            unit += 1

        size = round(size, 2)

        out = str(size) + units[unit]
        return out

    def preprocess(content):

        processed_content = {}
        content = list(content)
        print(content)
        for index, item in enumerate(content[0]):

            hash = item[8]

            if (hash in processed_content):
                processed_content[hash][7].append(item[7])
            else:
                temp = []
                temp.append(item[7])
                item[7] = temp
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

        dic = {
            "Status": 200,
            'files': [],
            'folders': []
        }
        depth = request.GET.get('depth', None)
        folder = request.GET.get('folder', None)
        if (folder == 'none'):
            folder = None

        temp = request.GET.get("depth", None)

        content = main.rows_at_depth(depth=int(depth), folder_name=folder)
        if (content[0] == False or content[1] == False):
            dic["Status"] = 404
            return HttpResponse(json.dumps(dic))
        content = Helper.preprocess(content)
        dic['files'] = content[0]
        dic['folders'] = content[1]
        return HttpResponse(json.dumps(dic))

    @api_view(['GET'])
    def getFolderList(request):

        dic = {
            'Status': 200,
            'files': [],
            'folders': []
        }
        unique_id = request.GET.get('unique_id', None)
        lazy_file_hash = request.GET.get('lazy_file_hash', None)
        content = main.childs(unique_id=unique_id,
                              lazy_file_hash=lazy_file_hash)
        if (content[0] == False or content[1] == False):
            dic["Status"] = 404
            return HttpResponse(json.dumps(dic))
        content = Helper.preprocess(content)

        dic['files'] = content[0]
        dic['folders'] = content[1]
        return HttpResponse(json.dumps(dic))

    @api_view(['GET'])
    def getParent(request):
        query_dict = request.GET
        dic = {'Status': 200}
        # print(type(query_dict))
        content = main.db_search(
            list(query_dict.keys()), list(query_dict.values()))

        if (content == False):
            dic['Status'] = 500
        else:
            content[0][5] = Helper.jsonify(content[0][5])
        dic['content'] = content
        return HttpResponse(json.dumps(dic))

    def searchQuery(request):
        query_dict = request.GET
        dic = {'Status': 200, 'files': [], 'folders': []}

        content = main.db_search(
            list(query_dict.keys()), list(query_dict.values()))
        print(content)
        if (content == False):
            dic['Status'] = 500

        else:
            for item in content:
                if (item[0] < 0 or item[3] == 1):
                    continue
                item[5] = Helper.jsonify(item[5])
                if (item[2] == 1):
                    dic['files'].append(item)
                else:
                    dic['folders'].append(item)

        return HttpResponse(json.dumps(dic))


class Upload:
    @api_view(['POST'])
    def upload(request):

        return


class Download:
    @api_view(['GET'])
    def unique_id_is_up(request):
        return

    @api_view(['POST'])
    def download(request):
        return

    @api_view(['GET'])
    def receive_progress(request):
        return


class Dashboard:
    @api_view(['GET'])
    def getDashboardEntries(request):
        return

    @api_view(['GET'])
    def getCurrentDownloads(request):
        return


class UserInfo:
    @api_view(['GET'])
    def setUsername(request):
        return


class Cache_remover:
    @api_view(['GET'])
    def main(request):
        return
