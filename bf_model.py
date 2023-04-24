from abc import ABC, abstractmethod
from collections import OrderedDict
from pybloomfilter import BloomFilter
import mmh3
import queue
class testclass:
    def __init__(self):
        #force this to be a fixed size by removing the zero index each time we exceed the pattern length
        self.accesspattern = list()
        self.patternQueue = queue.Queue()
        #use this to be able to update next accesses in the hashtable
        #self.lasthash = 0
def kmin_kmin(j, k, items):

    hashlist = list()
    for i in range(0,k):
        templist = list()
        for x in range(0, len(items)):
            templist.append(mmh3.hash(items[x], i))

        templist.sort()
        hashlist.append(templist[0]) 

    hashlist.sort() 
    returnlist = list()
    for i in range(0,j):
        returnlist.append(hashlist[i])
    return returnlist


class OMHModel(object):
    '''
    Abstract base class for your models. For HW-based approaches such as the
    NextLineModel below, you can directly add your prediction code. For ML
    models, you may want to use it as a wrapper, but alternative approaches
    are fine so long as the behavior described below is respected.
    '''

    @abstractmethod
    def load(self, path):
        '''
        Loads your model from the filepath path
        '''
        pass

    @abstractmethod
    def save(self, path):
        '''
        Saves your model to the filepath path
        '''
        pass

    @abstractmethod
    def train(self, data):
        '''
        Train your model here. No return value. The data parameter is in the
        same format as the load traces. Namely,
        Unique Instr Id, Cycle Count, Load Address, Instruction Pointer of the Load, LLC hit/miss
        '''
        pass

    @abstractmethod
    def generate(self, data):
        print(len(data))
        '''
        Generate your prefetches here. Remember to limit yourself to 2 prefetches
        for each instruction ID and to not look into the future :).

        The return format for this will be a list of tuples containing the
        unique instruction ID and the prefetch. For example,
        [
            (A, A1),
            (A, A2),
            (C, C1),
            ...
        ]

        where A, B, and C are the unique instruction IDs and A1, A2 and C1 are
        the prefetch addresses.
        '''

        #pattern size 10, k = 1, gap 0, removed index on delta string

        addresses = dict()
        PCs = dict()

        prefetch_addresses = []
        pagehash = dict()
        patterntable = dict()
        patternsize = 10
        predictions = 0
        samedelta = 0
        notsamedelta = 0
        newdelta = 0
        totalaccesses = 0
        previousprediction = -1
        correctnextaccess = 0
        predictiongap = 10
        kminhashcount = 4
        predictbarrier= 5
        bf = BloomFilter(100000, 0.01, 'filter.bloom')
        for (instr_id, cycle_count, load_addr, load_ip, llc_hit) in data:
            PCs[load_ip] = 1
            addresses[load_addr] = 1
            totalaccesses += 1
            pc, page, offset = load_ip, load_addr >> 12, ((load_addr >> 6) & 0x3f)

            if previousprediction != -1 and previousprediction == load_addr:
                correctnextaccess += 1


            #setting predicted_delta to 1 would make it a next line prefetcher
            #when there isn't anything to predict
            predicted_delta = 1
            #pagestring = str(page) + str(pc)
            pagestring = str(page)

            if pagehash.get(pagestring) == None:
                pagehash[pagestring] = testclass() 
                pagedata = pagehash[pagestring]
                (pagedata.accesspattern).append(offset)
                for i in range(0, predictiongap):
                    (pagedata.patternQueue).put("placeholder")

            else:
                pagedata = pagehash[pagestring]

                #update existing hash if there is one
                if len(pagedata.accesspattern) == patternsize: 
                    #compute the value that should be stored in the patterntable
                    valuedelta = offset - pagedata.accesspattern[-1] 
                    lasthash = (pagedata.patternQueue).get()
                    if lasthash != "placeholder":
                        #update the pattern table for the last hash
                        if patterntable.get(lasthash) != None:
                            previousdelta = (patterntable[lasthash])[0]
                            previouscount = (patterntable[lasthash])[1]

                            #sketching to try and keep the item that appears > 50% of the time
                            if previousdelta == valuedelta:
                                patterntable[lasthash] = (previousdelta, previouscount + 1)
                                samedelta+=1
                            else:
                                if previouscount == 0:
                                    patterntable[lasthash] = (valuedelta, 1)
                                    notsamedelta+=1
                                else:
                                 patterntable[lasthash] = (previousdelta, previouscount - 1)
                                 notsamedelta+=1
                        else:
                            if bf.add(lasthash):
                                patterntable[lasthash] = (valuedelta, 1)
                                newdelta+=1
                             

                pagedata.accesspattern.append(offset)
                if len(pagedata.accesspattern) > patternsize:
                    pagedata.accesspattern.pop(0)


                #compute deltas, then compute hash then put hash in pagedata
                #and insert hash into patternhashtable
                if len(pagedata.accesspattern) == patternsize: 
                    accesspattern = pagedata.accesspattern        
                    deltapattern = list()
                    for i in range(1, len(pagedata.accesspattern)):
                        deltapattern.append(str(accesspattern[i] - accesspattern[i-1]))
                        #deltapattern.append(str(i-1) + str(accesspattern[i] - accesspattern[i-1]))
                    hashes = kmin_kmin(kminhashcount, kminhashcount, deltapattern) 
                    hashstring = ""
                    for key in hashes:
                        hashstring += str(key)

                    
                    #store new hash in page data
                    (pagedata.patternQueue).put(hashstring)

                    #now make prediction based on what is in the hashtable
                    if patterntable.get(hashstring) != None:
                        predicted_delta = patterntable.get(hashstring)[0]
                        predicted_count = patterntable.get(hashstring)[1]
                        if predicted_count > predictbarrier:
                            predicted_address = (int(page) << 12) + (int(offset + predicted_delta) << 6)
                            #predicted_address = load_addr + predicted_delta
                            prefetch_addresses.append((instr_id, predicted_address))
                            predictions += 1 
                            previousprediction = predicted_address
                    else:
                        #print("no prediction to make")
                        previousprediction = -1
                else:
                    #print("no pattern to predict")
                    previousprediction = -1

        print("total accesses" + str(totalaccesses)) 
        print("testing number of predictions made " + str(predictions)) 
        print("same delta" + str(samedelta)) 
        print("not same delta" + str(notsamedelta)) 
        print("new delta" + str(newdelta)) 
        print("correct next access " + str(correctnextaccess))
        print("page hash size " + str(len(pagehash)))
        print("pattern table size" + str(len(patterntable)))

        print("total addresses " + str(len(addresses)))
        print("total PCs " + str(len(PCs)))
        print("total bits used by bloom filter " + str(bf.num_bits))

        return prefetch_addresses

# Replace this if you create your own model
Model = OMHModel
