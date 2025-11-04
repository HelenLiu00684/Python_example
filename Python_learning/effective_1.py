
#1.str vs bytes
import os


def to_str(bytes_or_str):
    if isinstance(bytes_or_str, bytes):
        r = bytes_or_str.decode('utf-8')
    else:
        r=bytes_or_str
    return r

def to_bytes(bytes_or_str):
    if isinstance(bytes_or_str, str):
        r=bytes_or_str.encode('utf-8')
    else:
        r=bytes_or_str
    return r
print("1.str vs bytpe decoding and encoding")
a='h\x65llo'
print(a)
print(list(a))
print(type(a))
print("transfer to bytes '{}' and the type is {}".format(to_bytes(a), type(to_bytes(a))))  

a = b'h\x65llo'
print(a)          
print(list(a))    
print(type(a)) 
print("transfer to str '{}' and the type is {}".format(to_str(a), type(to_str(a))))
print("*"*100)

print("2.str vs bytpe assert test")
print("assert test strings {}".format("Hello" > "Love"))
print("assert test bytes {}".format(b'Hello' > b'Love'))
#print("assert test bytes {}".format("Hello" > b'Love'))
print("*"*100)

print("3.str vs bytpe open file")
with open("data.txt","a") as f:
    f.write("I love my life.---text\n")


import os

print("3. str vs bytes open file")

with open("data.txt", "w") as f:
    f.write("I love my life.---text\n")

with open("data.bin", "wb") as f:
    f.write(b"I love my life.---bin")

os.system("cat data.txt")
os.system("cat data.bin")

