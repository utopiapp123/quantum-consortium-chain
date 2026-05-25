"""
区块结构 | Block
量子安全的区块结构，支持 QKD 密钥签名验证
"""
import json
import hashlib
import time
from dataclasses import dataclass, field
from typing import List, Optional
from cryptography.fernet import Fernet
import base64

@dataclass
class Transaction:
    """交易结构"""
    sender: str
    receiver: str
    amount: float
    timestamp: float = field(default_factory=time.time)
    signature: Optional[str] = None
    data: Optional[dict] = None  # 附加数据（如 QKD 公钥）
    
    def to_dict(self) -> dict:
        return {
            'sender': self.sender,
            'receiver': self.receiver,
            'amount': self.amount,
            'timestamp': self.timestamp,
            'data': self.data
        }
    
    def hash(self) -> str:
        tx_str = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(tx_str.encode()).hexdigest()

@dataclass
class Block:
    """区块"""
    index: int
    transactions: List[Transaction]
    previous_hash: str
    timestamp: float = field(default_factory=time.time)
    validator: str = ""  # 验证者节点ID
    qkd_signature: Optional[str] = None  # QKD 密钥签名
    nonce: int = 0
    hash: str = ""
    
    def compute_hash(self) -> str:
        """计算区块哈希"""
        block_data = {
            'index': self.index,
            'transactions': [t.to_dict() for t in self.transactions],
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'validator': self.validator,
            'nonce': self.nonce
        }
        block_str = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_str.encode()).hexdigest()
    
    def to_dict(self) -> dict:
        return {
            'index': self.index,
            'transactions': [t.to_dict() for t in self.transactions],
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'validator': self.validator,
            'nonce': self.nonce,
            'hash': self.hash,
            'qkd_signature': self.qkd_signature
        }
    
    def encrypt_with_qkd(self, key: bytes):
        """使用 QKD 密钥加密区块中的敏感数据"""
        fernet = Fernet(base64.urlsafe_b64encode(key[:32].ljust(32, b'\x00')))
        for tx in self.transactions:
            if tx.data:
                tx.data = {'encrypted': fernet.encrypt(
                    json.dumps(tx.data).encode()
                ).decode()}
    
    def sign_with_qkd(self, key: bytes):
        """使用 QKD 密钥签名"""
        h = self.compute_hash()
        self.qkd_signature = hashlib.hmac.new(key, h.encode(), hashlib.sha256).hexdigest()
        self.hash = h

class GenesisBlock:
    """创世区块工厂"""
    @staticmethod
    def create() -> Block:
        genesis_tx = Transaction(
            sender="0",
            receiver="Genesis",
            amount=0,
            data={"message": "Quantum Consortium Chain Genesis"}
        )
        block = Block(
            index=0,
            transactions=[genesis_tx],
            previous_hash="0" * 64,
            validator="Genesis",
        )
        block.hash = block.compute_hash()
        return block
