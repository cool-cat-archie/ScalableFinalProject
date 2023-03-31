from abc import ABC, abstractmethod
from collections import OrderedDict
import mmh3
class testclass:
    def __init__(self):
        #force this to be a fixed size by removing the zero index each time we exceed the pattern length
        self.accesspattern = list()
        #use this to be able to update next accesses in the hashtable
        self.lasthash = 0
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

        # vvvvvv CODE THAT WAS WRITTEN WITH LIN vvvvvv 
        prefetch_addresses = []
        pagehash = dict()
        patterntable = dict()
        patternsize = 6
        predictions = 0
        for (instr_id, cycle_count, load_addr, load_ip, llc_hit) in data:
            pc, page, offset = load_ip, load_addr >> 12, ((load_addr >> 6) & 0x3f)
            #setting predicted_delta to 1 would make it a next line prefetcher
            #when there isn't anything to predict
            predicted_delta = 1
            pagestring = str(page)
            if pagehash.get(pagestring) == None:
                pagehash[pagestring] = testclass() 
                pagedata = pagehash[pagestring]
                (pagedata.accesspattern).append(offset)
            else:
                pagedata = pagehash[pagestring]

                #update existing hash if there is one
                if len(pagedata.accesspattern) == patternsize: 
                    #compute the value that should be stored in the patterntable
                    valuedelta = offset - pagedata.accesspattern[-1] 
                    #update the pattern table for the last hash
                    patterntable[pagedata.lasthash] = valuedelta 

                pagedata.accesspattern.append(offset)
                if len(pagedata.accesspattern) > patternsize:
                    pagedata.accesspattern.pop(0)


                #compute deltas, then compute hash then put hash in pagedata
                #and insert hash into patternhashtable
                if len(pagedata.accesspattern) == patternsize: 
                    accesspattern = pagedata.accesspattern        
                    deltapattern = list()
                    for i in range(1, len(pagedata.accesspattern)):
                        deltapattern.append(str(i-1) + str(accesspattern[i] - accesspattern[i-1]))
                    hashes = kmin_kmin(1, 1, deltapattern) 
                    hashstring = ""
                    for key in hashes:
                        hashstring += str(key)
                    #store new hash in page data
                    pagedata.lasthash = hashstring

                    #now make prediction based on what is in the hashtable
                    if patterntable.get(hashstring) != None:
                        predicted_delta = patterntable.get(hashstring)
                        predicted_address = (int(page) << 12) + (int(offset + predicted_delta) << 6)
                        prefetch_addresses.append((instr_id, predicted_address))
                        predictions += 1 
                    else:
                        #print("no prediction to make")
                        xyz = 1
                else:
                    #print("no pattern to predict")
                    xyz = 1
        print("testing number of predictions made " + str(predictions)) 
        return prefetch_addresses
    # ^^^^^^ END OF CODE THAT WAS WRITTEN WITH LIN ^^^^^^ 

# Replace this if you create your own model
Model = OMHModel
