from uuid import uuid1
from flask import Flask, jsonify, request, render_template

from Blockchain import Blockchain

app = Flask(__name__)


blockchain = Blockchain()

@app.route('/mine',methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # Generate a globally unique address for this node
    node_identifier = str(uuid1()).replace('-', '')

    # 给工作量证明的节点提供奖励
    # 发送者为”0“表明是新挖出的币
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    # Forge the new Block by adding it to the chain
    block = blockchain.new_block(proof)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/transaction',methods=['GET'])
def transactions():
    return render_template('new_transaction.html')

@app.route('/transactions/new',methods=['POST'])
def new_transaction():
    sender = request.form['sender']
    recipient = request.form['recipient']
    amount = request.form['amount']
    # Check that the required fields are in the POST'ed data
    if not (sender and recipient and amount):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(sender,recipient,amount)
    response = {'message': 'Transaction will be added to Block {}'.format(index)}
    return jsonify(response), 201

@app.route('/chain',methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response),200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_nod(node)

    response = {
        'message': 'New ndes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_confilcts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain,
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain,
        }
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='192.168.2.204',port=5001)