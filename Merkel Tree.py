from hashlib import md5

class Node:
    def __init__(self):
        self.l=None
        self.r=None
        self.p=None
        self.hash="\\"
        self.data="\\"

    def change_data(self,data):
        self.data=data
        m=md5()
        m.update(data.encode('utf-8'))
        self.hash=m.hexdigest()
        return self.hash



class merkle_tree:
    def __int__(self):
        self.root = None
        self.h=0
        self.leaf=0
    #     添加 h层树的节点
    def add(self,item,h):
        l= Node()
        r=Node()
        l.p=item
        item.l=l
        r.p=item
        item.r=r
        h = h - 1
        if h==0:
            return
        else:
            self.add(l,h)
            self.add(r,h)

    def creat(self,h):
        self.root=Node()
        self.h=h
        self.leaf=2**h
        self.add(self.root,h)
        return self.root
    # 从左到右添加叶子节点
    def update(self,data,hash):
        if self.leaf==0:
            print("本树已满")
            return
        temp=self.root
        h=self.h
        leaf=self.leaf

        while(h!=0):
            if leaf>2**(h-1):
                leaf=leaf-2**(h-1)
                temp=temp.l
            else:
                temp=temp.r
            h=h-1
        self.leaf-=1
        temp.data=data
        temp.hash=hash
        self.up_update(temp)
        return temp
    def up_update(self,temp):
        if temp.p!=None:
            temp=temp.p
            m=md5()
            m.update((temp.l.hash+temp.r.hash).encode('utf-8'))
            temp.hash=m.hexdigest()
            self.up_update(temp)

    # 左到右 遍历
    def show1(self,root):
        if root.l!=None:
            print("向左",end="")
            self.show(root.l)
            print("向右", end="")
            self.show(root.r)
        if root.l==None:
            print(root.hash)
            print(root.data)
    # 层次遍历
    def show2(self,root):
        x=[]
        cc=[]
        x.append(root)
        print("\t",root.hash)
        while x!=[]:
            if x[0].l==None:
                break
            for _ in range(len(x)):
                print("\t",'%-70s' % x[_].l.hash,end="")
                print("\t",'%-70s' % x[_].r.hash,end="")
                cc.append(x[_].l)
                cc.append(x[_].r)
            print("")
            x=cc
            cc=[]



    def show_tree(self):
        root=self.root
        self.show2(root)

    #     除了根节点
    def sum(self,root):
        if root.l!=None and root.r!=None:
            return 2+self.sum(root.l)+self.sum(root.r)
        if root.l==None or root.r ==None:
            return 0



# test
b=merkle_tree()
b.creat(10)
print(b.sum(b.root))
for i in range(10):
    b.update(i,"hash")


b.show_tree()