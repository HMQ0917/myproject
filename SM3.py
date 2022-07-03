from joblib import Parallel, delayed
import time

m='78226364636263f46162636451226364616863646c626984616263d461e2636461626d6461786363616263946f326c64646263646f2263646182635761656b6a'
IV='63f016cf4914b2b91a2242d7df8a9014a96f70b4163158a5e38d9e5db0fb1c2f'

def filling(m):
    length_b = len(m)*4#记录消息的长度
    b = m
    b = b + '8'#补 1
    c = len(b)%128
    c = 112 - c#补 0 的个数
    d = '0'*c
    b = b + d#补 0
    length_m = '{:016x}'.format(length_b)#也是16进制
    b = b + length_m#填充完毕
    return b

#分组函数
def fenzu(m):
    m = filling(m)
    len_m = len(m)/128
    m_list = []
    Parallel(n_jobs=8)(
        delayed(m_list.append)(m[0+128*i:+128*(i+1)])
        for i in range(int(len_m)))
    return m_list

#扩展函数
def expand(m,n):
    B = fenzu(m)
    W = ['0' for i in range(68)]
    W_0 = ['0' for i in range(64)]
    for i in range(int(len(B[n])/8)):
        w = B[n][i*8:(i+1)*8]
        W[i] = w
    for j in range(16,68):
        a = or_16(W[j-16],W[j-9])

        W_j_3 = Cyc_shift(W[j-3],15)
        a = or_16(a,W_j_3)
        a = Replace_P1(a)
        W_j_13=Cyc_shift(W[j-13],7)
        a = or_16(a,W_j_13)
        a = or_16(a,W[j-6])
        W[j]=a
    W_0=Parallel(n_jobs=8)(
        delayed(or_16)(W[j],W[j+4])
        for j in range(64))

    return W,W_0

#置换函数
def Replace_P1(X):
    #X为32位字
    X_15 = Cyc_shift(X,15)  #循环移位
    X_23 = Cyc_shift(X,23)
    a = or_16(X,X_15)
    a = or_16(a,X_23)
    return a

#置换函数
def Replace_P0(X):
    X_9 = Cyc_shift(X,9)
    X_17 = Cyc_shift(X,17)
    a = or_16(X,X_9)
    a = or_16(a,X_17)
    return a

#异或
def or_16(A,B):
    A = int(A,16)
    B = int(B,16)
    C = A ^ B
    C = '{:08x}'.format(C)
    return C

#循环移位
def Cyc_shift(W,n):
    a = int(W,16)
    a = '{:032b}'.format(a)
    while n>=32:
        n=n-32
    a = a[n:] + a[:n]
    a = int(a,2)
    a = '{:08x}'.format(a)
    return a

#常量Tj
def T_j(j):
    if j<=15:
        T_j='79cc4519'
    else:
        T_j='7a879d8a'
    return T_j

#mod 2^32
def add(x,y):
    x = int(x,16)
    x = '{:032b}'.format(x)
    x = list(x)
    y = int(y, 16)
    y = '{:032b}'.format(y)
    y = list(y)
    a = [0 for _ in range(32)]
    carry = 0
    for i in range(32):
        m = int(x[31-i])+int(y[31-i])+carry
        if m>=2:
            d=m-2
            a[31-i]=str(d)
            carry=1
        else:
            carry=0
            d=m
            a[31 - i] = str(d)
    b=''.join(a)
    b=int(b,2)
    b='{:08x}'.format(b)
    return b

#FF
def FF_j(X,Y,Z,j):
    if j<=15:
        a = or_16(X,Y)
        a = or_16(a,Z)
    else:
        a = and_Cal(X,Y)
        b = and_Cal(X,Z)
        c = and_Cal(Y,Z)
        a = or_Cal(a,b)
        a = or_Cal(a,c)
    return a

#GG
def GG_j(X, Y, Z, j):
    if j <= 15:
        a = or_16(X, Y)
        a = or_16(a, Z)
    else:
        a = and_Cal(X,Y)
        b = neg(X)
        b = and_Cal(b,Z)
        a = or_Cal(a,b)
    return a

#与
def and_Cal(a,b):
    a = int(a,16)
    b = int(b,16)
    a_b = a & b
    a_b = '{:08x}'.format(a_b)
    return a_b

#或
def or_Cal(a,b):
    a = int(a, 16)
    b = int(b, 16)
    a_b = a | b
    a_b = '{:08x}'.format(a_b)
    return a_b

#按位取反
def neg(A):
    A = bin(int(A,16))[2:]
    B='1'*len(A)
    A=hex(int(A,2)^int(B,2))[2:]
    return A

#压缩函数
m_list = fenzu(m)
m_len = len(m_list)
V = ['0' for i in range(m_len+1)]
V[0]=IV

#压缩函数
def CF(m,n,k):
    w = expand(m, n)
    W = w[0]
    W_0 = w[1]
    A=V[k][0:8]
    B=V[k][8:16]
    C=V[k][16:24]
    D=V[k][24:32]
    E=V[k][32:40]
    F=V[k][40:48]
    G=V[k][48:56]
    H=V[k][56:64]

    r=''
    for j in range(64):

        b= a = Cyc_shift(A,12)
        T = T_j(j)
        #
        T = Cyc_shift(T,j)
        a = add(a,E)
        a = add(a,T)
        SS1 = Cyc_shift(a,7)
        SS2 = or_16(SS1,b)
        b = FF_j(A,B,C,j)
        b = add(b,D)
        b = add(b,SS2)
        TT1 = add(b,W_0[j])
        b = GG_j(E,F,G,j)
        b = add(b, H)
        b = add(b, SS1)
        TT2 = add(b, W[j])
        D = C
        C = Cyc_shift(B,9)
        B = A
        A = TT1#
        H = G
        G = Cyc_shift(F,19)
        F = E
        E = Replace_P0(TT2)
        r = A+B+C+D+E+F+G+H
    V[k+1]=or_16(V[k],r)


def SM3():
    for i in range(m_len):
        CF(m,i,i)
    return V[-1]


neg(m)
res=SM3()
print('输入的消息m是:\n',m)
print('消息m的hash值为:\n',res)