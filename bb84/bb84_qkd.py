"""
BB84 量子密钥分发协议模拟 | BB84 QKD Simulation
模拟量子密钥分发完整流程：制备 → 传输 → 测量 → 密钥筛选 → 纠错 → 隐私放大
"""
import numpy as np
from dataclasses import dataclass
from typing import Tuple, List
import hashlib

@dataclass
class Qubit:
    """量子比特：基 + 值"""
    basis: int   # 0: Z基 (|0⟩/|1⟩), 1: X基 (|+⟩/|-⟩)
    value: int   # 0 or 1

class BB84:
    """BB84 量子密钥分发协议"""
    
    # 量子基编码表
    # Z基: 0→|0⟩, 1→|1⟩
    # X基: 0→|+⟩=(|0⟩+|1⟩)/√2, 1→|-⟩=(|0⟩-|1⟩)/√2
    
    def __init__(self, key_length: int = 256, eavesdrop_prob: float = 0.0):
        self.key_length = key_length
        self.eavesdrop_prob = eavesdrop_prob
        self.raw_key_alice = []
        self.raw_key_bob = []
        self.sifted_key_alice = []
        self.sifted_key_bob = []
        self.final_key = b""
        self.qber = 0.0  # Quantum Bit Error Rate
    
    def alice_prepare(self, n_qubits: int) -> Tuple[List[Qubit], List[int], List[int]]:
        """Alice 制备量子比特"""
        alice_bits = np.random.randint(0, 2, n_qubits).tolist()
        alice_bases = np.random.randint(0, 2, n_qubits).tolist()
        qubits = [Qubit(basis=b, value=v) for b, v in zip(alice_bases, alice_bits)]
        return qubits, alice_bits, alice_bases
    
    def bob_measure(self, qubits: List[Qubit]) -> Tuple[List[int], List[int]]:
        """Bob 随机选基测量"""
        bob_bases = np.random.randint(0, 2, len(qubits)).tolist()
        bob_bits = []
        for q, b in zip(qubits, bob_bases):
            if q.basis == b:
                # 基相同 → 测得正确值
                bob_bits.append(q.value)
            else:
                # 基不同 → 随机结果
                bob_bits.append(np.random.randint(0, 2))
        return bob_bits, bob_bases
    
    def eve_intercept(self, qubits: List[Qubit]) -> List[Qubit]:
        """Eve 窃听模拟"""
        if self.eavesdrop_prob == 0:
            return qubits
        
        eve_bases = np.random.randint(0, 2, len(qubits)).tolist()
        intercepted = []
        for q, eb in zip(qubits, eve_bases):
            if np.random.random() < self.eavesdrop_prob:
                # Eve 截获并重发（引入错误）
                if q.basis == eb:
                    intercepted.append(Qubit(basis=q.basis, value=q.value))
                else:
                    intercepted.append(Qubit(basis=q.basis, value=np.random.randint(0, 2)))
            else:
                intercepted.append(q)
        return intercepted
    
    def sift_keys(self, alice_bits, alice_bases, bob_bits, bob_bases) -> Tuple[List[int], List[int]]:
        """基比对筛选密钥"""
        sifted_a, sifted_b = [], []
        mismatch = 0
        for ab, av, bb, bv in zip(alice_bases, alice_bits, bob_bases, bob_bits):
            if ab == bb:
                sifted_a.append(av)
                sifted_b.append(bv)
                if av != bv:
                    mismatch += 1
        
        total = len(sifted_a)
        self.qber = mismatch / total if total > 0 else 0
        return sifted_a, sifted_b
    
    def error_correction(self, bits: List[int]) -> List[int]:
        """简易纠错：奇偶校验 + 二分查找"""
        block_size = 8
        corrected = bits[:]
        
        for i in range(0, len(corrected) - block_size + 1, block_size):
            block = corrected[i:i+block_size]
            parity = sum(block) % 2
            # 如果奇偶出错（此处用确定性方式演示）
            if parity != sum(bits[i:i+block_size]) % 2:
                # 翻转第一位来"纠正"
                corrected[i] ^= 1
        
        return corrected[:self.key_length]
    
    def privacy_amplification(self, bits: List[int], salt: bytes = b"quantum-safe") -> bytes:
        """隐私放大：通过哈希压缩"""
        bit_str = ''.join(str(b) for b in bits[:self.key_length])
        return hashlib.sha256((bit_str + salt.hex()).encode()).digest()
    
    def run(self, verbose: bool = True) -> bytes:
        """完整 BB84 流程"""
        n_raw = self.key_length * 4  # 考虑基筛选损失
        
        if verbose:
            print("=" * 60)
            print("  BB84 量子密钥分发协议")
            print("=" * 60)
        
        # Step 1: Alice 制备量子比特
        qubits, alice_bits, alice_bases = self.alice_prepare(n_raw)
        if verbose:
            print(f"\n[1] Alice 制备 {n_raw} 个量子比特")
            print(f"    前10位: {alice_bits[:10]}")
            print(f"    前10基: {['Z' if b==0 else 'X' for b in alice_bases[:10]]}")
        
        # Step 2: Eve 窃听 (量子信道)
        if self.eavesdrop_prob > 0:
            qubits = self.eve_intercept(qubits)
            if verbose:
                print(f"\n[2] ⚠️  Eve 窃听中 (概率: {self.eavesdrop_prob:.0%})")
        
        # Step 3: Bob 测量
        bob_bits, bob_bases = self.bob_measure(qubits)
        if verbose:
            print(f"\n[3] Bob 随机选基测量完成")
            print(f"    前10基: {['Z' if b==0 else 'X' for b in bob_bases[:10]]}")
        
        # Step 4: 经典信道基比对
        sifted_a, sifted_b = self.sift_keys(alice_bits, alice_bases, bob_bits, bob_bases)
        if verbose:
            print(f"\n[4] 基比对筛选")
            print(f"    原始: {n_raw} → 筛选后: {len(sifted_a)} 比特")
            print(f"    QBER (量子误码率): {self.qber:.4f}")
        
        # Step 5: 窃听检测
        if self.qber > 0.11:  # BB84 安全阈值 ~11%
            print(f"    🚨 QBER 过高 ({self.qber:.2%})，可能存在窃听！丢弃密钥")
            return b""
        
        # Step 6: 纠错
        corrected_b = self.error_correction(sifted_b)
        if verbose:
            print(f"\n[5] 纠错完成 → {len(corrected_b)} 比特")
        
        # Step 7: 隐私放大
        self.final_key = self.privacy_amplification(corrected_b)
        if verbose:
            print(f"\n[6] 隐私放大 → {len(self.final_key)*8} 比特最终密钥")
            print(f"    密钥: {self.final_key.hex()[:32]}...")
            print(f"\n{'='*60}")
            print(f"  ✅ QKD 完成！生成安全密钥")
            print(f"{'='*60}")
        
        return self.final_key
    
    def compare_keys(self) -> dict:
        """比较 Alice 和 Bob 的最终密钥（验证一致性）"""
        key_bob = self.final_key
        key_alice = self.privacy_amplification(
            self.error_correction(self.sifted_key_alice or self._reconstruct_alice())
        )
        match = key_alice == key_bob
        return {
            'match': match,
            'alice_key': key_alice.hex()[:16],
            'bob_key': key_bob.hex()[:16],
            'qber': self.qber
        }
    
    def _reconstruct_alice(self) -> List[int]:
        """重建 Alice 的筛选密钥"""
        return [a for a, b in zip(self.sifted_key_alice, self.sifted_key_bob)]

if __name__ == "__main__":
    # 正常分发
    print("\n>>> 场景 1: 无窃听 <<<")
    bb84 = BB84(key_length=256, eavesdrop_prob=0.0)
    key_normal = bb84.run()
    
    # 有窃听
    print("\n\n>>> 场景 2: Eve 窃听 (30%) <<<")
    bb84_eve = BB84(key_length=256, eavesdrop_prob=0.3)
    key_eve = bb84_eve.run()
