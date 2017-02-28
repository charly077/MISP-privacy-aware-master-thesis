"""
Cryptographic system for bloom filter
"""
from crypto.interface import Crypto
import configparser
import glob, hashlib, os
from base64 import b64encode

# hash and crypto import
from crypto.pybloom import BloomFilter

class Bloom_filter(Crypto):
    def __init__(self, conf, metadata=None):
        self.conf = conf
        self.token = conf['misp']['token']
        self.passwords = list()
        # if for matching
        if metadata != None:
            filename = self.conf['rules']['location'] + '/joker'
            with open(filename, 'rb') as fd:
                self.f = BloomFilter.fromfile(fd)

    def create_rule(self, ioc, message):
        """
        We need to create one rule, thus we need a state
        """
        if (len(ioc)>1):
            # We also add the concatenation of the two values
            long_pass = '||'.join([attributes[attr] for attr in attributes])
            self.passwords.append(long_pass + self.token)
        
        for attr in attributes:
            self.passwords.append(attributes[attr]+ self.token)

        return {'joker':True}


    def match(self, attributes, rule, queue):
        """
        Sometimes we don't need to decrypt the whole
        ciphertext to know if there is a match
        as it is the case here thanks to ctr mode
        """
        print("check if it is a dict")
        print(attributes)

        passwords = list()

        if (len(attributes)>1):
            # We also add the concatenation of the two values
            long_pass = '||'.join([attributes[attr] for attr in attributes])
            passwords.append(long_pass + self.token)
        
        for attr in attributes:
            passwords.append(attributes[attr]+ self.token)
        
        for p in passwords:
            if p in self.f:
                queue.put("IOC {} matched for {}\n".format(attributes, p))



    def save_meta(self):
        meta = configparser.ConfigParser()
        meta['crypto'] = {}
        meta['crypto']['name'] = 'bloom_filter' 
        err_rate = self.conf['bloom_filter']['error_rate']
        meta['crypto']['error_rate'] = err_rate
        with open(self.conf['rules']['location'] + '/metadata', 'w') as config:
            meta.write(config)

        # create Bloom filter
        f = BloomFilter(capacity=len(self.passwords), error_rate=err_rate)
        [f.add(password) for password in passwords ]
        with open(self.conf['rules']['location'] + '/joker', 'wb') as fd:
            f.tofile(fd)
