
def change_file_content(file,*words):
    """ change content in ReadME """
    with open(file)as f: # READ THE FILE
        #   FIRST WE SPLIT THE WHOLE FILE'S TEXT , SO THAT WE GET EACH LINE
        content = f.read().split('\n')
        #    NOW FROM THE WORD , GET THE LINE 
        line_1 = 'test_ting line eeeeee'
        change = '\n'+'\n'.join([line_1 for line in content if line.lower().startswith(words[0])] ) +'\n'
        # change_line_1 = 'hi this is test line'
        # print(change_line_1)
        # print(change)


    with open(file,'r+')as w:
              w.write(change)  
            #   print(w.read())           

# change_file_content(
# r'C:\Users\Tushar\Desktop\lancer\map\README.MD',
# 'consider')
# change_file_content(
# r'C:\Users\Tushar\Desktop\python\test_MULTIVERSE.txt',
# "'consider")