# nested loop means for each i , j loops until its is finished (no matter what, j will b loopn)
# ( where i will be constant until j finishes up )


import re
from typing import Sequence
import pytesseract as tess
import pyautogui,keyboard
import datetime
tess.pytesseract.tesseract_cmd =r'D:\Program Files\Tesseract-OCR\tesseract.exe'
from PIL import Image   #pip install SpeechRecognition

import os,sys,time
import subprocess


def p():
     time.sleep(3)
     print(pyautogui.position())

# p()

################################################################


# assign 2 expressions in list comprehension
# [(pyautogui.click(r'C:\Users\Tushar\Desktop\python\pics\button.png'), power_button.off = 'off')  if 'Power off' in text else speak('Buddy the switch is already on ')]


# check patterns 
# count no of rows == outer iterations
# count no of columns == with respect to each row
# [ print('*'*i) for i in range(5)  ]

################################################################
# get word where vowels match == n

# a = ['qieawa','rtwwi','ahedo','iou']
# n = 3
# for  i in a:
#     count = 0
#     for each_word in set(i) :
#         if each_word.lower() in ('a','e','i','o','u'):
#             count += 1
#     if count == n:
#         print(i )

################################################################

arr= [9,7,4]

# def loop(arr):
#     for i in range(len(arr)):
#         # for j in range(i,len(arr)):
#         for j in range(i+1,len(arr)):   # here j runs according to i when i == 0 , j == 1 , i == 1 , j == 2 (+1)
         
#             print(i,j)
#             # print(arr[j])

# loop(arr)

# def summ(arr):
#     if len(arr)==0:
#         return 1
#     else:
#         return arr[0] + summ(arr[1:])
# print(summ([9,7,4]))


# def ch(arr):
#     if len(arr)==1:
#         return arr[1]
#     else:
#         return arr[0] + arr[1:]

# ch()


# if type == list , im gonna function call() and loop over it and finally add to output else im adding it only
# output = []     
# def remove_nested_list(l):
#     for i in l:
#         if type(i) ==list:
#             remove_nested_list(i)   # here im sure  'i'  will be a list and I will  loop over it 
#         else:
#             output.append(i)

# remove_nested_list([1, 2, [3, 4, [5, 6]], 7, 8, [9, [10]]])
# print(output)

# nested_list=[1, 2, [3, 4, [5, 6]], 7, 8, [9, [10]]]
nested_list=[1, 2, [3, 4,]]


def count_total_from_nested_list(arr):
    total=0
    for i in arr:
        if type(i) == list:
            print(count_total_from_nested_list(i)) # We give the function with parameter as a list 
            total +=count_total_from_nested_list(i) #  i Becomes  arr so , it will go to loop and get added in total
        else:
            total +=i
   
    return total

# count_total_from_nested_list(nested_list)

arr=[1,3,5,6]

def lc1(arr):
    target =2
    for i in range(len(arr)):
        for j in range(i+1,len(arr)):
            if arr[i]+arr[j] ==target:
                return i,j
            
def lc2(arr):
    target = 62
    for i in range(len(arr)):
        if target == arr[i]:
            return i

        elif arr[i] > target:
            return i
    return len(arr)
        
# print(lc2(arr))





# def stockBuySell(price, n):
     
#     # Prices must be given for at least two days
#     if (n == 1):
#         return 
     
#     # Traverse through given price array
#     i = 0
#     while (i < (n - 1)): # price = [100, 180, 260, 310, 40, 535, 695]
         
#         # Find Local Minima
#         # Note that the limit is (n-2) as we are
#         # comparing present element to the next element
#         while ((i < (n - 1)) and
#                 (price[i + 1] <= price[i])):
#             i += 1
         
#         # If we reached the end, break
#         # as no further solution possible
#         if (i == n - 1):
#             break
         
#         # Store the index of minima
#         buy = i
#         i += 1 #price = [100, 180, 260, 310, 40, 535, 695]
         
#         # Find Local Maxima
#         # Note that the limit is (n-1) as we are
#         # comparing to previous element
#         while ((i < n) and (price[i] >= price[i - 1])):
#             i += 1
             
#         # Store the index of maxima
#         sell = i - 1
         
#         print("Buy on day: ",buy,"\t",
#                 "Sell on day: ",sell)
         
# # Driver code
 
# # Stock prices on consecutive days
pricess2 = [100, 180, 695,260, 310, 40, 535,5 ]
pricess = ['a','b','c','d','e','g','f']
# n = len(price)
 
# # Function call
# stockBuySell(price, n)

# f_l=[{pricess[i]:pricess2[i]} for i in range(len(pricess))]

# print(sorted([(k,v)for each_dic in f_l for k,v in each_dic.items()],key=lambda x:x[1]))
# print(f_l)
# print(sorted(pricess2,key=lambda x:x[0]))


''' l = [3,5,2,6]
for each_item_in_list in range(len(l)):  # len == 3
     for j in range(len(l)-1):  # len = 3-1 = 2, len = 2-1 = 1, len = 1-1 = 0
          print(len(l)-1)
          # print(l[j],l[j+1],sep=' ') 
     print()
     # print(l,l[each_item_in_list],sep=' ')
     print()
     #      if l[j] > l[j+1]:
     #           l[j],l[j+1] = l[j+1],l[j]
     # print(l)

# for each in l:
#         each j == 3,5,2

# Therefore, if we have n elements in our list, \
# we would have n iterations per item -
#  thus Bubble Sort's time complexity is O(n^2).
#'''

class BobbleSort():
    def sort_bubble(self,new_list):
        # import pdb; pdb.set_trace()
        for each_iteration in range(len(new_list) ):
            for each_number in range(len(new_list) - 1 ):
                if new_list[each_number] > new_list[each_number + 1]:
                    new_list[each_number] , new_list[each_number + 1] = new_list[each_number+1] ,new_list[each_number]
        return new_list
        # for each number , if the curr number is greater than the next number , keep on swapping until end is reached

FIRST_LIST = BobbleSort()
# print(FIRST_LIST.sort_bubble(pricess2) )



''' We see that as i ( outer loop ) increases, we need to need to check and send less items. 
O(n^2).'''
class SelectionSort():
    def __init__(self,val):
        self.val = val
    def sort_selection(self):
          for each_outer_loop_iteration in range(len(self.val)):
            # all outer loop values are minimum
               min_value = each_outer_loop_iteration
               for next_element in range( each_outer_loop_iteration + 1, len(self.val)  ):
                    print(next_element)
                # the 0 index of outer loop gets compared with the inner loop index iterations 
          
               #  print( each_outer_loop_iteration,self.val[each_outer_loop_iteration] ,' checks if it is less than > ',  next_element,self.val[next_element]  )
                    if self.val[each_outer_loop_iteration]  > self.val[next_element]:
                         min_value = next_element
                         self.val[each_outer_loop_iteration], self.val[min_value] = self.val[min_value], self.val[each_outer_loop_iteration]
          print(self.val)
SECOND_LIST = SelectionSort([1,40,4,2,3])
# SECOND_LIST.sort_selection() 

class SortingAlgo():
    def quicksort(self,SEQUENCE):
        ''' FASTEST SORTING ALGORITHM '''
        length = len(SEQUENCE)
        """ make a pivot point and 
        compare the rest of the numbers with the pivot point and return the list 
        Do it for every number  """
        if length <= 1:
            return SEQUENCE
        else:
            pivot = SEQUENCE.pop()

        items_greater = []
        items_lower = []

        for every_item in SEQUENCE:
            if every_item > pivot:
                items_greater.append(every_item)

            else:
                items_lower.append(every_item)
        print(SEQUENCE,pivot,sep='\t')
        print('BIG LIST',items_greater)
        print('SMALL LIST',items_lower)
        print()
        return self.quicksort(items_lower) + [pivot] + self.quicksort(items_greater)

 
THIRD_LIST = SortingAlgo()
# print(THIRD_LIST.quicksort(SEQUENCE = [3,9,5,1]))

########################################################################
#                           highest group number in string

# s = "bab95ad12g5og54"
# l = []
# for i in range(len(s)):
#     if s[i].isnumeric():
#         l.append(i)
# l_= []
# for j in range(len(l)-1):
#     if l[j] - l[j+1] == -1 :
#         l_.append(int(s[l[j]]+s[l[j+1]]) )
# print(max(l_))
########################################################################




# list1=[1,2,3]
# list2 =list1
# list3 = [3,4,5]
# list4 = list3
# list1[:] = [10,20,30]
# list3 = [30,40,50]

# print(list2)
# print(list4)


# d = {1:True,2:False}

# x = [1,2] 
# sum_ = 0 
# for  i in x:
#     print(d.get(i, False))
#     sum_ += True
#     # sum_ += d.get(i, False)
# print(sum_)


l = [[3,4.0,2,8.4,6],[0,2,0.2,4,6],[9,3.5,0.32,5,4]]


# for i in range(3):
#     # for j in range(3,0,-1):   # 123 123  123
#     # for j in range(i+1):      # 1   12   123
#     # for j in range(3,i,-1):   # 321 32     1
#     for j in range(i+2):      # 
#         print(j+1,end=' ')
#     print('\n')


################################################################################################
# word = 'ABCDEFGHIJKLIMNOQRSTUVWXYZ'

# def wrap(string, max_width):

#     return "\n".join([string[i:i+max_width] for i in range(0, len(string), max_width)])

# def wrap(string, max_width):
#     l = []
#     for i in range(0, len(string), max_width):
#         # print('\t\t',word[i*4:4*i+4])
#         # print('\t\t',i*4,(i+1)*4)
#         print(i,i+max_width)
    # return'\n'.join(l)
    # return l   
# print(wrap(word,4))


''' startswith can check 2 group values at once for when in range(str[i:])
like checking substring in string ie 56 in 565667 == 2'''

# a=lambda x : x+1
# checks =['a']

# eval can be used to extract the string to its original form
# but i am not able to use above checks for that
#  EVAL -  It is not a built in standalone function. It is a method of str.

# assign functions in checks using eval - cant be possible because eval execs standalone functions
# checks =['isupper()','islower()','isdigit()','isalpha()','islower()','isalnum()']


# def solve(s):
#     return s.title() if ''.join(s).isalpha() else s

# print(solve('hello world')) 

################################################################################################


a = [3,4,2]

# for each in a:
#     get_last_numfrom_each = each - 1
#     get_right_numfrom_each = each + 1
#     while get_last_numfrom_each != 0:
#         print(get_last_numfrom_each,end=' ')
#         get_last_numfrom_each -= 1
#     print()

#     while get_right_numfrom_each <= 5:
#         print(get_right_numfrom_each,end=' ')
#         get_right_numfrom_each += 1
#     print()
#     print()
#     print('\n')
numbers = [3,5,2,9]

# array = {x:0 for x in numbers}

# for number in numbers:
#     if array[number] == 0:
#         left_count_of_number = number - 1
#         right_count_of_number = number + 1

#         while left_count_of_number   :
#             print(f'number = {number}',
#             f'its left count is {left_count_of_number}')
#             left_count_of_number -= 1

#             if left_count_of_number in array:
#                 array[left_count_of_number] += 1
#                 break
#         print()
# print(array) 
        
     
'''                 Code
# Your code here
def main ():
	word = input()
	print("Gravity" if word == 'Apple' else 'Space')
# main()


#                       Take inputs according to the range of l in one line
#                   words = [word for word in input().split(" ", l-1) ]   

def main():
    l = int(input())
    d = {}

    #                  Take inputs in one line
    #           words = [word for word in input() ]   
    
    for i in words:
        if i not in d:
            d[i] = 1
        else:
            d[i] += 1
    print('Nutan' if max(d, key=d.get) == 'N' else 'Tusla')

# main()




'''

# strs = ["eat","tea","tan","ate","nat","bat",'anana']

# for i in range(len(strs)-1):
#     if strs[i] == strs[i+1][::-1]:
#         print(str[i])
#     else:
#         print(strs[i],strs[i+1])

# check duplicate number in nums 
nums = [1,2,2]


# output = []
# for i in range(len(nums)):
#     print(i+1,nums[i])
#     if i+1 != nums[i]:
#         output.append(i+1)
#     if nums[i] in nums[i+1:]:
#         output.append(nums[i])

# print(output)
        


# bubble sort 
class algo:
    l = [3,5,2,9]
    def bubble(self,l = l):
        for i in range(len(l)-1):
        
        #     if l[i] > l[i+1]:
        #         l[i],l[i+1] = l[i+1],l[i]
        # print(l)

            for each_iteration in range(len(l)-1):
                # print('L > ',l)
                if l[each_iteration] > l[each_iteration+1]:
                    l[each_iteration],l[each_iteration+1] = l[each_iteration+1],l[each_iteration]
        print(l) 

    def insertion(self,l = l):
        for i in range(len(l)):
            for j in range(len(l)):
                print('  ',l[i],l[j])
                if l[i] < l[j]:
                    l[i],l[j] = l[j],l[i]
        print(l)

   
    def insta_question(self):
        # s = {'the','quick','brown','fox','quick','word'}
        s = "geeks for geeks contribute practice".split(' ')
        word1 = 'geeks'
        word2 = 'contribute'
        
        print(s)
        index1,index2 = 0,0
        for index,val in enumerate(s):
            if word1 == val :
                index1 = index
            if word2 in val:
                index2 = index
        print(index1,index2)
        print(index2-index1)
       
# obj = algo()
# obj.bubble()
# obj.insertion()
# obj.insta_question()



