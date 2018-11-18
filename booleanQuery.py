from collections import deque
from inverted_index import *

Ops = ["NOT", "AND", "OR"]


class Node:

    def __init__(self, data):
        self.left = None
        self.right = None
        self.data = data


def printPreOrder(root: Node):
    if root is None:
        return
    printPreOrder(root.left)
    print(str(root.data))
    printPreOrder(root.right)


query = '((south AND (african AND ward)) NOT sanctions)'
simple = '()'


def parseBoolExp(st: str):
    # print(st)
    if len(st) == 0 or (not ('(' in st)):
        spl = st.split(" ")
        if len(spl) == 1:
            return Node(spl[0])
        leafLeft = Node(spl[0])
        opNode = Node(spl[1])
        leafRight = Node(spl[2])
        opNode.left = leafLeft
        opNode.right = leafRight
        return opNode
    if st[0] == '(' and st[-1:] == ')':
        return parseBoolExp(st[1:-1])
    else:
        # from left only
        if st[0] == '(' and st[-1:] != ')':
            last = st.rindex(")")
            rightOpernd = list(filter(lambda x: len(x) != 0, st[last + 1:].split(" ")))
            opNode = Node(rightOpernd[0])
            opNode.right = Node(rightOpernd[1])
            opNode.left = parseBoolExp(st[1:last])
            return opNode
        # from right onlu
        elif st[-1] == ')' and st[0] != '(':
            first = st.index("(")
            leftOperand = list(filter(lambda x: len(x) != 0, st[:first].split(" ")))
            opNode = Node(leftOperand[1])
            opNode.left = Node(leftOperand[0])
            opNode.right = parseBoolExp(st[first:])
            return opNode


def makePostingListsTree(root: Node, idx: InvertIndex) -> Node:
    if root is None:
        return
    if root.data in Ops:
        nodeOp = Node(root.data)
        nodeOp.left = makePostingListsTree(root.left, idx)
        nodeOp.right = makePostingListsTree(root.right, idx)
        return nodeOp
    else:
        return Node(idx.findInIndex(root.data))


def mergeTreeOfPostingLists(root: Node) -> LinkedList:
    if root is None:
        return LinkedList()
    if root.data in Ops:
        if root.data == "AND":
            return mergeTreeOfPostingLists(root.left).intersect(mergeTreeOfPostingLists(root.right))
        if root.data == "NOT":
            return mergeTreeOfPostingLists(root.left).andNot(mergeTreeOfPostingLists(root.right))
        if root.data == "OR":
            return mergeTreeOfPostingLists(root.left).Or(mergeTreeOfPostingLists(root.right))
    else:
        return root.data


def BooleanRetrieval(queries, idx: InvertIndex):
    open("Part_2.txt", 'w').close()
    for tmpQuery in queries:
        tree = parseBoolExp(tmpQuery)
        postingTree = makePostingListsTree(tree, idx)
        res = mergeTreeOfPostingLists(postingTree)
        print("query " + tmpQuery)
        with open("Part_2.txt", 'a') as f:
            idmap = invIndex.docIdDocNo
            line = " ".join(map(lambda z: str(idmap[str(z)]), res.toList()))
            f.write(line + "\n")


def loadQueries():
    with open("BooleanQueries.txt") as qFile:
        lines = list(map(lambda line: line.rstrip('\n').replace("( ", "(").replace(" )", ")"), qFile.readlines()))
    return lines


queries = loadQueries()
print("running queries.....")
BooleanRetrieval(queries, invIndex)
# for q in queries:
#     print(q)
#     tree = parseBoolExp(q)
#     printPreOrder(tree)
