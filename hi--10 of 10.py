#!/usr/bin/python
#coding:utf-8
"test"

NUM = 5

def laugh():
    "laugh"
    print 'HaHaHaHa'

def main():
    "main"
    for i in range(1, NUM):
        print i
        laugh()


if __name__ == "__main__":
    main()