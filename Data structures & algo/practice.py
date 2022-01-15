#    linklist creation   node=|head|data|next >
class Node :
    def __init__(self,data=None,next=None):
        self.data = data    #  data is the type of data inserted 
        self.next = next    #  pointer to the next element 

class linklist:
    def __init__(self):
        self.head = None     # head - which points to the head of the list  

    def insert_beginning(self,data):
        node= Node(data,self.head) # we create the node element 
        self.head = node           # once our node is created which include (head , data ) , we specify self.node = node 
    
    def print(self):
        if self.head is None:
            print('its empty')
            return
        
        itr = self.head
        linklist_str=''
        while itr:
            linklist_str += str(itr.data) + ' ---> '
            itr = itr.next
        print(linklist_str)
    
    def insert_end(self,data):              # inserting values at end
        if self.head is None:
            self.head = Node(data,None)
            return
        itr = self.head
        while itr.next:
            itr = itr.next
        itr.next = Node(data,None)
    
    def insert_values(self,listt):           # inserting list 
        self.head = None
        for data in listt:
            self.insert_end(data)
    
    @property                                # because i dont want to print this function as function but an attribute of the class linklist 
    def lenght(self):                        # returning count of linkedlist
        count= 0
        itr= self.head
        while itr:
            count +=1
            itr = itr.next
        return count
    
    def remove(self,index):
        if index<0 or index >= self.lenght:      # remember now lenght is not a funciton but an attribute so use it likely 
            raise Exception ('Exceeded value  !')
        if index ==0:
            self.head = self.head.next 
            return
        
        count = 0             
        itr = self.head
        while itr:                # until it finishes
            if count == index -1:
                itr.next = itr.next.next
                break 
            itr = itr.next 
    
    def insert_at(self,index,data):
        if index<0 or index >= self.lenght:      # remember now lenght is not a funciton but an attribute so use it likely 
            raise Exception ('Exceeded value  !')
        if index ==0:
            self.insert_beginning (data)
            return

        count=0
        itr=self.head
        while itr:
            if count == index - 1: # inorder to insert at 2 index , we stop at index 1 > inorder to modify the index 1 element reference to the element at index 2

                node = Node(data , itr.next)  # we are  at index 1   here we point to itr.next
                itr.next = node               # itr.next == index 2 element   
                break


            itr = itr.next                # loop that is going to each element in the linkedlist 
            count +=1
        
''' when we insert in linkedlist - we point to the next elemnent reference  in the linkedlist '''

if __name__=="__main__":
    ll = linklist()
    # ll.insert_values(['tushar','malhan','watches','proffesional sports'])
    # ll.insert_beginning(5)
    # ll.insert_beginning(7)   
    # ll.insert_end(77)   
    # ll.insert_end(2)   
    # print('lenght = ' , ll.lenght)
    # ll.remove(-20)
    # ll.insert_at(2,'is')
    # ll.insert_at(3,' the king  and ')
    ll.print()
