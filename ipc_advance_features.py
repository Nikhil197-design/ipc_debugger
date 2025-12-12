"""
Advanced features for IPC Debugger
Includes performance profiling, pattern detection, and recommendations
"""

import time
import statistics
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Any
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# ==================== Performance Analyzer ====================

class PerformanceAnalyzer:
    """Analyze IPC performance patterns and bottlenecks"""

    def __init__(self):
        self.metrics_history = defaultdict(list)
        self.bottlenecks = []
        self.recommendations = []

    def analyze_latency_patterns(self, messages: List) -> Dict:
        """Analyze latency patterns in communications"""
        if not messages:
            return {}

        latencies = [msg.latency_ms for msg in messages]

        analysis = {
            'mean': statistics.mean(latencies),
            'median': statistics.median(latencies),
            'stdev': statistics.stdev(latencies) if len(latencies) > 1 else 0,
            'min': min(latencies),
            'max': max(latencies),
            'percentile_95': np.percentile(latencies, 95),
            'outliers': []
        }

        # Detect outliers (values beyond 2 standard deviations)
        if analysis['stdev'] > 0:
            threshold = analysis['mean'] + 2 * analysis['stdev']
            analysis['outliers'] = [l for l in latencies if l > threshold]

        return analysis

    def detect_communication_patterns(self, messages: List) -> Dict:
        """Detect communication patterns between processes"""
        patterns = {
            'frequent_pairs': Counter(),
            'message_flows': defaultdict(list),
            'peak_times': [],
            'idle_periods': []
        }

        # Count frequent communication pairs
        for msg in messages:
            pair = (msg.source_pid, msg.dest_pid)
            patterns['frequent_pairs'][pair] += 1

        # Identify message flows
        for msg in messages:
            patterns['message_flows'][msg.source_pid].append({
                'to': msg.dest_pid,
                'method': msg.method.value,
                'time': msg.timestamp
            })

        # Detect peak communication times
        time_buckets = defaultdict(int)
        for msg in messages:
            bucket = msg.timestamp.replace(second=0, microsecond=0)
            time_buckets[bucket] += 1

        if time_buckets:
            avg_messages = statistics.mean(time_buckets.values())
            patterns['peak_times'] = [
                time for time, count in time_buckets.items()
                if count > avg_messages * 1.5
            ]

        return patterns

    def identify_bottlenecks(self, processes: Dict, messages: List) -> List[Dict]:
        """Identify potential bottlenecks in IPC"""
        bottlenecks = []

        # Check for processes with high wait times
        process_wait_times = defaultdict(float)
        process_message_counts = defaultdict(int)

        for msg in messages:
            if msg.status != "Success":
                process_wait_times[msg.source_pid] += msg.latency_ms
                process_message_counts[msg.source_pid] += 1

        # Identify processes with abnormal wait times
        for pid, total_wait in process_wait_times.items():
            avg_wait = total_wait / process_message_counts[pid]
            if avg_wait > 100:  # More than 100ms average wait
                bottlenecks.append({
                    'type': 'high_wait_time',
                    'process_pid': pid,
                    'avg_wait_ms': avg_wait,
                    'severity': 'high' if avg_wait > 500 else 'medium'
                })

        # Check for message queue buildups
        queue_sizes = defaultdict(list)
        for msg in messages:
            if msg.method.value == "Message Queue":
                # Simulate queue size tracking
                queue_sizes[msg.dest_pid].append(msg.data_size)

        for pid, sizes in queue_sizes.items():
            if len(sizes) > 10 and statistics.mean(sizes) > 1024:
                bottlenecks.append({
                    'type': 'queue_buildup',
                    'process_pid': pid,
                    'avg_queue_size': statistics.mean(sizes),
                    'severity': 'medium'
                })

        return bottlenecks

    def generate_recommendations(self, analysis_results: Dict) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []

        # Check latency issues
        if 'latency_analysis' in analysis_results:
            latency = analysis_results['latency_analysis']
            if latency.get('max', 0) > 1000:
                recommendations.append(
                    "⚠️ High maximum latency detected (>1s). Consider using shared memory for large data transfers."
                )
            if latency.get('stdev', 0) > latency.get('mean', 1) * 0.5:
                recommendations.append(
                    "📊 High latency variance detected. Check for irregular system load or network issues."
                )

        # Check for bottlenecks
        if 'bottlenecks' in analysis_results:
            for bottleneck in analysis_results['bottlenecks']:
                if bottleneck['type'] == 'high_wait_time':
                    recommendations.append(
                        f"🔴 Process {bottleneck['process_pid']} has high wait times. "
                        f"Consider optimizing IPC method or increasing resources."
                    )
                elif bottleneck['type'] == 'queue_buildup':
                    recommendations.append(
                        f"📦 Queue buildup detected for process {bottleneck['process_pid']}. "
                        f"Consider increasing consumer throughput or using multiple consumers."
                    )

        # Check communication patterns
        if 'patterns' in analysis_results:
            patterns = analysis_results['patterns']
            frequent_pairs = patterns.get('frequent_pairs', {})
            if frequent_pairs:
                top_pair = max(frequent_pairs, key=frequent_pairs.get)
                if frequent_pairs[top_pair] > 100:
                    recommendations.append(
                        f"💬 High traffic between processes {top_pair[0]} and {top_pair[1]}. "
                        f"Consider using persistent connections or shared memory."
                    )

        return recommendations

# ==================== Pattern Recognition ====================

class PatternRecognizer:
    """Recognize common IPC patterns and anti-patterns"""

    def __init__(self):
        self.known_patterns = {
            'request_response': self._detect_request_response,
            'publish_subscribe': self._detect_pub_sub,
            'pipeline': self._detect_pipeline,
            'circular_dependency': self._detect_circular,
            'star_topology': self._detect_star
        }

    def detect_all_patterns(self, messages: List, processes: Dict) -> Dict:
        """Detect all known patterns in IPC communications"""
        detected = {}

        for pattern_name, detector in self.known_patterns.items():
            result = detector(messages, processes)
            if result:
                detected[pattern_name] = result

        return detected

    def _detect_request_response(self, messages: List, processes: Dict) -> Dict:
        """Detect request-response pattern"""
        pairs = defaultdict(list)

        for msg in messages:
            pairs[(msg.source_pid, msg.dest_pid)].append(msg.timestamp)

        request_response_pairs = []
        for (source, dest), timestamps in pairs.items():
            # Check if there are responses back
            if (dest, source) in pairs:
                request_response_pairs.append({
                    'client': source,
                    'server': dest,
                    'requests': len(timestamps),
                    'responses': len(pairs[(dest, source)])
                })

        return request_response_pairs if request_response_pairs else None

    def _detect_pub_sub(self, messages: List, processes: Dict) -> Dict:
        """Detect publish-subscribe pattern"""
        publishers = defaultdict(set)

        for msg in messages:
            # A publisher sends to multiple receivers
            publishers[msg.source_pid].add(msg.dest_pid)

        pub_sub_candidates = []
        for publisher, subscribers in publishers.items():
            if len(subscribers) >= 3:  # Publisher with 3+ subscribers
                pub_sub_candidates.append({
                    'publisher': publisher,
                    'subscribers': list(subscribers),
                    'subscriber_count': len(subscribers)
                })

        return pub_sub_candidates if pub_sub_candidates else None

    def _detect_pipeline(self, messages: List, processes: Dict) -> Dict:
        """Detect pipeline pattern (A->B->C->...)"""
        chains = defaultdict(list)

        for msg in messages:
            chains[msg.source_pid].append(msg.dest_pid)

        # Look for linear chains
        pipelines = []
        visited = set()

        for start_pid in chains:
            if start_pid not in visited:
                chain = [start_pid]
                current = start_pid

                while current in chains and len(chains[current]) == 1:
                    next_pid = chains[current][0]
                    if next_pid in chain:  # Avoid cycles
                        break
                    chain.append(next_pid)
                    visited.add(next_pid)
                    current = next_pid

                if len(chain) >= 3:  # Pipeline of at least 3 processes
                    pipelines.append({
                        'stages': chain,
                        'length': len(chain)
                    })

        return pipelines if pipelines else None

    def _detect_circular(self, messages: List, processes: Dict) -> Dict:
        """Detect circular dependencies"""
        graph = defaultdict(set)

        for msg in messages:
            graph[msg.source_pid].add(msg.dest_pid)

        def has_cycle_from(node, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph[node]:
                if neighbor not in visited:
                    if has_cycle_from(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        cycles = []
        visited = set()

        for node in graph:
            if node not in visited:
                rec_stack = set()
                if has_cycle_from(node, visited, rec_stack):
                    cycles.append({'process': node})

        return cycles if cycles else None

    def _detect_star(self, messages: List, processes: Dict) -> Dict:
        """Detect star topology (central hub)"""
        connection_counts = defaultdict(int)

        for msg in messages:
            connection_counts[msg.source_pid] += 1
            connection_counts[msg.dest_pid] += 1

        if not connection_counts:
            return None

        # Find processes with significantly more connections
        avg_connections = statistics.mean(connection_counts.values())
        hubs = []

        for pid, count in connection_counts.items():
            if count > avg_connections * 2:  # Hub has 2x average connections
                hubs.append({
                    'hub_pid': pid,
                    'connection_count': count,
                    'ratio': count / avg_connections
                })

        return hubs if hubs else None

# ==================== Visualization Components ====================

class IPCVisualizer:
    """Advanced visualization for IPC data"""

    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.figure = None
        self.canvas = None

    def create_performance_chart(self, data: Dict) -> FigureCanvasTkAgg:
        """Create performance metrics chart"""
        import matplotlib.pyplot as plt
        from matplotlib.figure import Figure

        fig = Figure(figsize=(10, 6))

        # Create subplots
        ax1 = fig.add_subplot(2, 2, 1)
        ax2 = fig.add_subplot(2, 2, 2)
        ax3 = fig.add_subplot(2, 2, 3)
        ax4 = fig.add_subplot(2, 2, 4)

        # Latency distribution
        if 'latencies' in data:
            ax1.hist(data['latencies'], bins=30, color='blue', alpha=0.7)
            ax1.set_title('Latency Distribution')
            ax1.set_xlabel('Latency (ms)')
            ax1.set_ylabel('Frequency')

        # Throughput over time
        if 'throughput' in data:
            ax2.plot(data['throughput']['times'], data['throughput']['values'],
                    color='green', linewidth=2)
            ax2.set_title('Throughput Over Time')
            ax2.set_xlabel('Time')
            ax2.set_ylabel('Messages/sec')

        # Process CPU usage
        if 'cpu_usage' in data:
            processes = list(data['cpu_usage'].keys())[:10]  # Top 10
            cpu_values = [data['cpu_usage'][p] for p in processes]
            ax3.bar(range(len(processes)), cpu_values, color='orange')
            ax3.set_title('Process CPU Usage')
            ax3.set_xlabel('Process')
            ax3.set_ylabel('CPU %')
            ax3.set_xticks(range(len(processes)))
            ax3.set_xticklabels([str(p)[:5] for p in processes], rotation=45)

        # IPC Method distribution
        if 'method_distribution' in data:
            methods = list(data['method_distribution'].keys())
            counts = list(data['method_distribution'].values())
            ax4.pie(counts, labels=methods, autopct='%1.1f%%', startangle=90)
            ax4.set_title('IPC Method Distribution')

        fig.tight_layout()

        # Create canvas
        canvas = FigureCanvasTkAgg(fig, master=self.parent)
        canvas.draw()

        return canvas

    def create_network_graph(self, processes: Dict, messages: List):
        """Create interactive network graph of process communications"""
        try:
            import networkx as nx
            from matplotlib.figure import Figure

            # Create directed graph
            G = nx.DiGraph()

            # Add nodes (processes)
            for pid, process in processes.items():
                G.add_node(pid, label=process.name,
                          cpu=process.cpu_percent,
                          memory=process.memory_mb)

            # Add edges (communications)
            edge_weights = defaultdict(int)
            for msg in messages:
                edge_weights[(msg.source_pid, msg.dest_pid)] += 1

            for (source, dest), weight in edge_weights.items():
                G.add_edge(source, dest, weight=weight)

            # Create figure
            fig = Figure(figsize=(12, 8))
            ax = fig.add_subplot(111)

            # Calculate layout
            pos = nx.spring_layout(G, k=2, iterations=50)

            # Draw nodes
            node_sizes = [processes[node].cpu_percent * 100 for node in G.nodes()]
            node_colors = ['red' if processes[node].state.value == "Blocked" else 'green'
                          for node in G.nodes()]

            nx.draw_networkx_nodes(G, pos, node_size=node_sizes,
                                  node_color=node_colors, alpha=0.7, ax=ax)

            # Draw edges
            edge_widths = [edge_weights[(u, v)] / 10 for u, v in G.edges()]
            nx.draw_networkx_edges(G, pos, width=edge_widths,
                                  alpha=0.5, arrows=True, ax=ax)

            # Draw labels
            labels = {node: f"{node}\n{processes[node].name[:10]}"
                     for node in G.nodes()}
            nx.draw_networkx_labels(G, pos, labels, font_size=8, ax=ax)

            ax.set_title("Process Communication Network")
            ax.axis('off')

            # Create canvas
            canvas = FigureCanvasTkAgg(fig, master=self.parent)
            canvas.draw()

            return canvas

        except ImportError:
            print("NetworkX not installed. Install with: pip install networkx")
            return None

# ==================== Report Generator ====================

class ReportGenerator:
    """Generate detailed analysis reports"""

    def __init__(self):
        self.report_sections = []

    def generate_html_report(self, monitor_data: Dict, analysis_results: Dict) -> str:
        """Generate comprehensive HTML report"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>IPC Analysis Report</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }
                h1 {
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                }
                h2 {
                    color: #34495e;
                    margin-top: 30px;
                }
                .summary {
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin: 20px 0;
                }
                .metric {
                    display: inline-block;
                    margin: 10px 20px;
                    padding: 10px;
                    background: #ecf0f1;
                    border-radius: 5px;
                }
                .warning {
                    background: #f39c12;
                    color: white;
                    padding: 10px;
                    border-radius: 5px;
                    margin: 10px 0;
                }
                .success {
                    background: #27ae60;
                    color: white;
                    padding: 10px;
                    border-radius: 5px;
                    margin: 10px 0;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    background: white;
                    margin: 20px 0;
                }
                th, td {
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }
                th {
                    background-color: #3498db;
                    color: white;
                }
                tr:hover {
                    background-color: #f5f5f5;
                }
                .chart {
                    margin: 20px 0;
                    padding: 20px;
                    background: white;
                    border-radius: 8px;
                }
                .recommendation {
                    background: #e8f8f5;
                    border-left: 4px solid #27ae60;
                    padding: 15px;
                    margin: 10px 0;
                }
            </style>
        </head>
        <body>
        """

        # Report header
        html += f"""
        <h1>IPC Analysis Report</h1>
        <div class="summary">
            <h2>Executive Summary</h2>
            <p>Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        """

        # Key metrics
        if 'statistics' in monitor_data:
            stats = monitor_data['statistics']
            html += """
            <div class="metrics">
                <h3>Key Metrics</h3>
            """
            for key, value in stats.items():
                html += f'<div class="metric"><strong>{key}:</strong> {value}</div>'
            html += "</div>"

        html += "</div>"

        # Performance Analysis
        if 'latency_analysis' in analysis_results:
            html += self._create_latency_section(analysis_results['latency_analysis'])

        # Bottlenecks
        if 'bottlenecks' in analysis_results:
            html += self._create_bottleneck_section(analysis_results['bottlenecks'])

        # Patterns
        if 'patterns' in analysis_results:
            html += self._create_patterns_section(analysis_results['patterns'])

        # Recommendations
        if 'recommendations' in analysis_results:
            html += self._create_recommendations_section(analysis_results['recommendations'])

        # Process Details
        if 'processes' in monitor_data:
            html += self._create_process_table(monitor_data['processes'])

        # Communication Log
        if 'recent_messages' in monitor_data:
            html += self._create_communication_log(monitor_data['recent_messages'])

        html += """
        </body>
        </html>
        """

        return html

    def _create_latency_section(self, latency_data: Dict) -> str:
        """Create latency analysis section"""
        html = """
        <div class="summary">
            <h2>Latency Analysis</h2>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
        """

        for key, value in latency_data.items():
            if key != 'outliers':
                html += f"""
                <tr>
                    <td>{key.replace('_', ' ').title()}</td>
                    <td>{value:.2f} ms</td>
                </tr>
                """

        html += "</table>"

        if latency_data.get('outliers'):
            html += f"""
            <div class="warning">
                ⚠️ Detected {len(latency_data['outliers'])} outlier(s) in latency measurements
            </div>
            """

        html += "</div>"
        return html

    def _create_bottleneck_section(self, bottlenecks: List) -> str:
        """Create bottleneck section"""
        if not bottlenecks:
            return ""

        html = """
        <div class="summary">
            <h2>Detected Bottlenecks</h2>
        """

        for bottleneck in bottlenecks:
            severity_class = 'warning' if bottleneck['severity'] == 'high' else 'success'
            html += f"""
            <div class="{severity_class}">
                <strong>{bottleneck['type'].replace('_', ' ').title()}</strong><br>
                Process PID: {bottleneck['process_pid']}<br>
                Severity: {bottleneck['severity'].upper()}
            </div>
            """

        html += "</div>"
        return html

    def _create_patterns_section(self, patterns: Dict) -> str:
        """Create patterns section"""
        html = """
        <div class="summary">
            <h2>Communication Patterns</h2>
        """

        if 'frequent_pairs' in patterns:
            html += "<h3>Most Frequent Communications</h3><ul>"
            for (source, dest), count in list(patterns['frequent_pairs'].most_common(5)):
                html += f"<li>Process {source} → Process {dest}: {count} messages</li>"
            html += "</ul>"

        if 'peak_times' in patterns and patterns['peak_times']:
            html += "<h3>Peak Communication Times</h3><ul>"
            for peak_time in patterns['peak_times'][:5]:
                html += f"<li>{peak_time.strftime('%H:%M')}</li>"
            html += "</ul>"

        html += "</div>"
        return html

    def _create_recommendations_section(self, recommendations: List) -> str:
        """Create recommendations section"""
        if not recommendations:
            return ""

        html = """
        <div class="summary">
            <h2>Recommendations</h2>
        """

        for rec in recommendations:
            html += f'<div class="recommendation">{rec}</div>'

        html += "</div>"
        return html

    def _create_process_table(self, processes: Dict) -> str:
        """Create process details table"""
        html = """
        <div class="summary">
            <h2>Process Details</h2>
            <table>
                <tr>
                    <th>PID</th>
                    <th>Name</th>
                    <th>State</th>
                    <th>CPU %</th>
                    <th>Memory (MB)</th>
                    <th>Connections</th>
                </tr>
        """

        for pid, process in list(processes.items())[:20]:  # Limit to 20 processes
            html += f"""
            <tr>
                <td>{pid}</td>
                <td>{process.name}</td>
                <td>{process.state.value}</td>
                <td>{process.cpu_percent:.1f}</td>
                <td>{process.memory_mb:.1f}</td>
                <td>{len(process.ipc_connections)}</td>
            </tr>
            """

        html += """
            </table>
        </div>
        """
        return html

    def _create_communication_log(self, messages: List) -> str:
        """Create communication log table"""
        html = """
        <div class="summary">
            <h2>Recent Communications</h2>
            <table>
                <tr>
                    <th>Timestamp</th>
                    <th>Source</th>
                    <th>Target</th>
                    <th>Method</th>
                    <th>Size</th>
                    <th>Latency</th>
                    <th>Status</th>
                </tr>
        """

        for msg in messages[:50]:  # Last 50 messages
            status_class = 'success' if msg.status == 'Success' else 'warning'
            html += f"""
            <tr>
                <td>{msg.timestamp.strftime('%H:%M:%S.%f')[:-3]}</td>
                <td>{msg.source_pid}</td>
                <td>{msg.dest_pid}</td>
                <td>{msg.method.value}</td>
                <td>{msg.data_size} B</td>
                <td>{msg.latency_ms:.2f} ms</td>
                <td><span class="{status_class}">{msg.status}</span></td>
            </tr>
            """

        html += """
            </table>
        </div>
        """
        return html

    def save_report(self, html_content: str, filename: str):
        """Save HTML report to file"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Report saved to: {filename}")

# ==================== Main Application Entry ====================

if __name__ == "__main__":
    print("""
    IPC Debugger - Advanced Features Module
    ========================================
    Professional IPC Analysis & Debugging Tool
    """)

    # This module is imported by the main IPC debugger
    print("Advanced features module loaded successfully.")
