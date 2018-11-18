import os
import xml.etree.ElementTree as ElementTree
from typing import Dict, Set
import json
import shelve

# import semidbm

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

    def fromSortedList(self, l):
        for a in l:
            if self.last is None or a != self.last.val:
                self.addLast(a)
        return self

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

    def Or(self, olinked):
        thisone = self.head
        otherone = olinked.head
        retval = LinkedList()
        while thisone and otherone:
            if otherone.val > thisone.val:
                retval.addLast(thisone.val)
                thisone = thisone.next
            elif thisone.val > otherone.val:
                retval.addLast(otherone.val)
                otherone = otherone.next
            else:
                retval.addLast(otherone.val)
                thisone = thisone.next
                otherone = otherone.next
        while thisone:
            retval.addLast(thisone.val)
            thisone = thisone.next

        while otherone:
            retval.addLast(otherone.val)
            otherone = otherone.next
        return retval

    def andNot(self, olinked):
        intersection = self.intersect(olinked)
        thisone = self.head
        otherone = intersection.head
        retval = LinkedList()
        while thisone and otherone:
            if otherone.val > thisone.val:
                retval.addLast(thisone.val)
                thisone = thisone.next
            elif thisone.val > otherone.val:
                retval.addLast(otherone.val)
                otherone = otherone.next
            else:
                thisone = thisone.next
                otherone = otherone.next
        while thisone:
            retval.addLast(thisone.val)
            thisone = thisone.next
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

    def toList(self):
        res = []
        for item in self:
            res.append(item.val)
        return res

    def toJsonArray(self):
        return json.dumps(self.toList())


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

    def __init__(self, id, docNo, text) -> None:
        self.id = id
        self.docNo = docNo
        self.text: str = text
        self.lingModule = LingModule()
        self.lingModule.addLingMapping(LingModule.toLowercase)
        self.wordSet: set = self._tokenize()

    def _tokenize(self):
        words = set(self.text.strip().replace("\n", " ").split(" "))
        words = set(self.lingModule.apply(words))
        return words

    def __str__(self) -> str:
        return "id:" + str(self.id) + "\n" + "docNo:" + str(self.docNo) + "\n" + "text:" + str(
            self.text) + "\n"


class InvertIndex:

    def __init__(self) -> None:
        self.indexPath = "invertedIndex.json"
        self.latestDocId = 1

        exists = os.path.exists('index.pkl')
        print("file exists " + str(exists))
        self.mode = 'r' if exists else 'c'
        self.index = shelve.open("index.pkl", self.mode, writeback=exists)
        self.docIdDocNo = shelve.open("docIddocNo.pkl", self.mode, writeback=exists)
        self.lingModule = LingModule()
        self.lingModule.addLingMapping(LingModule.toLowercaseStr)

    def findInIndex(self, word) -> LinkedList:
        tmpWord = self.lingModule.apply(word)
        if tmpWord in self.index:
            return LinkedList().fromSortedList(self.index[tmpWord])
        else:
            return LinkedList()

    def indexWord(self, word: str, doc: IRDoc):
        if len(word) == 0 or len(word.strip()) == 0 or not word:
            return

        if word in self.index:
            # if not (doc.id in self.index[word]):
            self.index[word].append(doc.id)
        else:
            self.index[word] = []
            self.index[word].append(doc.id)

    def indexIRDoc(self, doc: IRDoc):
        self.latestDocId = doc.id
        self.docIdDocNo[str(doc.id)] = doc.docNo
        for word in doc.wordSet:
            self.indexWord(word, doc)

    def maxKFreqTerms(self, k):
        sorted_by_value = sorted(self.index.items(), key=lambda kv: (len(kv[1]), kv[0]), reverse=True)
        topK = sorted_by_value[0:k]
        return topK

    def minKFreqTerms(self, k):
        sorted_by_value = sorted(self.index.items(), key=lambda kv: (len(kv[1]), kv[0]))
        topK = sorted_by_value[:k]
        return topK

    def writeStats(self):
        # open("Part_3.txt", "w").close()
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

    def sync(self):
        if self.mode != 'r':
            self.index.sync()
            self.index.close()
            self.index = shelve.open("index.pkl", 'c', writeback=True)
        else:
            self.index.close()


def __str__(self) -> str:
    for key, val in self.index.items():
        print(str(key) + ": " + str(val))
    return str(self.wordDocIdDict)


def loadFiles() -> list:
    directoryPath = "./AP_Coll_Parsed"
    directory = os.fsencode(directoryPath)
    res = []
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        res.append(directoryPath + "/" + filename)
    return res


def InvertedIndex() -> InvertIndex:
    invertedIdx: InvertIndex = InvertIndex()
    if len(invertedIdx.index) != 0:
        return invertedIdx
    xml = None
    files = loadFiles()
    cnt = 0
    for file in files:
        print(cnt)
        path = os.path.realpath(file)
        try:
            indexDocsInFile(path, invertedIdx)
        except ElementTree.ParseError as err:
            with open("errors.txt", 'a') as f:
                f.write(path + ", " + str(err) + "\n")
        cnt += 1
        if cnt % 100 == 0:
            invertedIdx.sync()
            print("syncDone")
    invertedIdx.sync()
    return invertedIdx


def indexDocsInFile(filePath, invertedIdx):
    # print("now working on " + filePath)
    with open(filePath, 'r') as f:  # Reading file
        xml = f.read()
    xml = '<ROOT>' + xml + '</ROOT>'
    docID = invertedIdx.latestDocId
    root = ElementTree.fromstring(xml)
    for doc in root:
        text = ""
        cases = doc.findall("TEXT")
        for c in cases:
            if not (c is None) and not (c.text is None):
                text += c.text.strip()
                text += " "
        irDoc = IRDoc(docID, doc.find('DOCNO').text.strip(), text)
        docID = docID + 1
        # print("docId now " + str(docID))
        invertedIdx.indexIRDoc(irDoc)
    invertedIdx.latestDocId = docID
    # print(invertedIdx)
    # invertedIdx.writeStats()


invIndex = InvertedIndex()
print("writing status....")
invIndex.writeStats()
# print(LinkedList().fromSortedList(invIndex.index["more"]))
