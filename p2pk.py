from Crypto.PublicKey import DSA
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
import json, hashlib, binascii

def generate_keypair():
    key = DSA.generate(1024)
    pub_key = key.publickey()
    return key, pub_key

Alice_private_key, Alice_pub_key = generate_keypair()
Bob_private_key, Bob_pub_key = generate_keypair()

with open("Alice_private_key.pem", "wb") as private_key_file:
    private_key_file.write(Alice_private_key.export_key('PEM'))
with open("Alice_public_key.pem", "wb") as public_key_file:
    public_key_file.write(Alice_pub_key.export_key('PEM'))

with open("Bob_private_key.pem", "wb") as private_key_file:
    private_key_file.write(Bob_private_key.export_key('PEM'))
with open("Bob_public_key.pem", "wb") as public_key_file:
    public_key_file.write(Bob_pub_key.export_key('PEM'))

genesis_block = {
        "TxID": 0,
        "Hash": "This is the genesis block.",
        "Nonce": 0,
        "Output": {
            "Value": 10,
            "ScriptPubKey": f"[{Alice_pub_key.export_key()}] OP_CHECKSIG"
            }
        }
blockchain = [genesis_block]

def calculate_hash(block):
    return hashlib.sha256(json.dumps(block).encode()).hexdigest()

def digital_signature(private_key, data):
    signature = DSS.new(private_key, 'fips-186-3')
    h = SHA256.new(data.encode())
    return signature.sign(h)

def mine_block(previous_block, sender_private_key, recipient_public_key, remains):
    txid = previous_block["TxID"] + 1
    nonce = 0
    
    while True:
        block = {
            "TxID": txid,
            "Hash": calculate_hash(previous_block),
            "Nonce": nonce,
            "Input": {
                "Previous Tx": calculate_hash(previous_block),
                "Index": 0,
                "ScriptSig": binascii.hexlify(digital_signature(Alice_private_key, calculate_hash(previous_block))).decode()
                },
            "Output": [{
                "Value": remains,
                "ScriptPubKey": f"[{Bob_pub_key.export_key()}] OP_CHECKSIG"
                },{
                "Value": 10 - remains,
                "ScriptPubKey": f"[{Alice_pub_key.export_key()}] OP_CHECKSIG"
                }]
            }
        if int(calculate_hash(block), 16) < 2 ** 248:
            blockchain.append(block)
            return block
        nonce += 1

with open(f"block0.txt", "w") as file:
    file.write(json.dumps(genesis_block, indent = 2))

for i in range(10):
    sender_block = blockchain[-1]
    new_block = mine_block(sender_block, Alice_private_key, Bob_pub_key, i+1)
    
    with open(f"block{i+1}.txt", "w") as file:
        file.write(json.dumps(new_block, indent = 2))

print("Block generation is done")
