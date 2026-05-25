"""
安全性对比分析 | ECDSA vs QKD Security Comparison
Shor 算法 vs BB84 — 量子时代区块链签名方案对比
"""
import time
import hashlib
import numpy as np
from dataclasses import dataclass
from typing import List

@dataclass
class SecurityMetric:
    """安全指标"""
    name: str
    ecdsa_classical: str
    ecdsa_quantum: str
    qkd_bb84: str
    notes: str

class SecurityComparison:
    """ECDSA vs QKD 全面对比"""
    
    @staticmethod
    def shor_attack_estimate(key_size: int = 256) -> dict:
        """
        Shor 算法攻击 ECDSA 时间估算
        经典 ECDSA-256: O(2^128) → 量子 Shor: O(n^3)
        """
        classical_ops = 2**128
        quantum_ops = key_size ** 3  # 约 16.7M 操作
        
        # 假设每秒 10^9 次运算
        classical_seconds = classical_ops / 1e9
        quantum_seconds = quantum_ops / 1e9
        
        classical_years = classical_seconds / (365 * 24 * 3600)
        
        return {
            'key_size': key_size,
            'classical_operations': f'2^{128}',
            'quantum_operations': f'{quantum_ops:.2e}',
            'classical_time': f'{classical_years:.2e} 年',
            'quantum_time': f'{quantum_seconds:.4f} 秒',
            'speedup': f'{classical_ops / quantum_ops:.2e}x'
        }
    
    @staticmethod
    def qkd_qber_analysis() -> dict:
        """
        BB84 在不同窃听率下的 QBER 分析
        QBER > 11% → 不安全，丢弃密钥
        """
        scenarios = [
            {'eve_prob': 0.0, 'label': '无窃听'},
            {'eve_prob': 0.1, 'label': '轻窃听 10%'},
            {'eve_prob': 0.3, 'label': '中窃听 30%'},
            {'eve_prob': 0.5, 'label': '重窃听 50%'},
            {'eve_prob': 0.7, 'label': '强窃听 70%'},
            {'eve_prob': 1.0, 'label': '全窃听 100%'},
        ]
        
        for s in scenarios:
            # BB84 理论 QBER = p_eve * (1/4 * 1/2) 当 Eve 随机猜基
            # 实际: 截获重发 → 当基失配时引入 50% 错误率
            eve_prob = s['eve_prob']
            # Eve 截获 → 1/2 基匹配(不引入错误) + 1/2 基失配(50%错误)
            s['expected_qber'] = eve_prob * 0.5 * 0.5
            s['safe'] = s['expected_qber'] < 0.11
        
        return scenarios
    
    @staticmethod
    def compare_table() -> List[SecurityMetric]:
        """生成完整对比表"""
        return [
            SecurityMetric(
                "抗量子攻击",
                "❌ 被 Shor 破解",
                "🕐 ~16,000,000 秒 (估)",
                "✅ 完全免疫",
                "BB84 安全性基于量子力学"
            ),
            SecurityMetric(
                "密钥分发",
                "❌ 需预共享/DH",
                "❌ DH 亦被 Shor 破解",
                "✅ 安全分发",
                "即用即分发"
            ),
            SecurityMetric(
                "窃听检测",
                "❌ 无法检测",
                "❌ 无法检测",
                "✅ QBER > 11%",
                "量子不可克隆定理"
            ),
            SecurityMetric(
                "前向安全",
                "❌ 私钥泄露→历史失效",
                "❌ 同上",
                "✅ 每次新密钥",
                "一次一密"
            ),
            SecurityMetric(
                "实现难度",
                "✅ 成熟方案",
                "❌ 需量子计算机",
                "⚠️  量子信道成本",
                "目前混合方案最现实"
            ),
            SecurityMetric(
                "标准化",
                "✅ NIST FIPS 186",
                "⏳ NIST PQC 进行中",
                "✅ ETSI GS QKD",
                "已标准化"
            ),
        ]
    
    def run_analysis(self):
        """完整分析报告"""
        print("=" * 65)
        print("  量子时代区块链签名方案安全性对比")
        print("  ECDSA vs QKD-BB84")
        print("=" * 65)
        
        # Part 1: Shor 攻击 ECDSA
        print("\n▶ Part 1: Shor 算法攻击 ECDSA-256")
        shor = self.shor_attack_estimate(256)
        print(f"  经典安全性: {shor['classical_operations']} 次操作")
        print(f"  经典破解时间: {shor['classical_time']}")
        print(f"  量子破解时间: {shor['quantum_time']}")
        print(f"  加速比: {shor['speedup']}")
        
        # Part 2: BB84 QBER 分析
        print("\n▶ Part 2: BB84 QBER 窃听检测")
        print(f"  {'窃听率':<12} {'预期 QBER':<12} {'状态':<10}")
        print("  " + "-" * 34)
        scenarios = self.qkd_qber_analysis()
        for s in scenarios:
            status = "✅ 安全" if s['safe'] else "🚨 丢弃"
            print(f"  {s['label']:<12} {s['expected_qber']:.1%}{'':>6} {status}")
        
        # Part 3: 综合对比
        print("\n▶ Part 3: 综合对比表")
        print("=" * 65)
        table = self.compare_table()
        header = f"  {'指标':<14} {'ECDSA经典':<14} {'ECDSA量子':<16} {'QKD-BB84':<12}"
        print(header)
        print("  " + "-" * 63)
        for row in table:
            print(f"  {row.name:<14} {row.ecdsa_classical:<14} {row.ecdsa_quantum:<16} {row.qkd_bb84:<12}")
        
        # Part 4: 结论
        print("\n▶ Part 4: 结论")
        print("  ┌────────────────────────────────────────────────────┐")
        print("  │ 量子计算机实用化后，ECDSA 将不再安全。           │")
        print("  │ BB84 QKD + 联盟链是可行的抗量子方案。            │")
        print("  │ 当前最佳实践: 混合部署（ECDSA + QKD 并行）。     │")
        print("  └────────────────────────────────────────────────────┘")
        
        return {'shor': shor, 'scenarios': scenarios, 'table': table}

if __name__ == "__main__":
    sc = SecurityComparison()
    sc.run_analysis()
