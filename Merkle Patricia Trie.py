
import hashlib
import time
#定义branch节点类
class Branch_ndoe:
    def __init__(self):
        self.type = 'branch'
        self.children = {'0': None, '1': None, '2': None, '3': None, '4': None, '5': None,
                         '6': None, '7': None, '8': None, '9': None,
                         'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'value': False}

#定义extension节点类
class Extension_node:
    def __init__(self):
        self.type = 'extension'
        self.key = None
        #将branch节点和extension节点捆绑在一起，branch节点作为extension节点的组成元素，对外只有extension和leaf两种类型的节点
        self.value = Branch_ndoe()
        self.prefix = None
        #对节点的hash值
        self.node_hash = None
        #对节点下的数据的hash
        self.node_value = None
#定义leaf节点类
class Leaf_node:
    def __init__(self):
        self.type = 'leaf'
        self.key_end = None
        self.value = None
        self.prefix = None
        #对节点下的数据的hash值
        self.node_value = None
        #对节点的hash值
        self.node_hash = None
#定义MPT树类
class Tree:
    def __init__(self,tree=None):
        #传入MPT树构建
        if tree != None:
            self.root = tree
        #否则，root节点创建新的extension
        else:
            self.root= self.make_extension()
            #默认根节点的前缀是root
            self.root.prefix = 'root'
            #定义树的value和hash
            self.value = None
            self.hash = None

    def add_node(self,node,key,value):
        #父节点为root 的情况
        if node.prefix == 'root':
            #root节点下branch表对应值为空，直接插入
            #默认将key【0】作为extension（root）节点下branch的索引
            #key【1：：】才是后续传递的new_key值，即去掉共同前缀的剩余部分
            if self.root.value.children[key[0]] == None:
                self.root.value.children[key[0]] = self.make_leaf(key[1::],key[1::],value)
                # 插入新的leaf节点后，节点数据发生改变，状态改变
                node.value.children['value'] = False
                return
            #root节点下branch表发生冲突，将冲突的节点位置作为参数进行递归
            else:
                self.root.value.children[key[0]] =  self.add_node(self.root.value.children[key[0]],key[1::],value)
                return
        father = node
        index = self.diff(father,key)
        prefix = key[:index:]
        new_key = key[index::]
        if index != len(father.prefix) and index < len(father.prefix):
            #extension冲突
            if father.type == 'extension':
                #调用函数，创建新的extension节点，解决冲突
                return self.pre_extension(father,prefix,new_key,index,value)
            #leaf冲突
            elif father.type == 'leaf':
                # 调用函数，创建新的extension节点，解决冲突
                return self.pro_extension(father,prefix,new_key,index,value)
        #否则，进入extension的branch中向下遍历
        else:
            if father.value.children[key[index]] == None:
                father.value.children[key[index]] = self.make_leaf(key[index+1::],key[index])
                father.value.children['value'] = False
                return father
            else:
                father = self.add_node(father.value.children[key[index]],new_key,value)
                return father
    #解决extension节点与leaf节点的冲突,向前添加extension节点
    def pre_extension(self,node,prefix,key,index,value):
        node_new_prefix = node.prefix[index+1::]
        #创建新的extension节点
        tmp_node = self.make_extension()
        #写入共同前缀
        tmp_node.prefix = prefix
        #将旧的extension节点插入branch表中
        tmp_node.value.children[node.prefix[index]] = node
        #修改旧的extension节点的共同前缀
        tmp_node.value.children[node.prefix[index]].prefix = node_new_prefix
        #插入leaf节点
        tmp_node.value.children[key[0]] = self.make_leaf(key[1::],key[0],value)
        #返回新的extension
        return tmp_node
    #解决leaf节点与leaf节点的冲突，向后添加extension节点，与向前插入基本相同，区别在于不需要修改prefix
    def pro_extension(self,node,prefix,key,index,value):
        leaf = node
        # 创建新的extension节点
        tmp_node = self.make_extension()
        # 写入共同前缀
        tmp_node.prefix = prefix
        # 将旧的leaf节点插入branch表中
        tmp_node.value.children[leaf.key_end[index]] = leaf
        #产生共同前缀，leaf节点的key_end发生改变
        tmp_node.value.children[leaf.key_end[index]].key_end = leaf.key_end[index+1::]
        # 插入新的leaf节点
        tmp_node.value.children[key[0]] = self.make_leaf(key[1::],key[0],value)
        #返回新的extension
        return tmp_node
    #创建叶节点
    def make_leaf(self,key,profix,value):
        tmp_node = Leaf_node()
        tmp_node.key_end = key
        tmp_node.prefix = profix
        # 添加leaf节点的值和hash
        tmp_node.value = value
        #对数据进行hash
        tmp_node.node_value = hashlib.sha256(value.encode('utf-8')).hexdigest()
        #对节点进行hash，顺序在数据hash之后，确保为最后的改动
        tmp_node.node_hash = hashlib.sha256(str(tmp_node).encode('utf-8')).hexdigest()
        return tmp_node

    #创建extension节点
    def make_extension(self):
        tmp_node = Extension_node()
        return tmp_node

    #获取差异值索引
    def diff(self,node,key):
        if len(key) < len(node.prefix):
            lenth = len(key)
        else:
            lenth = len(node.prefix)
        count = 0
        while count < lenth:
            if node.prefix[count] != key[count]:
                return count
            count+=1
        return count
    #遍历MPT树查询
    def traverse_search(self,node,index):
        #最终返回的节点的索引
        result_node = None
        #遍历当前extension节点的branch表
        for key in  node.value.children:
            #终止标志
            if key == 'value':
                break
            #检索到空值，继续循环
            if node.value.children[key] == None:
                continue
            #检索到leaf节点，对比key_end和索引值
            if node.value.children[key].type == 'leaf':
                #如果匹配，返回该节点
                if index[1::] == node.value.children[key].key_end:
                    result_node =  node.value.children[key]
                    break
                #否则继续检索
                else:
                    continue
            #检索到extension，进入到该节点的branch向下索引
            elif node.value.children[key].type == 'extension':
                #记录去除该extension节点的共同前缀后剩余的索引值
                short_key = index[len(node.value.children[key].prefix)+1::]
                #递归向下索引
                result_node = self.traverse_search(node.value.children[key],short_key)
                if result_node != None:
                    break
        return result_node
    #打印MPT树
    def print_all(self,node):
        print('extension of prefix:',node.prefix)
        for key in node.value.children:
            if key == 'value':
                break
            if node.value.children[key] == None:
                continue
            if node.value.children[key].type == 'leaf':
                print('branch:', key)
                print('leaf of key_end:',node.value.children[key].key_end)
            elif node.value.children[key].type == 'extension':
                print('branch:', key)
                self.print_all(node.value.children[key])

    #更新树，查询之前需要进行更新
    def update_tree(self,node):

        tmp_str = ''
        if node.value.children['value'] == True:
            return node.node_value
        for key in node.value.children:
            if key == 'value':
                break
            if node.value.children[key] == None:
                continue
            if node.value.children[key].type == 'leaf':
                #聚合leaf节点
                tmp_str = tmp_str + node.value.children[key].node_value
            elif node.value.children[key].type == 'extension':
                #聚合extension节点，同时向下递归遍历
                tmp_str = tmp_str + self.update_tree(node.value.children[key])
        #节点修改状态
        node.value.children['value'] = True
        #更新节点value，hash值
        node.node_value = hashlib.sha256(tmp_str.encode()).hexdigest()
        node.node_hash = hashlib.sha256(str(node).encode()).hexdigest()
        print('prefix:',node.prefix)
        print('node_value:',node.node_value)
        return node.node_value

    #通过遍历检索到需要删除的节点，然后使其对应的branch位置设为None值，再用del回收内存
    def delete_node(self,node,hash):
        for key in node.value.children:
            if key == 'value':
                break
            if node.value.children[key] == None:
                continue
            if node.value.children[key].type == 'leaf':
                if hash[1::] == node.value.children[key].key_end:
                    del node.value.children[key]
                    node.value.children[key] = None
                    return True
                else:
                    continue
            elif node.value.children[key].type == 'extension':
                short_hash = hash[len(node.value.children[key].prefix) + 1::]
                if short_hash == '':
                    del node.value.children[key]
                    node.value.children[key] = None
                    print('delete')
                    return True
                elif self.delete_node(node.value.children[key],short_hash):
                    return True


    #增操作，同时更新MPT树
    def add(self,key,value,node=None):
        if node == None:
            node = self.root
        self.add_node(node,key,value)
        self.update_tree(self.root)
    #删操作，同时更新MPT树
    def delete(self,key):
        print('delete from str')
        self.delete_node(self.root,key)
        self.update_tree(self.root)
    #改操作，同时更新MPT树（简化，只提供修改leaf节点的value值）
    def update(self,index,value):
        if type(index) == str:
            tmp_node = self.traverse_search(self.root,index)
            tmp_node.value = value
            # 对数据进行hash
            tmp_node.node_value = hashlib.sha256(value.encode('utf-8')).hexdigest()
            # 对节点进行hash，顺序在数据hash之后，确保为最后的改动
            tmp_node.node_hash = hashlib.sha256(str(tmp_node).encode('utf-8')).hexdigest()
        else:
            index.value = value
            # 对数据进行hash
            index.node_value = hashlib.sha256(value.encode('utf-8')).hexdigest()
            # 对节点进行hash，顺序在数据hash之后，确保为最后的改动
            index.node_hash = hashlib.sha256(str(index).encode('utf-8')).hexdigest()
        self.update_tree(self.root)

    def search(self,index):
        if type(index) == str:
            return self.traverse_search(self.root,index).value
        else:
            return index.value
    def drop_all_value(self,node=None):
        #self.update_tree(self.root)
        if node == None:
            node = self.root
        for key in node.value.children:
            if key == 'value':
                break
            if node.value.children[key] == None:
                continue
            if node.value.children[key].type == 'leaf':
                del node.value.children[key].value
                node.value.children[key].value = None
            elif node.value.children[key].type == 'extension':
                self.drop_all_value(node.value.children[key])

    def drop_tree(self):
        self.update_tree(self.root)
        self.value = self.root.node_value
        self.hash = self.root.node_hash
        del self.root
        self.root = None