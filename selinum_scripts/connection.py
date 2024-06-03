import subprocess

try:
    output = subprocess.check_output(["curl", "http://127.0.0.1:8000/"])
    output_str = output.decode("utf-8")
except:
    output_str = ""

while "html" not in output_str:
    try:
        output = subprocess.check_output(["curl", "http://127.0.0.1:8000/"])
        output_str = output.decode("utf-8")
    except:
        pass