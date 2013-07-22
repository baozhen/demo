#!/bin/env python2
# coding:UTF-8

import time
import sys
import random

lenth = 300000

def qsort(arr, left, right):
    key = arr[right]
    lp = left
    rp = right
    if lp == rp:return
    while True:
        while (arr[lp] >= key) and (rp > lp):
            lp = lp + 1
        while (arr[rp] <= key) and (rp > lp):
            rp = rp - 1
        arr[lp], arr[rp] = arr[rp], arr[lp]
        if lp >= rp: break
    arr[rp], arr[right] = arr[right], arr[rp]
    if left < lp:
        qsort(arr, left, lp-1)
    qsort(arr, rp, right)

def main():
    arr = []
    sys.setrecursionlimit(100000)
    for i in range(lenth):
        arr.append(random.randint(0, 1000000))
    qsort(arr, 0, lenth-1)
    print arr

if __name__ == '__main__':
    for i in range(1):
        main()
