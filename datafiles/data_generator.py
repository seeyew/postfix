import random

operators = ['+','-','*','/']
columns = 26
base_string=",".join(['{}' for x in range(columns)])
# print(base_string)
# print(base_string.format(*["1" for x in range(columns)]))
newline = False
with open('datafiles/large_dataset.csv', 'w') as f:
    for i in range(10**5):
        row_values = ["{} {} {}".format(random.randint(-100,100),random.randint(-100,100),operators[random.choice(range(0, len(operators)))]) for x in range(columns)]
        _ = f.write("{newline}{value}".format(value=base_string.format(*row_values), newline = "\n" if i > 0 else ""))
