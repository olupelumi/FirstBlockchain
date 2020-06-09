#Allows us to talk to our blockchain over the web using HTTP requests
#This server will represent a single node in our blockchian network
from textwrap import dedent
import json
from uuid import uuid4
from flask import Flask, jsonify, request
from Blockchain import Blockchain

# Instantiate our Node 
app = Flask(__name__)

#Generate a globally unique address for this node
node_address = str(uuid4()).replace('-', '') #a 128 bit string
#example = 2e8421c1fca743ec985b0fb6ad117a06

#Instantiate the blockchain
blockchain = Blockchain()

#creating endpoints
@app.route('/mine', methods=['GET'])
def mine():
    return "Gonna mine a new block"

#where new transactions will be posted
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    # The transaction request will look like(transaction info sent to the serve):
#     {
#  "sender": "my address",
#  "recipient": "someone else's address",
#  "amount": 5
#     }
    values = request.get_json()
    #Checking that the required fields are in the posted data
    required_fields = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required_fields): #for all k in required_fields is that k also in values
        #checking if all the k in required_fields are also in values
        return "Missing values"
    
    #Create a new transaction
    index = blockchain.add_new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transaction will be added to the block known by{index}'}
    return jsonify(response), 201

@app.route('/chain', methods = ['GET'])
def full_chain():
    #returns the full chain
    response = {
        'chain': blockchain.chain, 
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

if __name__ == '__main__':
    #runs the server on port 5000
    app.run(host = '0.0.0.0', port = 5000)
