#creating a simple blockchain as a way to really understand how the blockchain works

#chain of blocks. Each block holds transactions
class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []

    def new_block(self):
        #Creates a new block and adds it to the chain
        pass
    
    def add_new_transaction(self):
        #Adds a new transaction to the list of current_transactions
        pass
    
    @staticmethod #doesn't need an instance of this class to be executed. All objects share this
    def hash(block):
        #Hashes a block
        pass

    #makes the last block an attribute.
    #retrieves the last value always since we can't simply set it to a static number since the last value may change.
    @property
    def last_block(self):
        # Returns the last block in the chain
        pass
