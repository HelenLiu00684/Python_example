
from concurrent.futures import ThreadPoolExecutor,as_completed
import re,os,subprocess,time

def Ping_function_os(ip_add_list,count):
    """Ping a device multiple times and return success count"""
    start = time.time()
    success=0
    for ip_add in ip_add_list:
        response = os.system(f"ping -c {int(count)} {ip_add}> /dev/null 2>&1")  
        if response ==0:
            success=success+1
    end = time.time()
    print(f"Execution time: {end - start:.2f} seconds")          
    return success        

def Ping_function_sub_run(ip_add_list,count):
    start = time.time()
    """Ping a device multiple times and return success count"""
    base_path=os.path.dirname(os.path.abspath(__file__))
    result_file=os.path.join(base_path,"subprocess_logfile.txt")
    success=0
    with open(result_file,"w") as f:
        for ip_add in ip_add_list:
            response = subprocess.run(["ping","-c",str(count),ip_add],stdout=f,stderr=subprocess.STDOUT,text=True)  
            if response.returncode ==0:
                success=success+1
        end = time.time()
        print(f"Execution time: {end - start:.2f} seconds")            
    return success    

def Ping_function_sub_popen(ip_adds,count):
    """Ping a device multiple times and return success count"""
    start = time.time()
    filepath=os.path.dirname(os.path.abspath(__file__))
    processes=[]
    for ip_add in ip_adds:
        log_file=os.path.join(filepath,f"{ip_add}_subprocess_popen.txt")
        f = open(log_file, "w")
        p=subprocess.Popen(["ping","-c",str(count),ip_add],stdout=f,stderr=subprocess.STDOUT,text=True)
        processes.append((ip_add,p,f))
            
    while processes:
        for ip_add,p,f in processes[:]:
            ret=p.poll() 
            if ret is not None:
                f.close()   
                print(f" {ip_add} is done and save to {ip_add}_subprocess_popen.txt")
                processes.remove((ip_add, p, f))
    end = time.time()
    print(f"Execution time: {end - start:.2f} seconds")              

def ping_fuc_exec(host,count):
    base_path=os.path.dirname(__file__)
    result_thread_file=os.path.join(base_path,f"{host}_result_thread_map.txt")
    success = 0
 
    with open(result_thread_file,"w") as f:
        result = subprocess.run(["ping","-c",str(count),host],stdout=f,stderr=subprocess.STDOUT,text=True)
        if result.returncode ==0:
            success=success+1
    return host,success,result_thread_file

def Ping_function_thread_map(ip_add_list,count):
    """Ping a device multiple times and return success count"""
    start = time.time()
    success_total=0
    with ThreadPoolExecutor(max_workers=len(ip_add_list)) as exec:
        result_hosts = exec.map(ping_fuc_exec, ip_add_list, [str(count)] * len(ip_add_list))
        for host, success, logfile in result_hosts:
            print(f"{host} → {'Success' if success else ' Fail'}  Log: {logfile}")
            success_total += success
    print(f"\nTotal success count: {success_total}")
    end = time.time()
    print(f"Execution time: {end - start:.2f} seconds")  
    return success_total

def Ping_function_thread_submit(ip_add_list,count):
    """Ping a device multiple times and return success count"""
    start = time.time()
    success_total=0
    with ThreadPoolExecutor(max_workers=len(ip_add_list)) as exec:
        result_hosts = [exec.submit(ping_fuc_exec,host,str(count)) for host in ip_add_list] #executor.submit(func, arg)
        for result in as_completed(result_hosts):
            print(result)
            host, success, logfile = result.result()
            print(f"{host} → {'Success' if success else ' Fail'}  Log: {logfile}")
            success_total += success

    print(f"\n Total success count: {success_total}")
    end = time.time()
    print(f"Execution time: {end - start:.2f} seconds")  
    return success_total


def is_addlist_function(ip_add_list):
    pattern = r'^(?:25[0-5]|2[0-4]\d|1?\d{1,2})(?:\.(?:25[0-5]|2[0-4]\d|1?\d{1,2})){3}$'
    add_err_num = 0
    addlist_result = 0
    is_result = False
    for i in ip_add_list:
        pattern = r'^(?:25[0-5]|2[0-4]\d|1?\d{1,2})(?:\.(?:25[0-5]|2[0-4]\d|1?\d{1,2})){3}$'
        addlist_result=bool(re.match(pattern,i))
        if not addlist_result:
            add_err_num = add_err_num+1
    if add_err_num ==0:
        is_result = True
    return is_result  


if __name__=="__main__":
    print('*'*60)
    print('Choose the different process method by Python Language')
    print('1.Synchronous:os.system')
    print('2.Synchronous:subprocess.run')
    print('3.Asynchronous:subprocess.Popen')
    print('4.Multithreaded Concurrent:thread_map')
    print('5.Multithreaded Concurrent:thread_submit')
    print('*'*60)
    choice=input("you choice:")

    try:
        ip_add_list = str(input("Please input the address list and seperete by ',': ")) 
        ip_add_list =[ip.strip() for ip in ip_add_list.split(',') if ip.strip()]
        if not is_addlist_function(ip_add_list):
            raise ValueError ("The address list is not correct.")
        count = input("Please input the count:")
        if not count.isdigit():
            raise ValueError ("The count is not integer.")
        if(choice=="1"):
            print(f"The success of ping_os is : {Ping_function_os(ip_add_list,count)} ")   
        elif(choice=="2"):
            print(f"The success of ping_sub_run is: {Ping_function_sub_run(ip_add_list,count)} ")
        elif(choice=="3"):
            print(f"The success of ping_sub_popen is: {Ping_function_sub_popen(ip_add_list,count)} ")  
        elif(choice=="4"):
            print(f"The success of ping_thread is: {Ping_function_thread_map(ip_add_list,count)} ")
        elif(choice=="5"):
            print(f"The success of ping_thread is: {Ping_function_thread_submit(ip_add_list,count)} ")
    except ValueError as e:
        print(e)        


