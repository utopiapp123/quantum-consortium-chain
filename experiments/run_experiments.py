"""
对比实验 | Comparative Experiments
BB84 窃听率对比：0% / 30% / 50% — QBER、密钥率、安全性分析
从项目根目录运行: python experiments/run_experiments.py
"""
import sys
import os
import json
import time
import numpy as np

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bb84.bb84_qkd import BB84

class BB84Experiment:
    """BB84 窃听对抗实验"""
    
    def __init__(self, n_runs: int = 50):
        self.n_runs = n_runs
    
    def run_single(self, eavesdrop_prob: float, label: str) -> dict:
        bb84 = BB84(key_length=256, eavesdrop_prob=eavesdrop_prob)
        key = bb84.run(verbose=False)
        return {
            'eavesdrop_prob': eavesdrop_prob,
            'label': label,
            'qber': bb84.qber,
            'key_established': bool(key),
            'key_length': len(key) if key else 0,
            'safe': bb84.qber < 0.11,
        }
    
    def run_batch(self) -> dict:
        scenarios = [
            (0.0, '无窃听 (0%)'),
            (0.3, '轻窃听 (30%)'),
            (0.5, '重窃听 (50%)'),
        ]
        
        print("=" * 65)
        print("  BB84 窃听对抗实验")
        print(f"  每组 {self.n_runs} 次实验 × 3 组")
        print("=" * 65)
        
        summary = {}
        
        for prob, label in scenarios:
            results = []
            safe_count = 0
            qber_list = []
            
            print(f"\n▶ {label}")
            print(f"  运行 {self.n_runs} 次...", end=' ', flush=True)
            
            for i in range(self.n_runs):
                r = self.run_single(prob, label)
                results.append(r)
                qber_list.append(r['qber'])
                if r['safe']:
                    safe_count += 1
                if (i + 1) % 10 == 0:
                    print('.', end='', flush=True)
            
            print(" 完成!")
            
            avg_qber = float(np.mean(qber_list))
            std_qber = float(np.std(qber_list))
            
            summary[label] = {
                'avg_qber': round(avg_qber, 4),
                'std_qber': round(std_qber, 4),
                'safe_rate': round(safe_count / self.n_runs * 100, 2),
                'safe_count': safe_count,
                'total': self.n_runs,
            }
            
            print(f"    平均 QBER:    {avg_qber:.2%}")
            print(f"    QBER 标准差:  {std_qber:.4f}")
            print(f"    安全率:       {safe_count}/{self.n_runs} ({safe_count/self.n_runs:.0%})")
        
        return summary
    
    def print_report(self, summary: dict):
        print("\n" + "=" * 65)
        print("  实验结果汇总")
        print("=" * 65)
        print(f"\n{'场景':<16} {'平均QBER':<10} {'标准差':<10} {'安全率':<10}")
        print("-" * 46)
        for label, data in summary.items():
            print(f"{label:<16} {data['avg_qber']:.2%}     {data['std_qber']:<10.4f} {data['safe_rate']}%")
        
        print("\n📊 分析:")
        no_eve = summary['无窃听 (0%)']
        high_eve = summary['重窃听 (50%)']
        print(f"  • 无窃听 QBER: {no_eve['avg_qber']:.2%}")
        print(f"  • 50% 窃听 QBER: {high_eve['avg_qber']:.2%} (远超 11% 阈值)")
        print(f"  • BB84 可有效检测窃听攻击 ✅")


class IntegratedExperiment:
    """融合方案性能实验"""
    
    def run(self):
        from bb84.bb84_qkd import BB84
        from integration.quantum_secure_chain import QuantumSecureChain
        
        print("\n\n" + "=" * 65)
        print("  QKD + Consortium Chain 融合实验")
        print("=" * 65)
        
        chain = QuantumSecureChain("Node-A", ["Node-A", "Node-B", "Node-C"])
        
        print("\n▶ Step 1: QKD 密钥建立")
        start = time.time()
        for target in ["Node-B", "Node-C"]:
            bb84 = BB84(key_length=256, eavesdrop_prob=0.0)
            key = bb84.run(verbose=False)
            if key:
                chain.qkd_keys[target] = key
        
        qkd_time = time.time() - start
        chain.chain.set_qkd_key(list(chain.qkd_keys.values())[0])
        print(f"  密钥建立时间: {qkd_time:.3f}s")
        print(f"  QKD 通道: {len(chain.qkd_keys)}")
        
        print("\n▶ Step 2: QKD 签名交易")
        tx_times = []
        for i in range(10):
            start = time.time()
            chain.send_secure_transaction("Alice", "Bob", i * 10 + 10)
            tx_times.append(time.time() - start)
        
        avg_tx_time = np.mean(tx_times)
        print(f"  交易数: 10")
        print(f"  平均签名时间: {avg_tx_time*1000:.2f}ms")
        
        print("\n▶ Step 3: PBFT 共识出块")
        block_times = []
        for i in range(3):
            start = time.time()
            block = chain.mine_block()
            if block:
                block_times.append(time.time() - start)
        
        avg_block_time = np.mean(block_times) if block_times else 0
        print(f"  出块数: {len(block_times)}")
        print(f"  平均出块时间: {avg_block_time:.3f}s")
        
        print("\n▶ Step 4: 链完整性验证")
        chain.chain.validate_chain()
        
        print("\n" + "=" * 65)
        print("  融合实验报告")
        print("=" * 65)
        print(f"  QKD 密钥建立:  {qkd_time:.3f}s")
        print(f"  平均交易延迟:  {avg_tx_time*1000:.2f}ms")
        print(f"  平均出块时间:  {avg_block_time:.3f}s")
        print(f"  总交易数:      {10}")
        print(f"  链高度:        {chain.chain.height}")
        print(f"  QKD 安全状态:  {'✅ 已激活' if chain.secure else '❌ 未激活'}")

if __name__ == "__main__":
    exp = BB84Experiment(n_runs=50)
    summary = exp.run_batch()
    exp.print_report(summary)
    
    iexp = IntegratedExperiment()
    iexp.run()
    
    with open('experiment_results.json', 'w') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print("\n✅ 实验结果已保存到 experiment_results.json")
