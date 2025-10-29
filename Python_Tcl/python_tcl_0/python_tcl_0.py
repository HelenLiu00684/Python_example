import subprocess
import os
import sys
import datetime
'''
#sudo apt install python3-psutil -y;python3 -c "import psutil; print(psutil.cpu_percent(interval=1))"
sudo apt install htop -y

sys.stdout = DualOutput(sys.__stdout__, logfile)
'''
class sys_stdout_file():
    def __init__(self, *files):
        self.files = files

    def write(self, obj):
#        sys.__stdout__.write("TCL Output in Python stdout.OBJ invoke in the sys_class:\n")
#        sys.__stdout__.write("DEBUG obj ="+ repr(obj)+ "\n")  # use repr() to get object representation
#        sys.__stdout__.flush()
        for f in self.files:
            f.write(obj) # the content of write
            f.flush()  # output to be visible immediately

    def flush(self):
        for f in self.files:
            f.flush()

base_path = os.path.dirname(os.path.abspath(__file__))
tcl_file = os.path.join(base_path, "tcl_test_0.tcl")
tcl_test_result_path = os.path.join(base_path, "tcl_test_0_result.txt")

# Ensure file is empty
with open(tcl_test_result_path, "w", encoding="utf-8") as f:
    f.write("")

result_pointer=open(tcl_test_result_path, "w", encoding="utf-8")


sys_stdout = sys_stdout_file(sys.__stdout__, result_pointer)
sys.stdout = sys_stdout  # redirect stdout to both terminal and file
try:
    
    print("The result is prepared below:\n")

    now = datetime.datetime.now()
    print("current time: {}\n".format(now.strftime("%Y-%m-%d %H:%M:%S")))


    print("Invoke the Tcl scripts:\n")
    # invoke tclsh to execute TCL script
    result = subprocess.run(["tclsh", tcl_file], capture_output=True, text=True,cwd=base_path)

    print("TCL Output in Python OBJ return from TCL:\n")
    print("[DEBUG obj]", repr(result))
    print(result.stdout)

    if result.stderr:
        print("TCL Error Output:\n")
        print(result.stderr)

finally:
    print("The output of TCL is finished.\n")
    sys.stdout = sys.__stdout__  # restore terminal
    result_pointer.close()


