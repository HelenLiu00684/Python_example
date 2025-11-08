import sys
from typing import List
#1. Linear Table Algorithms
#1.1 Print Linear table
#def linear_print(linear):
'''
def linear_print(linear:List[int]) -> None:

    for value in enumerate(linear,1):
        print("The idx is {} and the value is {}".format(value))


if __name__ == "__main__":   
    linear = [3,6,8,4,1,9]     
    linear_print(linear)
'''
#1.2 Print maximum value in Linear table
'''
每一轮都从头开始比较，只到「未排序的最后一个位置」为止。
每一轮结束后，最大值“冒泡”到最后，不再参与比较。
外层循环控制的是“冒泡的轮数”,因此最多只需要冒泡 n−1 轮，最后一个自然是最小的。
内层循环是比较相邻元素：
-1 防止 j+1 越界；
-i 表示“已经冒到最后的部分不再参与比较”。
'''
'''
def linear_max_print(linear:List[int])->List[int]:

    temp = 0
    for i in range(len(linear)):
        for j in range(len(linear)-1-i):
            if linear[j]>linear[j+1]:
                temp = linear[j]
                linear[j]=linear[j+1]
                linear[j+1]=temp
    return linear  
        

if __name__ == "__main__":   
    linear = [3,6,8,4,1,9]     
    print(linear_max_print(linear))
'''
#1.3 Print maximum value in Linear table
'''
def linear_mix_value(linear:List[int])->List[int]:
    temp = 0
    for i in range(0,len(linear)-1):
        for j in range(0,len(linear)-1-i):
            if linear[j]<linear[j+1]:
                temp = linear[j]
                linear[j]=linear[j+1]
                linear[j+1]=temp
    return linear 

if __name__ == "__main__":
    linear = [3,6,8,4,1,9]
    print(linear_mix_value(linear))
'''
#1.4 Linear Table Append   
#Add a score 75 to the end of the one-dimensional array scores.
'''
def linear_append_value(linear:List[int], value:int)->List[int]:
    append_list = [0]*(len(linear)+1)
    for i in range(0,len(linear)):# the number of loop is len(linear)
        if linear[i]!=value:
            append_list[i] = linear[i]
        else:    
            break
    append_list[len(linear)]=value
    return append_list

if __name__ == "__main__":
    linear = [90,70,50,80,60,85]
    x = int(input("Enter an integer: "))
    print(linear_append_value(linear,x))
'''    
#1.5 Linear Table Insert
#Insert a student's score anywhere in the one-dimensional arrayscores.
'''
def linear_insert_value(linear:List[int], value:int, index:int)->List[int]:

    insert_list = [0]*(len(linear)+1)
    for i in range(len(linear)):
        if i<index:
            insert_list[i] =linear[i]
        elif i==index:
            temp = linear[i]
            insert_list[index] = value
            insert_list[index+1] = temp
        else:
            insert_list[i+1]=linear[i]
    return insert_list

if __name__ == "__main__":
    linear = [90,70,50,80,60,85]
    try:
        index = int(input("Enter a index: "))
        x = int(input("Enter an integer: "))
        if index < 0 or index >= len(linear):
            raise IndexError(f"index {x} is illegal the range should be :0~{len(linear)-1}")
        print(linear_insert_value(linear,x,index))
    except ValueError:
        print("Invalid input. Please enter integers only.")
    except IndexError as e:
        print(e)
'''
#1.6 Linear Table Delete
#delete a student's score anywhere in the one-dimensional arrayscores.
'''  
def linear_delete_index(linear:List[int], index:int)->List[int]:
    if index < len(linear):
        delete_list = [(len(linear)-1)*[0]]
        for i in range(len(linear)):
            if i<index:
                delete_list[i]=linear[i]
            elif i>=index and i < len(linear)-1:
                delete_list[i]=linear[i+1]
    else:
        print("The index is out of the range.\n")
    return delete_list

def linear_delete_value(linear:List[int], value:int)->List[int]:
    if value in linear:
        j = 0
        delete_list = []
        for i in range (len(linear)):
            if linear[i]!=value:
                delete_list.append(linear[i])
            else:
                continue
    else:
        print("The value is out of the range\n")
    return delete_list

if __name__ == "__main__":
    linear = [90,70,50,80,60,85]
    print("Please input the opinion to delete the value from the linear listb <0.index 1.value>:")
    try:
        x=int(input("Enter the opinion:"))
        print(x)
        if x!=0 and x!=1:
            raise ValueError(f"Only can accept 0 or 1")
        elif x==0:
            index = int(input("Enter the index to delete:"))
            print(f"After delete the index {index} the remain list is :{linear_delete_index(linear,index)}")
        elif x==1:
            value = int(input("Enter the value to delete:"))
            print(f"After delete the index {value} the remain list is :{linear_delete_value(linear,value)}")
    except ValueError as e:
        print(e)
''' 
#1.7 reverse order array
#delete a student's score anywhere in the one-dimensional arrayscores.
def linear_revert(linear:List[int])->List[int]:
    linear_revert = []
    if len(linear)%2==1:
        length = (int)(len(linear)/2)+1
    else:
        length = (int)(len(linear)/2)
    print(length)
    for i in range(length):
        temp = linear[i]
        linear[i]=linear[len(linear)-i-1]
        linear[len(linear)-1-i]=temp
    return linear
if __name__ == "__main__":
    linear = [90,85,80,75,70,65]
    print(f"The before linear list is {linear}\n")
    print(f"The after linear list is {linear_revert(linear)}\n")
    

