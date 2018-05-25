import hashlib
import json
from time import time
from urllib.parse import urlparse
import requests

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash=1,proof=100)

        self.nodes = set()

    def new_block(self,proof,previous_hash=None):
        # Creates a new Block and adds it to the chain
        # 生成新块
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self,sender,recipient,amount):
        # Adds a new transaction to the list of transactions
        # 生成新交易信息，信息将加入到下一个待挖的区块中

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    def proof_of_work(self,last_proof):
        """ 简单的工作量证明，查找一个p 使得hash(pp） 以4个0开头"""

        proof = 0
        while self.valid_proof(last_proof,proof) is False:
            proof += 1

        return proof

    def register_nod(self,address):
        """ 注册一个新的节点到列表 """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        """ 确定给定的链是否有效 """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(last_block)
            print(block)
            print("\n--------------\n")
            if block['previous_hash'] != self.hash(last_block):
                return False
            if not self.valid_proof(last_block['proof'],block['proof']):
                return False

            last_block = block
            current_index += 1
        return True

    def resolve_confilcts(self):
        """ 共识算法解决冲突
        使用网络中最长的链."""

        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)

        for node in neighbours:
            response = requests.get('http://{}/chain'.format(node))

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False

    @staticmethod
    def valid_proof(last_proof,proof):
        """
        验证证明：是否hash(last_proof,proof)以4个0开头？
        :param last_proof: <int> Previous Proof
        :param proof:  <int> Current Proof
        :return: <bool> True if correct, False if not.
        """

        guess = (str(last_proof)+str(proof)).encode()
        # guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    @staticmethod
    def hash(block):
        # Hashes a Block
        # 生成块的 SHA-256 hash值
        block_string = json.dumps(block,sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        # Returns the last Block in the chain
        return self.chain[-1]

# 块结构
"""
block = {
    'index': 1,
    'timestamp': 1506057125.450002,
    'transactions': [
        {
            'sender': '8527147fe1f5426f9dd545de4b27ee00',
            'recipient': 'a77f5cdfa2934df3954a5c7c7da5df1f',
            'amount': 5,
        }
    ],
    'proof': 324984774000,
    'previous_hash': '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824',
}
"""