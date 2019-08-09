#coding:utf-8

class LNode(object):
    def __init__(self,x):
        self.data = x
        self.next = None

class MyQueue(object):
    def __init__(self):
        self.pHead = None
        self.pEnd = None

    def is_empty(self):
        if self.pHead == None:
            return True
        return False

    def size(self):
        size=0
        p = self.pHead
        while p != None:
            p = p.next
            size += 1
        return size

    def enQueue(self, element):
        p = LNode(element)
        p.data = element
        p.next = None
        if self.pHead == None:
            self.pHead = self.pEnd=p
        else:
            self.pEnd.next = p
            self.pEnd = p

    def deQueue(self):
        if self.pHead == None:
            pass
        self.pHead = self.pHead.next
        if self.pHead == None:
            self.pEnd = None

    def getFront(self):
        if self.pHead == None:
            return None
        return self.pHead.data

    def getBack(self):
        if self.pEnd == None:
            return None
        return self.pEnd.data