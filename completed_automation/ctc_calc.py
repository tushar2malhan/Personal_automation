import datetime
import time

def calculate_():
     monthly = salary / 12 * 100000
     print('#########################################\n\t SALARY BREAKDOWN\n')
     print(f'Your NET salary is: \t\t\t \u20B9 {round(monthly)} on monthly basis')
     time.sleep(10)
     SALARY_DEDUCTIONS = 1000
     basic_expenses = 5000
     TOTAL_EXPENSES = SALARY_DEDUCTIONS + basic_expenses
     print(f'Your SALARY DEDUCTIONS from net salary are : \t\t \u20B9 \033[91m{SALARY_DEDUCTIONS}\033[0m')
     time.sleep(3)
     print( f'\nYour basic expenses are \033[91m{basic_expenses}\033[0m  monthly which \n\
          include preteinence, medical, housing, food, transport etc.')
     print(f'So Savings on monthly basis will  be \u20B9 {round(monthly)} -  \033[91m{TOTAL_EXPENSES}\033[0m \n' )
     time.sleep(5)
     savings =  round(monthly - TOTAL_EXPENSES)
     last_month = datetime.datetime.now().month - 1
     current_month = datetime.datetime.now().strftime("%B")

     print(f'#########################################\n')
     print(f'Savings for {current_month} will be  \t\u20B9{savings}')
     print(f'\n#########################################')
     time.sleep(5)
     print(f'\033[1m')

     print(f'\nNow by the end of the year { datetime.datetime.now().year},\n You will have \n  {savings*12} \n')
     time.sleep(5)

for _ in range(3):
     try:
          salary = int(input('\nYour annual salary in CTC: '))
          calculate_()   
          break
     except ValueError:
          print ('Please enter a valid number')
