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

def selection_sort_2(arr):
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
# selection_sort_2(arr)

# def selection_sort_3(arr):

#     for i in range(len(arr)-1):
#         while i>=0 and arr[i-1] > arr[i]:
#             arr[i-1], arr[i] = arr[i], arr[i-1]
#             i -= 1
#     print(arr)
# selection_sort_3(arr)


#                       Bubble Sort

def bubble(arr):
    # import pdb;pdb.set_trace()
    ''' arr = [64, 25, 12, 22, 11]
    '''
    ...