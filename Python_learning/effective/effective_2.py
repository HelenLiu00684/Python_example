favours = ['apples', 'bananas', 'tofu', 'cats']
print(favours[::3])
print(favours[:4])
print(favours[-3:])#reverse index -3 to 0

myfavours = favours[:]
myfavours_cont = favours[:-1]

print("The assertiont is : {}".format(myfavours == favours))
result=(True if myfavours_cont == favours else False)
print("The assertiont is : {}".format(result))
print("The reserver and step -1 is : {}".format(favours[::-1]))
print("The reserver is : {}".format(favours[::-2]))

number_list = list(range(20))
print("The number list is : {}".format(number_list))   
number_odd_list = number_list[1:10:2]
number_even_list = number_list[:10:2]         
print("The number_odd list slice [1:10:2] is : {}".format(number_odd_list))
print("The number_even list slice [:10:2] is : {}".format(number_even_list))
first,second,*other=number_list
print("The first number is : {}".format(first))
print("The second number is : {}".format(second))
print("The other number is : {}".format(other))

student_dict={}
with open("/home/qjliu/Python_code/Python_learning/data.csv", "r") as f:
    header,*content =f.readlines();
    print("Reading data from CSV file:")
    print("The header is :{}".format(header.strip()))
    for line in content:
        name, age, city = line.strip().split(',')
        print(f"Name: {name}, Age: {age}, City: {city}")
        student_dict[name] = [{'age': int(age)}, {'city': city}]
        

student_dict_sorted = dict(sorted(student_dict.items(), key=lambda x: x[1][0]["age"]))#note:x[0]---key x[1]---value
print("The student dictionary is : {}".format(student_dict))
print("The student_sort dictionary is : {}".format(student_dict_sorted))



