from abc import ABC, abstractmethod
from collections import OrderedDict
import mmh3
import queue

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

        prefetch_addresses = []
        predictiongap = 3
        #for (instr_id, cycle_count, load_addr, load_ip, llc_hit) in data:
        for i in range(0, len(data) - (predictiongap + 1)):
            #https://www.geeksforgeeks.org/unpacking-a-tuple-in-python/#
            instr_id, cycle_count, load_addr, load_ip, llc_hit = data[i]
            instr_id2, cycle_count2, load_addr2, load_ip2, llc_hit2 = data[i+predictiongap]
            instr_id3, cycle_count3, load_addr3, load_ip3, llc_hit3 = data[i+predictiongap+1]

            predicted_address = load_addr2 
            prefetch_addresses.append((instr_id, predicted_address))
            predicted_address = load_addr3 
            prefetch_addresses.append((instr_id, predicted_address))

        return prefetch_addresses
        #return []

# Replace this if you create your own model
Model = OMHModel
