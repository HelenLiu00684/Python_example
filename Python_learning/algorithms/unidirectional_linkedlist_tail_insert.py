#1. undirectional_linkedlist create_tail_insert
class Node:
    data = ''
    next = None
    def __init__(self,data):
        self.data=data
        self.next=None

class Linkedlist:
    def __init__(self):
        self.head = None
        self.tail = None

    def append(self,data):
        new_node = Node(data) 
        if not self.head:
            self.head=new_node
            self.tail=new_node
        else:
            self.tail.next=new_node
            self.tail=new_node

    def display(self):
        node = self.head
        while node != None:
            print(f"The current node is {node.data}")
            node = node.next

if __name__ == "__main__":
    linkedlist = Linkedlist()

    print("Enter numbers to add to the linked list 'TAIL' (enter -1 to stop):")

    x=int(input("Enter the data:"))

    while(x != -1):
        linkedlist.append(x)
        x=int(input("Enter the data:"))

    linkedlist.display()
   