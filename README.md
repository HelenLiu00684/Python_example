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
