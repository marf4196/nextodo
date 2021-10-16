import logging

logging.basicConfig(filename='logfile.log' ,level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s:%(message)s')


def add(x,y):
    return x + y

def sub(x,y):
    return x - y

def mult(x,y):
    return x * y

def div(x,y):
    return x / y

num1 = 10
num2 = 5

add_result = add(num1, num2)
logging.debug(f'add: {num1} + {num2} = {add_result}')
# print(f'add: {num1} + {num2} = {add_result}')

sub_result = sub(num1, num2)
logging.debug(f'sub: {num1} - {num2} = {sub_result}')
# print(f'sub: {num1} - {num2} = {sub_result}')

mult_result = mult(num1, num2)
logging.debug(f'mult: {num1} * {num2} = {mult_result}')
# print(f'mult: {num1} * {num2} = {mult_result}')
  
div_result = div(num1, num2)
logging.debug(f'div: {num1} / {num2} = {div_result}')
# print(f'div: {num1} / {num2} = {div_result}')