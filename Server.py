#Allows us to talk to our blockchain over the web using HTTP requests
#This server will represent a single node in our blockchian network
from textwrap import dedent
from uuid import uuid4
from flask import Flask

# Instantiate our Node 
app = Flask(__name__)