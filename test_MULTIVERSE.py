
arr = [2,4,1,5,6,3]

# insertion sort 
def check(arr):
    # import pdb;pdb.set_trace()
    # for i in range(len(arr)-1,0,-1): # Checking from Right to left
    for i in range(1,len(arr)):        # Checking from left to right
        next_element = i 
        # print('\t\t\n',arr[next_element-1] > arr[next_element],arr[next_element-1], arr[next_element],'\n')
        while arr[next_element-1] > arr[next_element] and next_element>0 :
            arr[next_element-1],arr[next_element] = arr[next_element],arr[next_element-1] 
            next_element -=1
    print(arr)
# check(arr)

# iterating each number from the list
# take a index position of the number in a variable = next_element
# if its smaller than previous number from the list 
# take a while loop where we keep on swaping the number , 
# reducing the index position from the current
# until  either it is bigger than the previous number or > 0 

def bubble(arr):
    import pdb;pdb.set_trace()
    for i in range(len(arr)):
        for j in range(len(arr)-1):
            print(i,j)
            if arr[j] > arr[j+1]:
                arr[j],arr[j+1] = arr[j+1],arr[j]

#     print(arr)
# bubble(arr)



# selection sort 

# def selection(arr):
#     for i in range(len(arr)):
#         min_index = i
#         for j in range(i+1,len(arr)):
#             if arr[min_index] > arr[j]:
#                 min_index = j
#         arr[i],arr[min_index] = arr[min_index],arr[i]
#     print(arr)

arr = [1,2,1]
# In this array, if next element  arr[i+1]
# is bigger than the current element, 
# then replace the value with the bigger element on current index
# If not then make current value -> Make current value -1 if not bigger on current index
# Make sure we traverse the array elements in circular way so that the last element start compares from reverse

def ok(arr):

    for i in range(len(arr)-1,0,-1):
        # import pdb;pdb.set_trace()
        index = i 
        while arr[index -1] > arr[index]:
            arr[index -1],arr[index] = arr[index],arr[index -1]
            # arr[index] = -1
            index -=1
    print(arr)
# ok(arr)

#  Array = [1,2,1]
# In this array, if next element is bigger than the current element, 
# then replace the value with the bigger element on current index
# If not then make current value ->  Make current value -1
# Make sure we traverse the array elements in circular way so that the last element start compares from reverse

# Make current value -1 if not bigger on current index




