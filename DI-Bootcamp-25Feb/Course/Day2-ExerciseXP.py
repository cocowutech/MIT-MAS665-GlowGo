# Exercise 1 : Hello World
print('Hello world\n'*4)

# Exercise 2 : Some Math
s = (99^3)*8
print(s)

#Ex3
print(5 < 3) #false
print(3 == 3) # true
print(3 == "3") #false
#print('3' > 3) #'>' not supported between instances of 'str' and 'int
print('Hello' == 'hello') #false

#Ex4
computer_brand = 'macpro'
print(f'I have a {computer_brand} computer.')

#Ex5
name = 'coco'
age = 26
shoe_size = 38
info = f'{name} is {int(age)}, but she has a shoe size of {int(shoe_size)}'
print(info)

# Exercise 6 : A & B
a = 3
b = 5
if a > b:
    print('Hello world')

#Exercise 7 : Odd or Even
user_input = input('please give me a number')
if int(user_input)%2 ==0:
    print('even')
else:
    print('odd')

#Ex8 :What’s your name ?
user_input2 = input("what's your name?")
myname = 'coco'
if str(user_input2) == myname:
    print('wow we have the same name')
else: 
    print("oops, it's not meant to be")