1.Python TCL
1.1 python_tcl_0:This exercise is to implement a process where a Tcl script reads commands one by one, 
sends them to a file in the WSL environment, then returns the results to Python3 for file reading and processing, 
so that the information is both recorded in a file and displayed in the terminal.
                                                                ------ 28/10/2025
1.2 python_tcl_1:Added through file to push commands
                                                                
2.Python Threading：
This exercise is to implement the different multithreading method by ping commands. 
（os.system、subprocess.run、subprocess.Popen、ThreadPoolExecutor）                                                               
keypoints:
1.Synchronous(os.system、subprocess.run):The next command can be run until the previous one finished.
2.Asynchronous(subprocess.Popen):To start several ping commands simultaneously, and using poll() to observe.
3.Multithreaded Concurrent(thread_map/thread_submit):Using thread to execute the function. 
4.Using file open and write function 
5.using re to filter string
Note:Global Interpreter Lock (GIL) problem, Python can not execute multiple threads simultaneously,true parallel computation is not possible
