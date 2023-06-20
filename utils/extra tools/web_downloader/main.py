import sys
import requests
import os
import shutil
import threading
import time
import datetime
from termcolor import colored

sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', '..')))
from utils.log.main import log

"""
This downloads a file from the web using multiple threads and merges the file segments into a single file. This is useful when there is a downloading speed limit per connection from sever side.
"""

TMP_DOWNLOAD_DIR = "data/Web_downloader/tmp"
WEB_DOWNLOAD_DIR = "data/Web_downloader"
DOWNLOADED_SIZE=0

def download_segment(url, start_byte, end_byte, file, TOTAL_SIZE, FILE_SIZE_SHOW,num_segments):
    start_time = time.time()
    headers = {'Range': f'bytes={start_byte}-{end_byte}'}
    response = requests.get(url, headers=headers, stream=True)

    DOWNLOADED_SIZE=0
    DOWNLOADED_SIZE_lock=threading.Lock()
    def access_downloaded_size(inc_val,fetch=False):
        global DOWNLOADED_SIZE
        DOWNLOADED_SIZE_lock.acquire()
        if fetch:
            val=DOWNLOADED_SIZE
            DOWNLOADED_SIZE_lock.release()
            return val
        DOWNLOADED_SIZE+=inc_val
        DOWNLOADED_SIZE_lock.release()

    def report_progress():
        downloaded = access_downloaded_size(None, True)
        progress = downloaded / TOTAL_SIZE
        progress_percent = int(progress * 100)
        total_bar_length = int(progress*25)

        bar = ('#' * (total_bar_length) + '-' * ((25 - total_bar_length)))

        bar_color = 'green' if progress_percent >= 50 else 'yellow'
        percent_color = 'cyan'

        # Calculate estimated time remaining
        elapsed_time = time.time() - start_time
        estimated_total_time = elapsed_time / progress if progress > 0 else 0
        estimated_remaining_time = estimated_total_time - elapsed_time

        # Format estimated remaining time
        minutes = int(estimated_remaining_time // 60)
        seconds = int(estimated_remaining_time % 60)
        progress_str = f"Downloading: [{colored(bar, bar_color):<25}] {colored(progress_percent, percent_color)}%"
        estimated_time_str = f" ET: {minutes} min {seconds} sec"

        print('\r' + progress_str + estimated_time_str, end='')
    
    with open(file, 'wb') as file:
        for chunk in response.iter_content(chunk_size=1024*1024*5):
            file.write(chunk)
            if FILE_SIZE_SHOW:
                access_downloaded_size(len(chunk))
                report_progress()
                

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
        thread = threading.Thread(target=download_segment, args=(url, start_byte, end_byte, segment_filepath,TOTAL_SIZE,FILE_SIZE_SHOW,num_segments))
        thread.start()
        threads.append(thread)
        file_segments.append(segment_filepath)

    for thread in threads:
        thread.join()

    bar = ('#' * (25) + '-' * ((25 - 25)))
    bar_color = 'green' if 100 >= 50 else 'yellow'
    percent_color = 'cyan'
    f"Downloading: [{colored(bar, bar_color):<25}] {colored(100, percent_color)}%"
    log("\nDownload complete")

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
            url_filename=url.split('/')[-1]
            ind_dot=url_filename.find('.')
            ext=url_filename[ind_dot:]
            output_filename=output_filename+ext
        log(f"Saving as {output_filename}")
    
    output_filedir = os.path.join(WEB_DOWNLOAD_DIR,output_filename)
    if os.path.exists(output_filedir):
        log(f"File '{output_filename}' already exists",2)
        return
    
    file_segments = download_file(url, num_segments,output_filename)

    # Merge the file segments
    merge_files(file_segments, output_filedir)

    # Remove the file segments
    for segment in file_segments:
        os.remove(segment)
    
    # Move to output directory
    destination = WEB_DOWNLOAD_DIR
    if not os.path.exists(destination):
        os.makedirs(destination)
    if output_dir:
        destination = output_dir
        if(os.path.exists(os.path.join(output_dir,output_filename))):
            log(f"File '{output_filename}' already exists in {output_dir}",1)

            new_output_filename =  datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+"_"+output_filename
            # rename file
            os.rename(output_filedir,os.path.join(os.getcwd(),"data","Web_downloader",new_output_filename))
            output_filedir = os.path.join(os.getcwd(),"data","Web_downloader",new_output_filename)
            log(f"Saving with filename {new_output_filename}",1)

        shutil.move(output_filedir,output_dir)

    log(f"File '{output_filename}' downloaded at {destination}")


if __name__ == '__main__':
    try:
        url = 'https://github.com/AI-Arsenals/TorrentLAN/archive/refs/heads/main.zip'
        main(url,output_filename='TorrentLAN')
    except Exception as e:
        log(e,2)

    try:
        url='https://gitlab.com/kalilinux/packages/wordlists/-/raw/kali/master/rockyou.txt.gz'
        main(url,output_dir=os.path.join(os.getcwd(),"data","Web_downloader"))
    except Exception as e:
        log(e,2)
