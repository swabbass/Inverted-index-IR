import xml.etree.ElementTree as ElementTree
from typing import Dict, Set

docCount: int = 1


class ListNode:
    def __init__(self, val):
        self.val = val
        self.next = None

    def __str__(self) -> str:
        return str(self.val)


class LinkedList:

    def __init__(self) -> None:
        self.head = None
        self.last = None
        self.current: ListNode = None

    def addLast(self, data: object) -> None:
        if self.head is None:
            self.head = ListNode(data)
            self.last = self.head
        else:
            self.last.next = ListNode(data)
            self.last = self.last.next

    def intersect(self, olinked):
        thisone = self.head
        otherone = olinked.head
        retval = LinkedList()
        while thisone and otherone:
            if otherone.val > thisone.val:
                thisone = thisone.next
            elif thisone.val > otherone.val:
                otherone = otherone.next
            else:
                retval.addLast(otherone.val)
                thisone = thisone.next
                otherone = otherone.next
        return retval

    def notIntersect(self, olinked):
        intersection = self.intersect(olinked)
        print(intersection)
        thisone = self.head
        otherone = intersection.head
        retval = LinkedList()
        while thisone and otherone:
            if otherone.val > thisone.val:
                thisone = thisone.next
            elif thisone.val > otherone.val:
                otherone = otherone.next
                retval.addLast(otherone.val)
            else:
                thisone = thisone.next
                otherone = otherone.next
        return retval

    def __iter__(self):
        self.current = self.head
        return self

    def __next__(self):
        if self.current is None:
            raise StopIteration
        tmp = self.current
        self.current = self.current.next
        return tmp

    def __str__(self) -> str:
        res = ""
        for item in self:
            res += str(item)
            res += " --> "
        return res


class LingModule:

    def __init__(self) -> None:
        self.maps = list()

    def addLingMapping(self, mapping):
        self.maps.append(mapping)

    def apply(self, data):
        tmp = data
        for mapping in self.maps:
            tmp = mapping(tmp)
        return tmp

    @staticmethod
    def toLowercase(stringSet: Set[str]):
        return set(map(lambda string: LingModule.toLowercaseStr(string), stringSet))

    @staticmethod
    def toLowercaseStr(string: str) -> str:
        return string.lower()


class IRDoc:

    def __init__(self, id, docNo, text, feildId) -> None:
        self.id = id
        self.docNo = docNo
        self.text: str = text
        self.fieldId = feildId
        self.lingModule = LingModule()
        self.lingModule.addLingMapping(LingModule.toLowercase)
        self.wordSet: set = self._tokenize()

    def _tokenize(self):
        words = set(self.text.split(" "))
        words = set(self.lingModule.apply(words))
        return words

    def __str__(self) -> str:
        return "id:" + str(self.id) + "\n" + "docNo:" + str(self.docNo) + "\n" + "text:" + str(
            self.text) + "\n" + "fieldId:" + str(self.fieldId) + "\n"

    def hasWord(self, word: str) -> bool:
        return self.lingModule.apply(word) in self.wordSet


class InvertIndex:

    def __init__(self) -> None:
        self.index: Dict[str, LinkedList] = dict()
        self.wordDocIdDict: Dict[str, set] = dict()
        self.docs: Dict[int, IRDoc] = dict()
        self.lingModule = LingModule()
        self.lingModule.addLingMapping(LingModule.toLowercaseStr)

    def findInIndex(self, word) -> LinkedList:
        tmpWord = self.lingModule.apply(word)
        if tmpWord in self.index:
            return self.index[tmpWord]
        else:
            return LinkedList()

    def indexWord(self, word: str, docId: int):
        if word in self.wordDocIdDict:
            if not (docId in self.wordDocIdDict[word]):
                self.wordDocIdDict[word].add(docId)
                self.index[word].addLast(docId)
        else:
            self.wordDocIdDict[word] = set()
            self.index[word] = LinkedList()
            self.wordDocIdDict[word].add(docId)
            self.index[word].addLast(docId)

    def indexIRDoc(self, doc: IRDoc):
        self.docs[doc.id] = doc
        for word in doc.wordSet:
            self.indexWord(word, doc.id)

    def maxKFreqTerms(self, k):
        sorted_by_value = sorted(self.wordDocIdDict.items(), key=lambda kv: (len(kv[1]), kv[0]), reverse=True)
        topK = sorted_by_value[:k]
        return topK

    def minKFreqTerms(self, k):
        sorted_by_value = sorted(self.wordDocIdDict.items(), key=lambda kv: (len(kv[1]), kv[0]))
        topK = sorted_by_value[:k]
        return topK

    def writeStats(self):
        open("Part_3.txt", "w").close()
        f = open("Part_3.txt", "a")
        f.write("highest term freqs:\n")
        for key, _ in self.maxKFreqTerms(10):
            f.write(key)
            f.write('\n')
        f.write("lowest term freqs:\n")
        for key, _ in self.minKFreqTerms(10):
            f.write(key)
            f.write('\n')
        f.close()


def __str__(self) -> str:
    for key, val in self.index.items():
        print(str(key) + ": " + str(val))
    return str(self.wordDocIdDict)


def testLinkedList():
    tmpList = LinkedList()
    tmpList.addLast(1)
    tmpList.addLast(2)
    tmpList.addLast(3)
    for it in tmpList:
        print(it.val)


def testInvertedIndex():
    invIdx = InvertIndex()
    invIdx.indexWord("ward", 1)
    invIdx.indexWord("ward", 1)
    invIdx.indexWord("ward", 2)
    invIdx.indexWord("ward", 3)
    invIdx.indexWord("ward", 4)
    invIdx.indexWord("warde", 2)
    invIdx.indexWord("warde", 1)
    invIdx.indexWord("wardeq", 1)
    print(invIdx)


def testIntersectTwoLinkedLists():
    l1 = LinkedList()
    l1.addLast(2)
    l1.addLast(4)
    l1.addLast(8)
    l1.addLast(16)
    l1.addLast(32)
    l1.addLast(64)
    l1.addLast(128)

    l2 = LinkedList()
    l2.addLast(1)
    l2.addLast(2)
    l2.addLast(3)
    l2.addLast(5)
    l2.addLast(8)
    l2.addLast(13)
    l2.addLast(21)
    l2.addLast(34)

    # print(l1.intersect(l2))


def testNotIntersect():
    l1 = LinkedList()
    l1.addLast(2)
    l1.addLast(4)
    l1.addLast(8)
    l1.addLast(16)
    l1.addLast(32)
    l1.addLast(64)
    l1.addLast(128)

    l2 = LinkedList()
    l2.addLast(1)
    l2.addLast(2)
    l2.addLast(3)
    l2.addLast(5)
    l2.addLast(8)
    l2.addLast(13)
    l2.addLast(21)
    l2.addLast(34)

    print(l1.notIntersect(l2))


def InvertedIndex() -> InvertIndex:
    invertedIdx: InvertIndex = InvertIndex()
    global docCount
    xml = None
    with open('test.trec', 'r') as f:  # Reading file
        xml = f.read()
    xml = '<ROOT>' + xml + '</ROOT>'
    root = ElementTree.fromstring(xml)

    for doc in root:
        irDoc = IRDoc(docCount, doc.find('DOCNO').text.strip(), doc.find('TEXT').text.strip().replace("\n", " "),
                      doc.find('FILEID').text.strip())
        docCount += 1
        invertedIdx.indexIRDoc(irDoc)
    # print(invertedIdx)
    invertedIdx.writeStats()
    return invertedIdx


testNotIntersect()
