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
#The mining endpoint
@app.route('/mine', methods=['GET'])
def mine():
    #mining endpoint will do three things:
    #1.Calculate the proof of work
    #2.Reward the miner by adding a transaction that grants us 1 coin
    #3.Creates the new block and adds it to the chain


    #running the proof of work algorithm 
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    curr_proof = blockchain.compute_proof_of_work(last_proof)

    #receiving a reward for finding the proof
    #A sender of '0' means this node has mined a new coin

    blockchain.add_new_transaction(sender = "0", recipient = node_address, amount = 1)

    #now forging the new block with all the needed info
    prev_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof = curr_proof, prev_hash = prev_hash) #block here automatically added to the chain

    #response back to the user
    response = {
        'message': "New Block has been forged",
        "index": block['index'],
        "transactions": block['transactions'],
        "proof": block['proof'],
        "previous_hash" : block['prev_hash']
    }


    return jsonify(response), 200

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
    print(values)
    #Checking that the required fields are in the posted data
    required_fields = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required_fields): #for all k in required_fields is that k also in values
        #checking if all the k in required_fields are also in values
        return "Missing values", 400
    
    #Create a new transaction
    index = blockchain.add_new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transaction will be added to the block known by {index}'}
    return jsonify(response), 201

@app.route('/chain', methods = ['GET'])
def full_chain():
    #returns the full chain
    response = {
        'chain': blockchain.chain, 
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

#Taking care of the Decentralized and Consensus Algorithm portions

#To accept a list of new nodes (in the form of URLs)
@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please suply a valid list of nodes", 400
    
    for node in nodes:
        blockchain.register_node(node)
    
    #responding back to the poster so they know that their POST request was successful
    response = {
        'message': "New nodes have been registered",
        'total_nodes' : list(blockchain.node_set)
    }
    return jsonify(response), 201

#Implements our consensus algorithm, resolving any conflicts--ensuring a node has the correct chain
@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    is_replaced = blockchain.resolve_conflict()

    if is_replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain' : blockchain.chain
        }
        return jsonify(response), 200
    
    #else the current chain is the correct one
    response = {
        'message': 'Our chain is authoritative',
        'chain': blockchain.chain
    }
    return jsonify(response), 200



if __name__ == '__main__':
    #runs the server on port 5000
    app.run(host = '0.0.0.0', port = 5000)
