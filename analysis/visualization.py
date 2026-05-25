"""
可视化模块 | Visualization Suite
网络拓扑图 / QBER 曲线 / 出块时序 / 安全性雷达图
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import networkx as nx

# 中文字体设置
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

class Visualizer:
    """量子安全联盟链可视化"""
    
    @staticmethod
    def plot_network_topology(nodes: list, qkd_links: list, 
                              save_path: str = None):
        """绘制网络拓扑图"""
        G = nx.Graph()
        G.add_nodes_from(nodes)
        G.add_edges_from(qkd_links)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        pos = nx.spring_layout(G, seed=42, k=2)
        
        # 节点
        nx.draw_networkx_nodes(G, pos, node_color='#2196F3', 
                               node_size=2000, alpha=0.9, ax=ax)
        # 边 - QKD 链路用特殊样式
        nx.draw_networkx_edges(G, pos, edge_color='#4CAF50', 
                               width=3, style='dashed', alpha=0.8, ax=ax)
        # 标签
        nx.draw_networkx_labels(G, pos, font_size=11, font_color='white',
                                font_weight='bold', ax=ax)
        
        ax.set_title('Quantum Consortium Chain Network Topology', 
                     fontsize=14, fontweight='bold', pad=20)
        
        # 图例
        legend_elements = [
            mpatches.Patch(color='#2196F3', label='Consortium Node'),
            mpatches.Patch(color='#4CAF50', label='QKD Channel (BB84)')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        ax.axis('off')
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight', 
                       facecolor='#0D1117', edgecolor='none')
        return fig
    
    @staticmethod
    def plot_qber_curve(eavesdrop_rates: list, qber_values: list, 
                        threshold: float = 0.11, save_path: str = None):
        """绘制 QBER 随窃听率变化曲线"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.plot(eavesdrop_rates, [v * 100 for v in qber_values], 
                'o-', color='#FF5722', linewidth=2.5, markersize=8,
                label='QBER')
        ax.axhline(y=threshold * 100, color='#E91E63', linestyle='--', 
                   linewidth=2, label=f'Security Threshold ({threshold:.0%})')
        
        ax.fill_between(eavesdrop_rates, 0, [v * 100 for v in qber_values],
                         alpha=0.2, color='#FF5722')
        ax.fill_between(eavesdrop_rates, threshold * 100, 50,
                         alpha=0.1, color='#E91E63', 
                         label='UNSAFE Zone')
        
        ax.set_xlabel('Eavesdropping Rate', fontsize=12)
        ax.set_ylabel('QBER (%)', fontsize=12)
        ax.set_title('BB84 QBER vs Eavesdropping Rate', 
                     fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 55)
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        return fig
    
    @staticmethod
    def plot_block_timeline(blocks: list, save_path: str = None):
        """绘制出块时序图"""
        fig, ax = plt.subplots(figsize=(12, 5))
        
        heights = range(len(blocks))
        colors = ['#4CAF50' if b.get('qkd_signed') else '#FFC107' 
                  for b in blocks]
        
        bars = ax.barh(heights, [b['tx_count'] for b in blocks], 
                       color=colors, edgecolor='white', height=0.6)
        
        for i, b in enumerate(blocks):
            ax.text(b['tx_count'] + 0.2, i, 
                    f"Block #{b['index']}\n{b['tx_count']} txs\nQKD: {'Yes' if b['qkd_signed'] else 'No'}",
                    va='center', fontsize=9)
        
        ax.set_xlabel('Transaction Count', fontsize=12)
        ax.set_ylabel('Block Height', fontsize=12)
        ax.set_title('Consortium Chain Block Timeline', 
                     fontsize=14, fontweight='bold')
        ax.set_yticks(heights)
        ax.set_yticklabels([f'#{b["index"]}' for b in blocks])
        
        legend_elements = [
            mpatches.Patch(color='#4CAF50', label='QKD Signed'),
            mpatches.Patch(color='#FFC107', label='Unsigned')
        ]
        ax.legend(handles=legend_elements, loc='lower right')
        ax.grid(True, alpha=0.2, axis='x')
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        return fig
    
    @staticmethod
    def plot_security_radar(save_path: str = None):
        """安全性雷达图"""
        categories = ['Quantum
Resistance', 'Key
Distribution', 
                      'Eavesdrop
Detection', 'Forward
Security',
                      'Implementation
Maturity']
        N = len(categories)
        
        ecdsa_values = [1, 3, 1, 1, 5]
        qkd_values = [5, 5, 5, 5, 2]
        hybrid_values = [5, 5, 5, 5, 4]
        
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        ecdsa_values += ecdsa_values[:1]
        qkd_values += qkd_values[:1]
        hybrid_values += hybrid_values[:1]
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        
        ax.plot(angles, ecdsa_values, 'o-', linewidth=2, 
                color='#E91E63', label='ECDSA (Classical)')
        ax.fill(angles, ecdsa_values, alpha=0.1, color='#E91E63')
        
        ax.plot(angles, qkd_values, 'o-', linewidth=2,
                color='#4CAF50', label='QKD-BB84')
        ax.fill(angles, qkd_values, alpha=0.1, color='#4CAF50')
        
        ax.plot(angles, hybrid_values, 'o-', linewidth=2,
                color='#2196F3', label='Hybrid (Proposed)')
        ax.fill(angles, hybrid_values, alpha=0.1, color='#2196F3')
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=10)
        ax.set_ylim(0, 5.5)
        ax.set_yticks([1, 2, 3, 4, 5])
        ax.set_title('Security Comparison: ECDSA vs QKD vs Hybrid',
                     fontsize=14, fontweight='bold', pad=30)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        ax.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        return fig
    
    @staticmethod
    def generate_all(save_dir: str = "."):
        """生成全部可视化图表"""
        import os
        os.makedirs(save_dir, exist_ok=True)
        
        print("生成网络拓扑图...")
        Visualizer.plot_network_topology(
            ['Node-A', 'Node-B', 'Node-C', 'Node-D'],
            [('Node-A','Node-B'), ('Node-B','Node-C'), 
             ('Node-C','Node-D'), ('Node-D','Node-A'),
             ('Node-A','Node-C')],
            f"{save_dir}/network_topology.png"
        )
        print("  ✓ network_topology.png")
        
        print("生成 QBER 曲线...")
        eve_rates = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        qber_vals = [r * 0.25 for r in eve_rates]
        Visualizer.plot_qber_curve(eve_rates, qber_vals, 
                                   save_path=f"{save_dir}/qber_curve.png")
        print("  ✓ qber_curve.png")
        
        print("生成出块时序...")
        blocks = [
            {'index': 1, 'tx_count': 3, 'qkd_signed': True},
            {'index': 2, 'tx_count': 5, 'qkd_signed': True},
            {'index': 3, 'tx_count': 2, 'qkd_signed': True},
            {'index': 4, 'tx_count': 7, 'qkd_signed': True},
            {'index': 5, 'tx_count': 4, 'qkd_signed': True},
        ]
        Visualizer.plot_block_timeline(blocks, 
                                       save_path=f"{save_dir}/block_timeline.png")
        print("  ✓ block_timeline.png")
        
        print("生成安全性雷达图...")
        Visualizer.plot_security_radar(save_path=f"{save_dir}/security_radar.png")
        print("  ✓ security_radar.png")
        
        print(f"\n✅ 全部图表已生成到 {save_dir}/")

if __name__ == "__main__":
    Visualizer.generate_all(".")
