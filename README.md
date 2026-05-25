# 🌌 Quantum Consortium Chain

> **量子安全联盟链** — BB84 QKD × PBFT Consensus

将 BB84 量子密钥分发协议与联盟链深度融合，构建抗量子计算攻击的安全区块链。

**🏆 适用场景: 课程设计 / 毕业设计 / 学术研究**

---

## 🎯 核心思想

传统区块链依赖 ECDSA/RSA 签名，Shor 算法能在多项式时间内破解。本项目将 **BB84 QKD 生成的量子密钥** 注入联盟链：

```
┌──────────────────────────────────────────────────────────┐
│                    量子安全联盟链                         │
│                                                          │
│   BB84 QKD (Qiskit 真量子态) ──→ 量子密钥 ──→ 签名       │
│               ↓                          ↓               │
│   ┌─────────────────────┐    ┌──────────────────────┐    │
│   │  BB84 协议模拟       │    │  交易 QKD 加密        │    │
│   │  • NumPy 经典模拟    │    │  区块 HMAC 签名       │    │
│   │  • Qiskit 量子电路   │    │  窃听检测 (QBER)      │    │
│   └─────────────────────┘    └──────────────────────┘    │
│               ↓                          ↓               │
│   ┌──────────────────────────────────────────────────┐   │
│   │         PBFT 共识 (PrePrepare→Prepare→Commit)     │   │
│   └──────────────────────────────────────────────────┘   │
│               ↓                          ↓               │
│   ┌──────────────┐    ┌──────────────┐    ┌───────────┐  │
│   │ 安全性分析    │    │  图表可视化   │    │ 对比实验   │  │
│   │ ECDSA vs QKD│    │  拓扑/雷达/QBER│   │ 0/30/50% │  │
│   └──────────────┘    └──────────────┘    └───────────┘  │
└──────────────────────────────────────────────────────────┘
```

---

## 📂 项目结构

```
quantum-consortium-chain/
├── bb84/                              # BB84 量子密钥分发
│   ├── bb84_qkd.py                    # NumPy 模拟 (完整协议流程)
│   └── bb84_qiskit.py                 # Qiskit 真量子态 (量子电路)
├── blockchain/                        # 联盟链核心
│   ├── block.py                       # 区块 & 交易 (QKD 签名/加密)
│   ├── chain.py                       # 联盟链 (QKD 密钥注入 + 链验证)
│   └── consensus.py                   # PBFT 实用拜占庭容错
├── integration/                       # 融合方案
│   └── quantum_secure_chain.py        # BB84 + 联盟链集成 + 演示
├── analysis/                          # 分析与可视化
│   ├── security_comparison.py         # ECDSA vs QKD 安全性对比
│   └── visualization.py               # 网络拓扑/雷达图/QBER/出块图
├── experiments/                       # 实验
│   └── run_experiments.py             # 窃听对比实验 + 融合性能测试
├── requirements.txt
└── README.md
```

---

## 🚀 快速开始

```bash
pip install -r requirements.txt

# 1. 完整融合演示
python integration/quantum_secure_chain.py

# 2. BB84 真量子态模拟 (Qiskit)
python bb84/bb84_qiskit.py

# 3. 安全性对比分析
python analysis/security_comparison.py

# 4. 生成可视化图表
python analysis/visualization.py

# 5. 批量对比实验
python experiments/run_experiments.py
```

---

## 📊 实验结果预览

| 窃听率 | 平均 QBER | 安全率 | 状态 |
|--------|-----------|--------|------|
| 0% | ~0.0% | 100% | ✅ 安全 |
| 30% | ~7.5% | ~95% | ⚠️ 可检测 |
| 50% | ~12.5% | ~60% | 🚨 不安全 |

---

## 🔬 课程设计报告结构建议

```
一、背景与意义
    1.1 量子计算对区块链的威胁
    1.2 BB84 与联盟链融合价值

二、理论基础
    2.1 BB84 量子密钥分发协议
    2.2 PBFT 拜占庭容错共识
    2.3 Shor/Grover 算法威胁模型

三、系统设计
    3.1 总体架构
    3.2 QKD 密钥注入流程
    3.3 量子安全签名机制

四、实现与实验
    4.1 Qiskit 量子电路实现
    4.2 联盟链 PBFT 共识
    4.3 窃听攻击对抗实验
    4.4 对比图表分析

五、安全性分析
    5.1 ECDSA vs QKD 对比
    5.2 QBER 窃听检测分析

六、总结与展望
```

---

## ⚠️ 免责声明

本项目为学术研究与概念验证，不适用于生产环境。
