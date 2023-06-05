"""
This downloads a file from the web using multiple threads and merges the file segments into a single file. This is useful when there is a downloading speed limit per connection from sever side.
"""

import requests
import os
import threading

def download_segment(url, start_byte, end_byte, filename):
    headers = {'Range': f'bytes={start_byte}-{end_byte}'}
    response = requests.get(url, headers=headers, stream=True)

    with open(filename, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

def download_file(url, num_segments):
    response = requests.head(url)
    total_size = int(response.headers.get('content-length', 0))

    chunk_size = total_size // num_segments
    remaining_bytes = total_size % num_segments

    threads = []
    file_segments = []
    for i in range(num_segments):
        start_byte = i * chunk_size
        end_byte = start_byte + chunk_size - 1

        if i == num_segments - 1:
            end_byte += remaining_bytes

        segment_filename = f'segment{i}.dat'
        thread = threading.Thread(target=download_segment, args=(url, start_byte, end_byte, segment_filename))
        thread.start()
        threads.append(thread)
        file_segments.append(segment_filename)

    for thread in threads:
        thread.join()

    return file_segments

def merge_files(file_segments, output_filename):
    with open(output_filename, 'wb') as output_file:
        for segment in file_segments:
            with open(segment, 'rb') as segment_file:
                output_file.write(segment_file.read())

# Configuration
url = 'https://example.com/download.zip'  # URL of the file to download
num_segments = 10  # Number of file segments (you can adjust this according to your needs)

# Download the file segments
file_segments = download_file(url, num_segments)

# Merge the file segments
output_filename = url.split('/')[-1]
merge_files(file_segments, output_filename)

# Remove the file segments
for segment in file_segments:
    os.remove(segment)

print(f"File downloaded and merged successfully into '{output_filename}'.")
