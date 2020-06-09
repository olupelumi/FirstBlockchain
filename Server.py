#Allows us to talk to our blockchain over the web using HTTP requests
#This server will represent a single node in our blockchian network
from textwrap import dedent
import json
from uuid import uuid4
from flask import Flask, jsonify
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

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    return "gonna add a new transaction"

@app.route('/chain', methods = ['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain, 
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200