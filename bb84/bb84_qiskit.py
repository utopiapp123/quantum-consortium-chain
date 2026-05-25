"""
BB84 Qiskit 真量子态实现 | Quantum-State BB84 on Qiskit
使用真实量子电路模拟 BB84 协议：量子比特制备、传输、测量
"""
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

class BB84Qiskit:
    """
    基于 Qiskit 量子电路的 BB84 实现
    
    量子态映射:
    ┌──────┬──────────┬──────────┐
    │ 比特 │ Z 基编码  │ X 基编码  │
    ├──────┼──────────┼──────────┤
    │  0   │  |0⟩     │  |+⟩     │
    │  1   │  |1⟩     │  |-⟩     │
    └──────┴──────────┴──────────┘
    
    Z 基: |0⟩, |1⟩ — 计算基
    X 基: |+⟩ = (|0⟩+|1⟩)/√2, |-⟩ = (|0⟩-|1⟩)/√2
    """
    
    def __init__(self, n_qubits: int = 8, eavesdrop: bool = False):
        self.n_qubits = n_qubits
        self.eavesdrop = eavesdrop
        self.simulator = AerSimulator()
        
        # 存储
        self.alice_bits = []
        self.alice_bases = []
        self.bob_bases = []
        self.bob_results = []
        self.eve_bases = []
        self.eve_results = []
        self.qber = 0.0
        self.counts = {}
    
    def prepare_qubit(self, bit: int, basis: int) -> QuantumCircuit:
        """
        制备单个量子比特
        basis=0 (Z基): |0⟩ 或 |1⟩
        basis=1 (X基): |+⟩ 或 |-⟩
        """
        qc = QuantumCircuit(1, 1)
        
        if bit == 1:
            qc.x(0)  # 翻转到 |1⟩
        
        if basis == 1:
            qc.h(0)  # Hadamard → |+⟩ 或 |-⟩
        
        return qc
    
    def measure_qubit(self, qc: QuantumCircuit, basis: int) -> QuantumCircuit:
        """在指定基上测量"""
        if basis == 1:
            qc.h(0)  # 转回 Z 基测量
        
        qc.measure(0, 0)
        return qc
    
    def alice_prepare(self):
        """Alice 随机选 bit 和 basis 制备量子比特"""
        self.alice_bits = np.random.randint(0, 2, self.n_qubits).tolist()
        self.alice_bases = np.random.randint(0, 2, self.n_qubits).tolist()
        
        print(f"Alice 制备 {self.n_qubits} 个量子比特:")
        for i in range(min(8, self.n_qubits)):
            b = 'Z' if self.alice_bases[i] == 0 else 'X'
            print(f"  q[{i}]: bit={self.alice_bits[i]}, basis={b}")
    
    def bob_measure(self):
        """Bob 随机选基测量"""
        self.bob_bases = np.random.randint(0, 2, self.n_qubits).tolist()
        self.bob_results = []
        
        for i in range(self.n_qubits):
            qc = self.prepare_qubit(self.alice_bits[i], self.alice_bases[i])
            
            # Eve 窃听
            if self.eavesdrop and np.random.random() < 0.3:
                eve_basis = np.random.randint(0, 2)
                qc = self.measure_qubit(qc, eve_basis)
                # 窃听后重制备（破坏原态）
                qc = self.prepare_qubit(
                    np.random.randint(0, 2), eve_basis
                )
            
            # Bob 测量
            qc = self.measure_qubit(qc, self.bob_bases[i])
            
            # 运行
            job = self.simulator.run(qc, shots=1)
            result = job.result()
            counts = result.get_counts()
            measured = int(list(counts.keys())[0])
            self.bob_results.append(measured)
    
    def sift_and_compare(self) -> dict:
        """基比对 + 计算 QBER"""
        matches = 0
        errors = 0
        sifted = []
        
        for i in range(self.n_qubits):
            if self.alice_bases[i] == self.bob_bases[i]:
                matches += 1
                if self.alice_bits[i] != self.bob_results[i]:
                    errors += 1
                else:
                    sifted.append(self.alice_bits[i])
        
        self.qber = errors / matches if matches > 0 else 0
        
        return {
            'total_qubits': self.n_qubits,
            'matching_bases': matches,
            'errors': errors,
            'qber': self.qber,
            'sifted_key_length': len(sifted),
            'efficiency': len(sifted) / self.n_qubits,
        }
    
    def run(self, verbose: bool = True) -> dict:
        """完整 BB84 Qiskit 模拟"""
        if verbose:
            print("\n" + "=" * 60)
            print("  BB84 Qiskit 量子电路模拟")
            print("=" * 60)
        
        self.alice_prepare()
        self.bob_measure()
        result = self.sift_and_compare()
        
        if verbose:
            print(f"\n基匹配: {result['matching_bases']}/{result['total_qubits']}")
            print(f"错误数: {result['errors']}")
            print(f"QBER: {result['qber']:.4f}")
            print(f"筛选密钥长度: {result['sifted_key_length']} bits")
            
            if self.eavesdrop and result['qber'] > 0.11:
                print("🚨 QBER 超出 11% 阈值 — 检测到窃听!")
            elif self.eavesdrop:
                print("⚠️  轻微窃听检测")
            else:
                print("✅ 安全信道")
        
        return result
    
    def draw_circuit(self, qubit_idx: int = 0, save_path: str = None):
        """绘制单量子比特电路图"""
        qc = self.prepare_qubit(self.alice_bits[qubit_idx], 
                                self.alice_bases[qubit_idx])
        qc = self.measure_qubit(qc, self.bob_bases[qubit_idx])
        
        fig = qc.draw(output='mpl', style='iqp')
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        return fig

if __name__ == "__main__":
    print(">>> 场景 1: 无窃听 BB84 <<<")
    bb84 = BB84Qiskit(n_qubits=64, eavesdrop=False)
    r = bb84.run()
    
    print("\n>>> 场景 2: 有窃听 BB84 <<<")
    bb84_eve = BB84Qiskit(n_qubits=64, eavesdrop=True)
    r_eve = bb84_eve.run()
    
    print("\n>>> 对比 <<<")
    print(f"  无窃听 QBER: {r['qber']:.4f}")
    print(f"  有窃听 QBER: {r_eve['qber']:.4f}")
    print(f"  QBER 增幅: {(r_eve['qber'] - r['qber'])*100:.2f}%")
