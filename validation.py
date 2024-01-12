from Crypto.PublicKey import DSA
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
import json, hashlib, binascii

def calculate_hash(block):
    return hashlib.sha256(json.dumps(block).encode()).hexdigest()

def verify_signature(public_key, signature, data):
    verifying = DSS.new(public_key, 'fips-186-3')
    h = SHA256.new(data.encode())
    try:
        verifying.verify(h, binascii.unhexlify(signature))
        return True
    except ValueError:
        return False

def verify_block(blockchain):
    for i in range(1, len(blockchain)):
        previous_block = blockchain[i-1]
        current_block = blockchain[i]

        if calculate_hash(previous_block) != current_block["Hash"]:
            return False

        input_sig = current_block["Input"]["ScriptSig"]
        previous_public_key = current_block["Output"][0]["ScriptPubKey"].strip('[]')
        previous_public_key = DSA.import_key(open("Alice_public_key.pem", "rb").read())
        if not verify_signature(previous_public_key, input_sig, calculate_hash(previous_block)):
            return False

    return True

blockchain = []
for i in range(10):
    filename = f"block{i+1}.txt"
    with open(filename, "r") as file:
        block = json.load(file)
        blockchain.append(block)

if verify_block(blockchain):
    print("Block is valid!")
else:
    print("Block is invalid!")
