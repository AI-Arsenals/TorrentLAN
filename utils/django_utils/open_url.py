import os

def open_url(url):
    os.system('start '+url)

if __name__ == '__main__':
    open_url('http://localhost:3000')