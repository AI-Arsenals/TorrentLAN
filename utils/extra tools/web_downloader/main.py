import sys
import requests
import os
import shutil
import threading
import time

sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', '..')))
from utils.log.main import log

"""
This downloads a file from the web using multiple threads and merges the file segments into a single file. This is useful when there is a downloading speed limit per connection from sever side.
"""

TMP_DOWNLOAD_DIR = "data/Web_downloader/tmp"
PROGRESS_METER=0
PROGRESS_BAR_MIN=0

def download_segment(url, start_byte, end_byte, file, TOTAL_SIZE, DOWNLOADED_SIZE, FILE_SIZE_SHOW,num_segments):
    global PROGRESS_METER
    global PROGRESS_BAR_MIN
    headers = {'Range': f'bytes={start_byte}-{end_byte}'}
    response = requests.get(url, headers=headers, stream=True)
    
    with open(file, 'wb') as file:
        for chunk in response.iter_content(chunk_size=64*1024):
            file.write(chunk)
            if FILE_SIZE_SHOW:
                DOWNLOADED_SIZE += len(chunk)
                progress = DOWNLOADED_SIZE / TOTAL_SIZE
                progress_bar = '#' * PROGRESS_BAR_MIN * num_segments
            
            # Remove the progress bar periodically
            if PROGRESS_METER % 10 ==0:
                if(int(progress * 100) > PROGRESS_BAR_MIN):
                    PROGRESS_BAR_MIN=int(progress * 100)
                    if(PROGRESS_BAR_MIN>99):
                        PROGRESS_BAR_MIN=99
                sys.stdout.write("\rDownloading: [{:<100}] {}%".format(progress_bar, PROGRESS_BAR_MIN*num_segments))
                sys.stdout.flush()
            PROGRESS_METER+=1
                
    if FILE_SIZE_SHOW:
        sys.stdout.write('\n')
        sys.stdout.flush()

def download_file(url, num_segments,filename):
    response = requests.head(url)
    TOTAL_SIZE = int(response.headers.get('content-length', 0))
    FILE_SIZE_SHOW=True
    if(not TOTAL_SIZE):
        log(f"Server not showing content-length for {url}",1)
        num_segments=1
        log(f"Changing threads to {num_segments}",1)
        FILE_SIZE_SHOW=False
    else:
        log(f"Downloading {TOTAL_SIZE} bytes ...")

    DOWNLOADED_SIZE = 0

    if not os.path.exists (TMP_DOWNLOAD_DIR):
        os.makedirs(TMP_DOWNLOAD_DIR)

    chunk_size = TOTAL_SIZE // num_segments
    remaining_bytes = TOTAL_SIZE % num_segments

    threads = []
    file_segments = []
    for i in range(num_segments):
        start_byte = i * chunk_size
        end_byte = start_byte + chunk_size - 1

        if i == num_segments - 1:
            end_byte += remaining_bytes

        segment_filepath = f'{filename}_segment{i}.dat'
        segment_filepath = os.path.join(TMP_DOWNLOAD_DIR, segment_filepath)
        thread = threading.Thread(target=download_segment, args=(url, start_byte, end_byte, segment_filepath,TOTAL_SIZE,DOWNLOADED_SIZE,FILE_SIZE_SHOW,num_segments))
        thread.start()
        threads.append(thread)
        file_segments.append(segment_filepath)

    for thread in threads:
        thread.join()

    sys.stdout.write("\rDownloading: [{:<100}] {}%".format('#' * 100, 100))
    sys.stdout.flush()

    return file_segments

def merge_files(file_segments, output_filepath):
    with open(output_filepath, 'wb') as output_file:
        for segment in file_segments:
            with open(segment, 'rb') as segment_file:
                output_file.write(segment_file.read())


def main(url,output_filename=None,output_dir=None):
    num_segments = 5  # Number of segments to split the file into
    log(f"Downloading with {num_segments} threads ...")
    if not output_filename:
        output_filename = url.split('/')[-1]
        log(f"Output filename not specified, using {output_filename} as filename")
    else:
        if '.' not in output_filename:
            if '.' in url:
                output_filename+="."+url.split('.')[-1]
        log(f"Saving as {output_filename}")
    
    output_filedir = os.path.join(os.getcwd(),"data","Web_downloader",output_filename)
    if os.path.exists(output_filedir):
        log(f"File '{output_filename}' already exists",2)
        return
    
    file_segments = download_file(url, num_segments,output_filename)

    # Merge the file segments
    merge_files(file_segments, output_filename)

    # Remove the file segments
    for segment in file_segments:
        os.remove(segment)

    # correct file extension
    file_ext="."+url.split('.')[-1]
    
    # Move to output directory
    destination = os.path.join(os.getcwd(),"data","web_downloader")
    if not os.path.exists(destination):
        os.makedirs(destination)
    if output_dir:
        destination = output_dir
        if(os.path.exists(os.path.join(output_dir,output_filename))):
            log(f"File '{output_filename}' already exists in {output_dir}",1)

            new_output_filename =  str(time.time())+output_filename
            # rename file
            os.rename(output_filedir,os.path.join(os.getcwd(),"data","Web_downloader",new_output_filename))
            output_filedir = os.path.join(os.getcwd(),"data","Web_downloader",new_output_filename)
            log(f"Renamed file to {new_output_filename}",1)

        shutil.move(output_filedir,output_dir)

    log(f"File '{output_filename}' downloaded at {destination}")


if __name__ == '__main__':
    try:
        url = 'https://github.com/AI-Arsenals/TorrentLAN/archive/refs/heads/main.zip'
        main(url,output_filename='TorrentLAN',output_dir=os.path.join(os.getcwd(),"data"))
    except Exception as e:
        log(e,2)

    try:
        url='https://gitlab.com/kalilinux/packages/wordlists/-/raw/kali/master/rockyou.txt.gz'
        main(url,output_dir=os.path.join(os.getcwd(),"data","Web_downloader"))
    except Exception as e:
        log(e,2)
