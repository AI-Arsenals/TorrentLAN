import os
path=input("Enter the path\n")

info={}

for attribute in ['md5' ,'sha256']:
    command1=f"echo {path} | {attribute}sum  "
    p=os.popen(command1).read()
    info[attribute]=p.split(' ')[0]
    

print(info)