#creating a simple blockchain as a way to really understand how the blockchain works
import hashlib
import json
from time import time
from urllib.parse import urlparse
import requests
#chain of blocks. Each block holds transactions
#The Blockchain class is also responsible for adding new blocks to the chain.
class Blockchain:
    def __init__(self):
        #the chain of blocks
        self.chain = []
        #list of transacrtions in one block
        self.current_transactions = []
        
        #Create the genesis block 
        self.new_block(proof = 100, prev_hash = 1)

        #The other nodes
        self.node_set = set()

    #registering the other nodes
    def register_node(self, address):
        """
        Requires:
        address: <str> Address of a node. E.g 'http://192.168.0.5:5000'

        Effects:
        Adds a new node to the set of nodes
        Returns nothing
        """
        #parsing the address with a general URL structure: scheme://netloc/path;parameters?query#fragment
        #Example: urlparse('http://www.cwi.nl:80/%7Eguido/Python.html') -> ParseResult(scheme='http', netloc='www.cwi.nl:80', path='/%7Eguido/Python.html', params='', query='', fragment='')
        parsed_url = urlparse(address)

        #getting the location of the node on the web and adding it to the node set
        self.node_set.add(parsed_url.netloc)

        

    #makes the last block an attribute.
    #retrieves the last value always since we can't simply set it to a static number since the last value may change.
    @property
    def last_block(self):
        # Returns the last block in the chain
        return self.chain[-1]

    def new_block(self, proof, prev_hash = None):
        #Creates a new block and adds it to the chain
        """
        Requires:
        proof:<int> proof of work of the block
        prev_hash: <str> Hash of the previous block

        Effects:
        Creates a new block and adds it to the chain
        Returns the <dict> new block
        """
        block = {
            'index': len(self.chain) + 1, #this new block will incrase length by 1
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'prev_hash': prev_hash or self.hash(self.chain[-1]) #if prev_hash is None then assigned to the return of self.hash
        }

        #resets the current list of transactions. 
        self.current_transactions = [] #an empty list that will be populated with transactions for another block
        
        #adding the block to the chain
        self.chain.append(block)
        return block
    
    def add_new_transaction(self, sender, recipient, amount):
        #Adds a new transaction to the list of current_transactions in a block
        """
        Requires:
        sender is a string address of the Sender node
        recipient is a string address of the recipient node
        amount: <int> Amount that was transacted

        Effects:
        Adds the new transaction to a list of transactions
        Returns the index of the block that holds this transaction.
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })
        #seems like there is one transaction per block (may come to a different conclusion later)
        return self.last_block['index'] + 1
    
    @staticmethod #doesn't need an instance of this class to be executed. All objects share this
    def hash(block):
        #Hashes a block
        """
        Requires:
        block: <dict> a block with some transactions
        
        Effects:
        returns the <str> SHA-256 hash of the block
        """
        #the dictionary representing the block must be ordered/immutable to avoid inconsistent Hashes

        #changes the dictionary to a json with a certain key order and then converts the json to a string
        block_string = json.dumps(block, sort_keys=True).encode() 
        
        #doing the hashing
        return hashlib.sha256(block_string).hexdigest() #hexdigest makes it a secure hash
        
    #proof of work is finding a number that solves a problem 
    #computing the number must be difficult to compute but easy to verify
    def compute_proof_of_work(self, prev_proof):
        """
        Requires:
        last_proof: <int> The proof of work of the previous block

        Effects:
        Finds a number m' such that the hash(mm') contains four leading zeros.
        m is the previous proof of work and m' will be the new proof of work

        Returns <int> m' 
        """

        proof = 0 # first guess 
        while self.valid_proof(prev_proof = prev_proof, candidate_proof = proof) is not True:
            proof += 1
        return proof

    def valid_proof(self, prev_proof, candidate_proof):
        """"
        Requires:
        prev_proof: <int> The proof of the previous block
        candidate_proof: <int> the proof that we want to verify

        Effects:
        validates whether the hash(prev_proof, candidate_proof) contains four leading zeros
        Returns True or False
        """
        guess = f'{prev_proof}{candidate_proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000" #checking that the first four items are zeros

    # Consensus - resolves conflicts between two nodes

    #verifying validity of the chain 
    def is_chain_valid(self, chain):
        """"
        Requires:
        chain: <list> A blockchain
        Effects:
        Returns <bool> True if valid, False if not
        """ 

        prev_block = chain[0]
        curr_idx = 1
        
        #iterating through the blocks
        while curr_idx < len(chain):
            curr_block = chain[curr_idx]
            print (f'{prev_block}')
            print (f'{curr_block}')
            print('\n----------\n')

            #check that the prev_hash stored in the current block is correct
            #Don't need to check the first block since it is the genesis block that is certain to be valid

            if curr_block['prev_hash'] != self.hash(prev_block):
                return False
            
            #checking that the proof of work is correct
            if not self.valid_proof(prev_block['proof'], curr_block['proof']):
                return False
            
            prev_block = curr_block
            curr_idx += 1 

        return True

    def resolve_conflict(self):
        """"
        Requires:
        None
        Effects:
        This is our consensus algorithm that resolves conflicts
        Returns <bool> True if our chain was replaced, False if not
        """

        neighbors = self.node_set
        new_chain = None

        #We're looking for chains longer than our own 
        max_len = len(self.chain)

        #Check all the nodes in our network to see if they have a longer chain
        for node in neighbors:
            #requesting the chain data for this node
            response = requests.get(f'http://{node}/chain')

            #verifying the validity of the response
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                #checking if the neighbor's chain is valid and that its chain length is longer than the current largest length
                if length > max_len and self.is_chain_valid(chain):
                    max_len = length
                    new_chain = chain

        #if the new chain is not None then it means the chain for this node is to be changed
        if new_chain: #if not none
            self.chain = new_chain
            return True
        
        return False