
#!/bin/bash

echo -e "\n\tThis is bash scripting practice\n \t $date "
echo -e "\nSpell Your name"
read name
echo -e "\nWhats your age ? "
read age
echo -e "\nHello $name this is bash scripting practice where your age $age is shown using $ sign and input is taken via read "
echo -e "\nNow some variables are built-in -> $+RANDOM ,  $+whomami  $+pwd $pwd"
sleep 1
echo ' There are 2 ways for giving  newline >>>     echo -e "new \n word"   >>> 2    echo $"heelo\nyo" '
sleep 1
echo -e "\nTime.sleep == sleep 2 where 2 sec delay is shown "
sleep 1
echo -e "\nFor doing any mathematical calculations we do it by $((4 + 3))   $(()) + 2 brackets open "
sleep 1
echo -e "\nNow we create a variable by   twitter = "elon musk" , remember just like python we dont need to define data type before and value should be in double quotes comma not single quotes to make it work "
sleep 1
echo -e "\nNow you name a twiiter id , ill save it as a variable"
read twitter
echo -e " \n $twitter  >>> this was your name you stored \n "

echo -e "\n Final thing for today\n 07-05-2022\n"
echo -e  " making variable global by \texport twitter in terminal \t, but since you writing this script in child process (ie here  == shell script file) \n this variable wont be shwon when you create in terminal \t so we need to make it permanent variable by \t going to .bashrc | export twitter = elon musk  \t This will make a system variable \t But you need to restart terminal to confirm and get the output  \n"

echo "Lets talk about postional argument"
val = $1

echo -e " so val is postional arg where when script runs ir ./getrich.sh  tushar\n"
echo -e "your val like this is printed out $val"
