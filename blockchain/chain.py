"""
联盟链核心 | Consortium Blockchain Core
基于 PBFT 的联盟链实现，集成 QKD 密钥
"""
import json
import time
import threading
from typing import List, Dict, Optional, Set
from blockchain.block import Block, Transaction, GenesisBlock
from blockchain.consensus import PBFTConsensus

class ConsortiumChain:
    """量子安全联盟链"""
    
    def __init__(self, node_id: str, nodes: List[str], f: int = 1):
        self.node_id = node_id
        self.nodes = nodes  # 所有联盟节点
        self.f = f  # 容错节点数
        self.chain: List[Block] = []
        self.pending_txs: List[Transaction] = []
        self.consensus = PBFTConsensus(node_id, nodes, f)
        self.qkd_key: Optional[bytes] = None  # BB84 分发的密钥
        self.block_time = 2  # 出块间隔(秒)
        self.running = False
        self._lock = threading.Lock()
        
        # 创建创世区块
        genesis = GenesisBlock.create()
        self.chain.append(genesis)
    
    def set_qkd_key(self, key: bytes):
        """注入 BB84 分发的量子密钥"""
        self.qkd_key = key
        print(f"[{self.node_id}] ✅ QKD 密钥已注入 ({len(key)*8} bits)")
    
    @property
    def last_block(self) -> Block:
        return self.chain[-1]
    
    @property
    def height(self) -> int:
        return len(self.chain)
    
    def add_transaction(self, tx: Transaction) -> bool:
        """添加交易到待处理池"""
        with self._lock:
            # QKD 签名验证
            if self.qkd_key:
                tx_hash = tx.hash()
                tx.signature = hashlib.sha256(
                    (tx_hash + self.qkd_key.hex()).encode()
                ).hexdigest()
            
            self.pending_txs.append(tx)
            print(f"[{self.node_id}] 📝 交易入池: {tx.sender} → {tx.receiver} ({tx.amount})")
            return True
    
    def create_block(self) -> Optional[Block]:
        """创建新区块"""
        with self._lock:
            if len(self.pending_txs) < 1:
                return None
            
            txs = self.pending_txs[:10]  # 最多10笔交易
            self.pending_txs = self.pending_txs[10:]
        
        block = Block(
            index=self.height,
            transactions=txs,
            previous_hash=self.last_block.hash,
            validator=self.node_id,
        )
        
        # QKD 签名
        if self.qkd_key:
            block.sign_with_qkd(self.qkd_key)
        else:
            block.hash = block.compute_hash()
        
        return block
    
    def propose_block(self, block: Block) -> bool:
        """PBFT 共识提议"""
        print(f"\n[{self.node_id}] 📢 提议区块 #{block.index}")
        
        # 模拟共识过程
        result = self.consensus.reach_consensus(block)
        
        if result:
            return self.commit_block(block)
        return False
    
    def commit_block(self, block: Block) -> bool:
        """提交区块到链"""
        with self._lock:
            if block.previous_hash != self.last_block.hash:
                return False
            
            self.chain.append(block)
            print(f"[{self.node_id}] ✅ 区块 #{block.index} 已提交")
            print(f"    哈希: {block.hash[:16]}...")
            print(f"    交易数: {len(block.transactions)}")
            if block.qkd_signature:
                print(f"    QKD签名: {block.qkd_signature[:16]}...")
            return True
    
    def validate_chain(self) -> bool:
        """验证整条链的完整性"""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            
            if current.previous_hash != previous.hash:
                print(f"❌ 区块 #{i} 前哈希不匹配")
                return False
            
            if current.hash != current.compute_hash():
                print(f"❌ 区块 #{i} 哈希无效")
                return False
            
            # 验证 QKD 签名
            if current.qkd_signature and self.qkd_key:
                expected = hashlib.hmac.new(
                    self.qkd_key, current.hash.encode(), hashlib.sha256
                ).hexdigest()
                if current.qkd_signature != expected:
                    print(f"❌ 区块 #{i} QKD签名无效")
                    return False
        
        print(f"✅ 链验证通过 ({len(self.chain)} 个区块)")
        return True
    
    def get_stats(self) -> dict:
        """链统计信息"""
        total_txs = sum(len(b.transactions) for b in self.chain)
        qkd_signed = sum(1 for b in self.chain if b.qkd_signature)
        return {
            'height': self.height,
            'total_transactions': total_txs,
            'pending_transactions': len(self.pending_txs),
            'qkd_signed_blocks': qkd_signed,
            'qkd_secured': self.qkd_key is not None,
            'nodes': len(self.nodes),
            'fault_tolerance': self.f
        }

import hashlib
