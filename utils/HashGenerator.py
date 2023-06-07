import os
path=input("Enter the path\n")

info={}

for attribute in ['md5' ,'sha256']:
    command1=f"certutil -hashfile {path} {attribute}"
    p=os.popen(command1).read()
    info[attribute]=p.split('\n')[1]

print(info)