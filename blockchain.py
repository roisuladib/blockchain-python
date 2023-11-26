import hashlib
import json

from time import time
from uuid import uuid4

from flask import Flask
from flask.globals import request
from flask.json import jsonify


class Blockchain(object):
   difficulty_target = "0000"

   def hash_block(self, block):
      block_encoded = json.dumps(block, sort_keys=True).encode()
      return hashlib.sha256(block_encoded).hexdigest()

   def __init__(self):
      self.chains = []
      self.current_transactions = []
      genesis_hash = self.hash_block("genesis_block")

      self.append_block(
         hash_of_previous_block = genesis_hash,
         nonce = self.proof_of_work(0, genesis_hash, [])
      )

   def proof_of_work(self, index, hash_of_previous_block, transactions):
      nonce = 0
      while self.valid_proof(index, hash_of_previous_block, transactions, nonce) is False:
         nonce += 1
      return nonce

   def valid_proof(self, index, hash_of_previous_block, transactions, nonce):
      content = f'{index}{hash_of_previous_block}{transactions}{nonce}'.encode()
      content_hash = hashlib.sha256(content).hexdigest()

      return content_hash[:len(self.difficulty_target)] == self.difficulty_target

   def append_block(self, hash_of_previous_block, nonce):
      block = {
         'index': len(self.chains),
         'timestamp': time(),
         'transaction': self.current_transactions,
         'nonce': nonce,
         'hash_of_previous_block': hash_of_previous_block
      }

      self.current_transactions = []
      self.chains.append(block)

      return block

   def add_transaction(self, sender, recipient, amount):
      self.current_transactions.append({
         'amount': amount,
         'recipient': recipient,
         'sender': sender
      })
      return self.last_block['index'] + 1

   @property
   def last_block(self):
      return self.chains[-1]

app = Flask(__name__)
node_identifier = str(uuid4()).replace('-', "")

blockchain = Blockchain()

#routes
@app.route("/")
def main():
    return "<p>Hello, World!</p>"

@app.route('/blockchains')
def blockchains():
   response = {
      'chains': blockchain.chains,
      'length': len(blockchain.chains)
   }

   return jsonify(response), 200

@app.route('/mine')
def mine():
   blockchain.add_transaction(
      sender="0",
      recipient=node_identifier,
      amount=1
   )
   index = len(blockchain.chains)
   last_block_hash = blockchain.hash_block(blockchain.last_block)
   nonce = blockchain.proof_of_work(index, last_block_hash, blockchain.current_transactions)
   block = blockchain.append_block(nonce, last_block_hash)

   response = {
      'message': 'Added new mine',
      'index': block['index'],
      'hash_of_previous_block': block['hash_of_previous_block'],
      'nonce': block['block'],
      'transaction': block['transaction']
   }

   return jsonify(response), 200

# @app.route('transactions', methods=['POST'])
# def transactions():
#    values = request.get_json()
#    required_fields = ['sender', 'recipient', 'amount']
#    if not all(k in values for k in required_fields):
#       return 'Missing fields', 400

#    index = blockchain.add_transaction(
#       values['sender'],
#       values['recipient'],
#       values['amount']
#    )

#    response = {
#       'message': f'Added new transaction {index}'
#    }
#    return jsonify(response), 201
