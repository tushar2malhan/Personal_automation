''' 
    ALL the sorting alogrithms with your detailed explanation 

    Author:     Tushar Malhan
    Date:       9/11/2022

'''
#               selection sort 

arr = [64, 25, 12, 22, 11]

def selection_(arr):
    for i in range(len(arr)-1):
        import pdb;pdb.set_trace()
        while i >= 0 and arr[i+1] < arr[i]:
            arr[i+1], arr[i] = arr[i], arr[i+1]
            i -=1
    print(arr)
# selection_(arr)

#        For EACH element in the list,
# ie each iteration > we check if the next element  arr[i+1]
#   is smaller than the current element
# if yes then take a second "while" loop and 
# take a index "i" where i is the current element which
#   keeps on getting swapped with the next element if smaller
# as a measure to keep on reducing the "i" until it is 0
 
''' Second explanation 
Here i is the iteration of the list where we loop over
each element in the list and check if the next element is smaller
to sort it in ascending order

    Date:      9/21/2022
'''

def selection_2(arr):
    # import pdb;pdb.set_trace()
    ''' arr = [64, 25, 12, 22, 11]
    '''
    for i in range(len(arr)-1):
        index = i 
        for next_element in range(i+1, len(arr)):
            if arr[next_element] < arr[index]:
                index = next_element
        arr[i], arr[index] = arr[index], arr[i]
    print(arr)
# selection_2(arr)
'''
    Date:      9/25/2022
    Selection Sort 2

Here we initially take the first element of array as i 
and run the second loop where we check if the next element
is smaller than the current element and if yes then we 
swap the elements, THis we do this for each element in the list

'''

def selection_sort_3(arr):

    for i in range(len(arr)-1):
        while i>=0 and arr[i-1] > arr[i]:
            arr[i-1], arr[i] = arr[i], arr[i-1]
            i -= 1
    print(arr)
# selection_sort_3(arr)


#                       Bubble Sort

def bubble(arr):
    # import pdb;pdb.set_trace()
    ''' arr = [64, 25, 12, 22, 11]
    '''
    ...
    for i in range(len(arr)):
        for j in range(len(arr)-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    print(arr)
# bubble(arr)


def bubble2(arr):
    for i in range(len(arr)):
        while i>=0 and arr[i-1] > arr[i]:
            arr[i-1], arr[i] = arr[i], arr[i-1]
            i -= 1
    print(arr)
# bubble2(arr)


#                       Insertion Sort



def insertion(numbers):

    print("Before Sorting:", numbers)  #size/length is = 5
    for i in range(len(numbers)-1): #0,1,2,3 (Iteration 4)
        #finding the minimum value from partition to rest of data
        #partition/index is moving to right
        for j in range(i+1, len(numbers)):
            #comparing the selected index value with its next index value
            if numbers[j] < numbers[i]:
                #swapping partition's left value with the right value
                numbers[i], numbers[j] =  numbers[j], numbers[i]
    print('After Sorting: ', numbers)

# insertion(arr)


''' 10/7/2022 '''
#                       Merge Sort 

# def merge(arr):
#     ...



''' 11/21/2022 '''

# # A = [10,19,15]
# A = [6,1,4,6,12,2,2,4]
# K = 3
# L = 2

# def solution(A, K, L):
#     if K + L > len(A):
#         return -1

#     if (K+L) %2 == 0 and len(A) %2 !=0:
#         return -1
#     if K > len(A) or L > len(A):
#         return -1

#     max_target_alice = 0
#     alice_start = 0
#     max_target_bob = 0
#     for each_apple in range(len(A)):
#         if sum(A[each_apple:K+each_apple ]) > max_target_alice:
#             max_target_alice = sum(A[each_apple:K+each_apple])
#             alice_start = each_apple

#     A = A[:alice_start-1] + A [K+alice_start:]

#     for each_apple in range(len(A)):
#         if sum(A[each_apple:L+each_apple ]) > max_target_bob:
#             max_target_bob = sum(A[each_apple:L+each_apple])
           
#     return  (max_target_alice+ max_target_bob)

    

# print(solution(A,K,L))


# class Order:
#     def __init__(self, is_buy, qty, price):
#         self.is_buy = is_buy
#         self.qty = qty
#         self.price = price

#     def __repr__(self):
#         return '{} {}@${:.1f}'.format(
#             'buy' if self.is_buy else 'sell',
#             self.qty,
#             self.price)
    
#     def __gt__(self, other):
#         return self.price > other.price

# class OrderBook:
#     def __init__(self):
#         self._orders = []

#     def __enter__(self):
#         return self

#     def __exit__(self, *args):
#         '''
#         formats and prints the order book as the test cases expect
#         '''
#         buys, sells = self._split_into_buy_and_sell_orders()
#         buys = sorted(buys)
#         sells = sorted(sells)
#         for o in [*buys, *sells]:
#             print(o)

#     def _split_into_buy_and_sell_orders(self):
#         '''
#         splits orders into buy and sell orders.
#         returns a pair of iterables:
#         first iterable points to the first buy order.
#         second points to the first sell order.
#         '''
#         from itertools import tee, filterfalse
#         is_buy = lambda o: o.is_buy
#         buys, sells = tee(self._orders)
#         return filter(is_buy, buys), filterfalse(is_buy, sells)
#     def add(self, order):
#         '''
#         checks the opposing side's available orders.
#         for a buy order, look at existing sell orders, and vice versa.
#         if a trade is possible, update the order book accordingly.
#         otherwise, insert the order into the book.
#         '''
#         other = self._find_trade(order)
#         if other:
#             self._orders.remove(other)
#         else:
#             self._orders.append(order)        

#     def _find_trade(self, order):
#         '''
#         returns an order for the best "match" for a give order.
#         for buy orders, this would be the lowest sell price.
#         for sell orders,the highest buy price.
#         if no orders meet the criteria, return None.
#         '''
#         ret = None
#         i = 0
#         while i < len(self._orders):
#             if order.is_buy != self._orders[i]:
#                 if order.price > self._orders[i].qty:
#                     ret = self._orders[i]
#                     break
#         return ret
            
# def parse(order_book = OrderBook()):
#     while True:
#         line = input().strip().split()
#         if line[0] == 'end':
#             break

#         is_buy = line[0] == 'buy'
#         qty, price = line[1:]
#         order_book.add(Order(is_buy, qty, price))

# with OrderBook() as order_book:
#     parse()
# order_book.add(Order(True, 10, 11.0))


# def f():
#     n = 0
#     while True:
#         yield n
#         n+=2

# # print(next(f(),3))
# # print(next(f()))
# # print(next(f()))
# # print(next(f()))

# # e = next(f())
# # # print(next(e))
# # # print(next(e))
# # print(e)


# #

# # what term correctly refers to the type __init__?
# # a) constructor
# # b) initializer
# # c) initializer method
# # d) constructor method
# # e) constructor function



# class customeContext:

#   # open file 
#     def __init__(self, filename, mode):
#         self.file = open(filename, mode)

