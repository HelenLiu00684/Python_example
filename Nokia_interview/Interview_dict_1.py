import os,sys,re
from pathlib import Path



def func_device(filename):
    line_success=0
    line_fail=0
    pingsuc=r'.*ttl=64 time=(0\.\d{3}) ms$'
    pingfail=r'^Request timed out.$'
    ping_result_list=[]

    with open(filename,'r') as f:
        for line in f:
            #print(line.strip())          
            ping_suc_result=re.search(pingsuc,line)
            ping_fai_result=re.search(pingfail,line)
            if ping_suc_result:
                ping_result_list.append(1)
                print(f'the ttl is {ping_suc_result.group(1)}')
                line_success = line_success+1
            elif ping_fai_result:
                line_fail = line_fail+1
                ping_result_list.append(0)   
        print(f"The result is {ping_result_list}")           
        print(f"The total success line is {line_success}")
    return ping_result_list    



    



if __name__=="__main__":
    filepattern=r'^(.*)_ping\.txt$'
    basepath=os.path.dirname(os.path.abspath(__file__))
    print(basepath)
    path=Path(basepath)
    filename_lists=[]
    for p in path.iterdir():
        re_result=re.match(filepattern,p.name)
        if not p.is_file():
            continue
        if re_result:
            print(re_result.group(0))
            filename_lists.append(re_result.group(1))
        
    print(filename_lists)

    device_result_dic = {}
    for file in filename_lists:
        
        filename=os.path.join(basepath,file+"_ping.txt")
        # print(filename)
        result_dev_list=func_device(filename)
        device_result_dic[file]=result_dev_list


    print(device_result_dic)
    for ip,result in device_result_dic.items():
        print(ip,"-",result)


    # filename_lists=[]
    # ping_result={}
    
