import subprocess
import os

if __name__ == "__main__":
    
    print
    print(u"\u001b[32m PASS: \u001b[0m Loading Rhino...")
    result = subprocess.call(r'"C:\Program Files\Rhino 7\System\Rhino.exe" /nosplash /runscript="_-Grasshopper Banner Disable Window Load Window Show _Enter"')
    
    print(result)

    print
    #print(u"\u001b[32m PASS: \u001b[0m Everything is ok.")
    #print(u"\u001b[31m FAIL: \u001b[0m Something went wrong.")
    print