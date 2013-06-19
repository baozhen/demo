b = [1,2,3]
a = [4,5,6]


def change_list(b):
    b[0] = b[0] + 1
    return b

def exchange(a,b):
    tmp = a
    a = b
    b = tmp
    return a,b

print exchange(a,b)
