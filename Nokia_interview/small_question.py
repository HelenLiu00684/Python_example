# import re
# text = "Ping 10.1.1.1 success, Ping 172.16.0.1 failed, Ping 192.168.0.5 success"
# ipv4_pattern = r'(?:25[0-5]|2[0-4]\d|1?\d{1,2})(?:\.(?:25[0-5]|2[0-4]\d|1?\d{1,2})){3}'
#  #    pattern = r'(?:25[0-5]|2[0-4]\d|1?\d{1,2})(?:\.(?:25[0-5]|2[0-4]\d|1?\d{1,2})){3}$'
#  #    pattern = r'^(?:25[0-5]|2[0-4]\d|1+\d{1,2})(?:\.(?:25[0-5]|2[0-4]\d|1+\d{1,2})){3}$'
# for line in text.strip().split(','):
#     print(re.search(ipv4_pattern,line))
#     if re.search(ipv4_pattern,line):
#         print(re.search(ipv4_pattern,line).group(0))

# import os,sys,pathlib,re
# bathpath=os.path.dirname(os.path.abspath(__file__))
# filename=os.path.join(bathpath,'10.0.0.1_ping.txt')
# textpattern=r'.*icmp_seq=.*'
# with open(filename,'r') as f:
#     for line in f.readlines():
#         # print(line.strip())
#         print(re.search(textpattern,line.strip()))

# data = {
#     '10.0.0.1': 'success',
#     '10.0.0.2': 'failed',
#     '10.0.0.3': 'success'
# }

# ip_list =[ip for ip,result in data.items() if result=='success']
# print(ip_list)
# ip_duplicate=[100,144,100]
# print(set(ip_duplicate))

# import os,sys,pathlib,re,subprocess
# if __name__=="__main__":
#     #result=subprocess.run(["ping","-c",str(10),"127.0.0.1"],stdout=subprocess.PIPE)
#     result=subprocess.run(["ping","-c",str(10),"127.0.0.1"],stdout=subprocess.PIPE,text=True)
#     f=open("log.txt",'w')
#     for i in result.stdout:
#         f.write(i)
#     f.close()    

# if __name__=="__main__":
#         key_list=[1,2,3,4,5]
#         value_list=[6,7,8,9,10]
#         dict_data=dict(zip(key_list,value_list))
#         print(dict_data)
#         reverse = {v:k for k,v in dict_data.items()}
#         print(reverse)



# test1 = {"R1": "OK", "R2": "OK", "R3": "OK"}
# test2 = {"R2": "FAIL", "R4": "OK"}

# merge = {**test1,**test2}
# print(merge)


# devices = {
#     "R1": "Router",
#     "R2": "Router",
#     "S1": "Switch",
#     "S2": "Switch",
#     "FW1": "Firewall"
# }

# device_count={}
# for type in devices.values():
#         device_count[type]=device_count.get(type,0)+1
# print(device_count)


import json
import os

# 自动找到当前目录下的 JSON 文件
basepath = os.path.dirname(os.path.abspath(__file__))
json_file = os.path.join(basepath, "devices_status.json")

# 1️⃣ 打开并加载 JSON 文件
with open(json_file, "r") as f:
    data = json.load(f)

# 2️⃣ 提取设备列表
devices = data["devices"]

# 3️⃣ 统计 up/down 数量
up_count = sum(1 for d in devices if d["status"] == "up")
down_list = [d["name"] for d in devices if d["status"] == "down"]

# 4️⃣ 输出结果
print(f"✅ 在线设备数量: {up_count}")
print(f"❌ 离线设备: {', '.join(down_list)}")

# 5️⃣ 显示完整数据结构
print("\n📘 全部数据结构:")
print(json.dumps(data, indent=4))