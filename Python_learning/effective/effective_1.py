

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

import os

print("3. str vs bytes open file")

with open("data.txt", "a") as f:
    f.write("I love my cat.---text\n")

with open("data.bin", "ab") as f:
    f.write(b"I love my cat.---bin\n")

os.system("cat data.txt")
os.system("cat data.bin")

with open("data.bin", "rb") as f:
    print("The content of bin file is : \n{}".format(f.read()))

print("*"*100)

print("4.format using on str")

id = "041150452"
value = "Alice"
age = 30
height = 5.5467
print("my name is {1} and my is id is {0}\n.".format(id, value))
formatted=format(age,"^20d")
print("* My age is ",formatted,"and my height is {:.2f}*".format(height))

f_string=f"{value.strip('\'')!r:<10} height is {height:.2f}"
print(f_string)
print("*"*100)

print("5.complicated expression")
from urllib.parse import parse_qs
query_string = 'name=Alice Liu&age=30&height=5.5467'
my_dict = parse_qs(query_string)
print(repr(my_dict))

print("name",my_dict['name'])
print("name",my_dict.get('name')[0])
print("name",my_dict['name'][0])

print("age",my_dict['age'][0])
print("height",my_dict['height'][0])
print("gender",my_dict.get('gender', ['Male'])[0])

height_num = my_dict.get('height')[0]
if height_num:
    print("height value:{:.2f}".format(float(height_num)))

course_table ={'MATH':('CALCULUS',4)}
course_table['CS'] = ('INTRO TO CS', 3)
course_table['ENG'] = ('ENGLISH LITERATURE', 2)

for course, (name, credits) in course_table.items():
    print(f"{course}: {name} ({credits} credits)")

for course, (name, credits) in enumerate(course_table.items(), 1):
    print(f"{course}: {name} ({credits} credits)")

favours = ['apples', 'bananas', 'tofu', 'cats']
i = 0
for favour in favours:
    i += 1
    print('the id {} favour is {}'.format(i,favour))    

favours = ['apples', 'bananas', 'tofu', 'cats']
for i, favour in enumerate(favours, 1):
    print(f'{i} {favour}')

favours = ['apples', 'bananas', 'tofu', 'cats']
for favour in enumerate(favours, 1):
    print(favour)    