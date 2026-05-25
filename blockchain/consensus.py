"""
PBFT 共识 | Practical Byzantine Fault Tolerance
联盟链实用拜占庭容错共识算法
"""
import time
import random
from typing import List
from blockchain.block import Block

class PBFTConsensus:
    """PBFT 共识引擎"""
    
    # 阶段定义
    PRE_PREPARE = "pre-prepare"
    PREPARE = "prepare"
    COMMIT = "commit"
    
    def __init__(self, node_id: str, nodes: List[str], f: int = 1):
        self.node_id = node_id
        self.nodes = nodes
        self.f = f  # 最大容错节点数
        self.quorum = 2 * f + 1  # 法定人数
        self.view = 0
        self.sequence_number = 0
    
    def reach_consensus(self, block: Block) -> bool:
        """尝试达成共识"""
        total_nodes = len(self.nodes)
        
        if total_nodes < self.quorum:
            print(f"  ⚠️  节点数不足 ({total_nodes} < {self.quorum})")
            return False
        
        # 模拟投票
        votes = 0
        
        # Phase 1: Pre-Prepare
        print(f"  [{self.PRE_PREPARE}] 主节点广播区块...")
        time.sleep(0.1)
        
        # Phase 2: Prepare (模拟各节点验证)
        for node in self.nodes:
            if self._simulate_node_vote(node, block):
                votes += 1
        
        print(f"  [{self.PREPARE}] 投票: {votes}/{total_nodes} (需要 {self.quorum})")
        
        if votes < self.quorum:
            print(f"  ❌ 共识失败 - 票数不足")
            return False
        
        # Phase 3: Commit
        print(f"  [{self.COMMIT}] 提交区块...")
        time.sleep(0.1)
        
        return True
    
    def _simulate_node_vote(self, node_id: str, block: Block) -> bool:
        """模拟节点投票（真实场景下是网络通信）"""
        # 拜占庭节点有概率投反对
        if node_id == self.node_id:
            return True
        # 90% 概率同意
        return random.random() < 0.9
    
    def is_primary(self) -> bool:
        """判断当前节点是否是主节点"""
        return self.nodes[self.view % len(self.nodes)] == self.node_id
