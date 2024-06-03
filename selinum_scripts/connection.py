import os 

web = os.system("curl http://127.0.0.1:8000/")

while "html" not in web:
    web = os.system("curl http://127.0.0.1:8000/")
    os.system(web)
