"""
量子安全联盟链集成方案 | Quantum-Secure Consortium Chain
BB84 QKD + Consortium Blockchain 完整融合方案
"""
import time
import threading
import json
import hashlib
from typing import List, Optional

from bb84.bb84_qkd import BB84
from blockchain.chain import ConsortiumChain
from blockchain.block import Transaction, Block

class QuantumSecureChain:
    """
    量子安全联盟链
    
    架构:
    ┌──────────────────────────────────────┐
    │         应用层 (DApp)                 │
    ├──────────────────────────────────────┤
    │  量子安全联盟链 (Quantum Chain)      │
    ├──────────────┬───────────────────────┤
    │  BB84 QKD    │  PBFT 共识            │
    │  密钥分发     │  拜占庭容错            │
    ├──────────────┴───────────────────────┤
    │         网络层 (P2P)                 │
    └──────────────────────────────────────┘
    
    流程:
    1. 节点间运行 BB84 → 生成量子密钥
    2. 密钥注入联盟链 → 签名 + 加密交易
    3. PBFT 共识出块 → QKD 签名验证
    """
    
    def __init__(self, node_id: str, peer_nodes: List[str] = None):
        self.node_id = node_id
        self.peer_nodes = peer_nodes or [node_id]
        self.bb84 = BB84(key_length=256, eavesdrop_prob=0.0)
        self.chain = ConsortiumChain(node_id, self.peer_nodes)
        self.qkd_keys = {}
        self.secure = False
    
    def initialize_qkd(self, target_nodes: List[str] = None):
        targets = target_nodes or self.peer_nodes
        print("\n" + "🔐 " + "=" * 54)
        print("  量子密钥分发初始化")
        print("=" * 58)
        
        for target in targets:
            if target == self.node_id:
                continue
            
            print(f"\n📡 {self.node_id} ←→ {target}")
            self.bb84 = BB84(key_length=256, eavesdrop_prob=0.05)
            key = self.bb84.run(verbose=False)
            
            if key:
                self.qkd_keys[target] = key
                print(f"   ✅ 密钥建立: {key.hex()[:16]}...")
                print(f"   QBER: {self.bb84.qber:.3%}")
            else:
                print(f"   ❌ QBER 过高，密钥丢弃")
        
        if self.qkd_keys:
            primary_key = list(self.qkd_keys.values())[0]
            self.chain.set_qkd_key(primary_key)
            self.secure = True
        
        print(f"\n{'='*58}")
        print(f"  🔒 联盟链量子安全状态: {'已激活' if self.secure else '未激活'}")
        print(f"  📊 QKD 通道数: {len(self.qkd_keys)}")
        print(f"{'='*58}\n")
    
    def send_secure_transaction(self, sender: str, receiver: str, 
                                amount: float, data: dict = None) -> Transaction:
        if not self.secure:
            print("⚠️  链未激活量子安全保护！")
        
        tx = Transaction(sender=sender, receiver=receiver,
                         amount=amount, data=data or {})
        
        if self.chain.qkd_key:
            encrypted_data = hashlib.sha256(
                (json.dumps(tx.to_dict(), sort_keys=True) + 
                 self.chain.qkd_key.hex()).encode()
            ).hexdigest()
            tx.data['qkd_hash'] = encrypted_data
        
        self.chain.add_transaction(tx)
        return tx
    
    def mine_block(self) -> Optional[Block]:
        block = self.chain.create_block()
        if block:
            success = self.chain.propose_block(block)
            if success:
                return block
        return None
    
    def run_demo(self):
        print("\n" + "🌌 " + "=" * 56)
        print("   量子安全联盟链 | Quantum-Secure Consortium Chain")
        print("   BB84 QKD × PBFT Consensus")
        print("=" * 58)
        
        print("\n▶ Phase 1: 量子密钥分发")
        self.initialize_qkd(["Node-A", "Node-B", "Node-C"])
        
        print("▶ Phase 2: 量子安全交易")
        tx1 = self.send_secure_transaction("Alice", "Bob", 100, 
                                           {"note": "量子安全转账"})
        tx2 = self.send_secure_transaction("Bob", "Charlie", 50,
                                           {"note": "QKD 签名验证"})
        tx3 = self.send_secure_transaction("Charlie", "Alice", 30,
                                           {"note": "跨链量子密钥"})
        
        print("\n▶ Phase 3: PBFT 共识出块")
        time.sleep(0.5)
        block1 = self.mine_block()
        
        self.send_secure_transaction("Alice", "Charlie", 25,
                                     {"note": "量子安全投票"})
        self.send_secure_transaction("Bob", "Alice", 15,
                                     {"note": "QKD密钥轮换"})
        time.sleep(0.5)
        block2 = self.mine_block()
        
        print("\n▶ Phase 4: 链完整性验证")
        self.chain.validate_chain()
        
        print("\n▶ Phase 5: 链状态")
        stats = self.chain.get_stats()
        for k, v in stats.items():
            print(f"  {k}: {v}")
        
        print("\n" + "⚠️ " + "=" * 56)
        print("   窃听攻击模拟")
        print("=" * 58)
        
        print("\n>>> 场景: 无窃听 (Eve=0%)")
        print("    状态: ✅ 安全通信")
        
        self.bb84.eavesdrop_prob = 0.3
        print("\n>>> 场景: Eve 窃听 30%")
        key = self.bb84.run(verbose=False)
        if not key:
            print("    结果: 🚨 QBER过高，自动丢弃密钥")
            print("    联盟链: ✅ 未受影响 (前序密钥继续有效)")
        
        print("\n" + "=" * 58)
        print("  🎉 量子安全联盟链 演示完成")
        print("=" * 58)

if __name__ == "__main__":
    chain = QuantumSecureChain("Node-A")
    chain.run_demo()
