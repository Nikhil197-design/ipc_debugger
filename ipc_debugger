"""
=================================================================
    IPC DEBUGGER - Complete Implementation
    A Professional Tool for Inter-Process Communication Debugging
    Version: 2.0 | Python 3.8+
=================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import multiprocessing
from multiprocessing import Process, Queue, Pipe, Value, Array, Manager
import queue
import time
import os
import sys
import json
import socket
import pickle
import math
from datetime import datetime, timedelta
from collections import deque, defaultdict
import random
import psutil  # For process monitoring
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== Constants & Configuration ====================

class Config:
    """Configuration constants"""
    REFRESH_RATE = 100  # milliseconds
    MAX_LOG_ENTRIES = 1000
    DEADLOCK_CHECK_INTERVAL = 2  # seconds
    PERFORMANCE_SAMPLE_SIZE = 100
    GUI_WIDTH = 1400
    GUI_HEIGHT = 800

    # Colors for GUI
    COLOR_ACTIVE = "#2ECC71"
    COLOR_BLOCKED = "#E74C3C"
    COLOR_WAITING = "#F39C12"
    COLOR_NORMAL = "#3498DB"

# ==================== Data Models ====================

class IPCMethod(Enum):
    """IPC communication methods"""
    PIPE = "Pipe"
    QUEUE = "Message Queue"
    SHARED_MEMORY = "Shared Memory"
    SOCKET = "Socket"
    SIGNAL = "Signal"

class ProcessState(Enum):
    """Process states"""
    RUNNING = "Running"
    BLOCKED = "Blocked"
    WAITING = "Waiting"
    READY = "Ready"
    TERMINATED = "Terminated"

@dataclass
class ProcessNode:
    """Represents a process in the system"""
    pid: int
    name: str
    state: ProcessState
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    threads: int = 1
    created_time: datetime = field(default_factory=datetime.now)
    parent_pid: Optional[int] = None
    children_pids: List[int] = field(default_factory=list)
    ipc_connections: Dict[int, IPCMethod] = field(default_factory=dict)

@dataclass
class IPCMessage:
    """Represents an IPC message"""
    id: str
    timestamp: datetime
    source_pid: int
    dest_pid: int
    method: IPCMethod
    data_size: int
    data: Any
    latency_ms: float = 0.0
    status: str = "Success"

@dataclass
class PerformanceMetrics:
    """Performance metrics for IPC"""
    throughput: float = 0.0  # messages per second
    avg_latency: float = 0.0  # milliseconds
    max_latency: float = 0.0
    min_latency: float = float('inf')
    total_messages: int = 0
    total_bytes: int = 0
    error_rate: float = 0.0

# ==================== IPC Simulators ====================

class IPCSimulator(ABC):
    """Abstract base class for IPC simulators"""

    @abstractmethod
    def send(self, data: Any) -> bool:
        pass

    @abstractmethod
    def receive(self) -> Any:
        pass

    @abstractmethod
    def get_stats(self) -> dict:
        pass

class PipeSimulator(IPCSimulator):
    """Simulates pipe communication"""

    def __init__(self, name="Pipe"):
        self.name = name
        self.parent_conn, self.child_conn = Pipe()
        self.message_count = 0+
        self.total_bytes = 0
        self.errors = 0

    def send(self, data: Any) -> bool:
        try:
            self.parent_conn.send(data)
            self.message_count += 1
            self.total_bytes += sys.getsizeof(data)
            return True
        except Exception as e:
            self.errors += 1
            logger.error(f"Pipe send error: {e}")
            return False

    def receive(self) -> Any:
        try:
            if self.child_conn.poll(timeout=0.1):
                return self.child_conn.recv()
        except Exception as e:
            self.errors += 1
            logger.error(f"Pipe receive error: {e}")
        return None

    def get_stats(self) -> dict:
        return {
            'messages': self.message_count,
            'bytes': self.total_bytes,
            'errors': self.errors
        }

class QueueSimulator(IPCSimulator):
    """Simulates message queue communication"""

    def __init__(self, name="Queue"):
        self.name = name
        self.queue = multiprocessing.Queue()
        self.message_count = 0
        self.total_bytes = 0
        self.errors = 0

    def send(self, data: Any) -> bool:
        try:
            self.queue.put(data, timeout=1)
            self.message_count += 1
            self.total_bytes += sys.getsizeof(data)
            return True
        except Exception as e:
            self.errors += 1
            logger.error(f"Queue send error: {e}")
            return False

    def receive(self) -> Any:
        try:
            return self.queue.get(timeout=0.1)
        except queue.Empty:
            return None
        except Exception as e:
            self.errors += 1
            logger.error(f"Queue receive error: {e}")
            return None

    def get_stats(self) -> dict:
        return {
            'messages': self.message_count,
            'bytes': self.total_bytes,
            'errors': self.errors,
            'queue_size': self.queue.qsize()
        }

class SharedMemorySimulator(IPCSimulator):
    """Simulates shared memory communication"""

    def __init__(self, name="SharedMem"):
        self.name = name
        manager = Manager()
        self.shared_dict = manager.dict()
        self.shared_list = manager.list()
        self.lock = manager.Lock()
        self.access_count = 0
        self.errors = 0

    def send(self, data: Any) -> bool:
        try:
            with self.lock:
                key = f"msg_{self.access_count}"
                self.shared_dict[key] = data
                self.shared_list.append(key)
                self.access_count += 1
            return True
        except Exception as e:
            self.errors += 1
            logger.error(f"SharedMemory write error: {e}")
            return False

    def receive(self) -> Any:
        try:
            with self.lock:
                if self.shared_list:
                    key = self.shared_list.pop(0)
                    return self.shared_dict.pop(key, None)
        except Exception as e:
            self.errors += 1
            logger.error(f"SharedMemory read error: {e}")
        return None

    def get_stats(self) -> dict:
        return {
            'accesses': self.access_count,
            'errors': self.errors,
            'items_in_memory': len(self.shared_dict)
        }

# ==================== Deadlock Detector ====================

class DeadlockDetector:
    """Detects deadlocks in IPC operations"""

    def __init__(self):
        self.resource_allocation = defaultdict(set)  # resource -> processes
        self.process_waiting = defaultdict(set)  # process -> resources
        self.lock = threading.Lock()

    def request_resource(self, process_id: int, resource_id: str):
        """Process requests a resource"""
        with self.lock:
            self.process_waiting[process_id].add(resource_id)

    def acquire_resource(self, process_id: int, resource_id: str):
        """Process acquires a resource"""
        with self.lock:
            self.resource_allocation[resource_id].add(process_id)
            self.process_waiting[process_id].discard(resource_id)

    def release_resource(self, process_id: int, resource_id: str):
        """Process releases a resource"""
        with self.lock:
            self.resource_allocation[resource_id].discard(process_id)

    def detect_deadlock(self) -> List[int]:
        """Detect deadlock using cycle detection algorithm"""
        with self.lock:
            # Build wait-for graph
            wait_for_graph = defaultdict(set)

            for process, resources in self.process_waiting.items():
                for resource in resources:
                    holders = self.resource_allocation.get(resource, set())
                    for holder in holders:
                        if holder != process:
                            wait_for_graph[process].add(holder)

            # Detect cycle using DFS
            def has_cycle(node, visited, rec_stack):
                visited.add(node)
                rec_stack.add(node)

                for neighbor in wait_for_graph.get(node, []):
                    if neighbor not in visited:
                        if has_cycle(neighbor, visited, rec_stack):
                            return True
                    elif neighbor in rec_stack:
                        return True

                rec_stack.remove(node)
                return False

            visited = set()
            rec_stack = set()
            deadlocked_processes = []

            for node in wait_for_graph:
                if node not in visited:
                    if has_cycle(node, visited, rec_stack):
                        deadlocked_processes.append(node)

            return deadlocked_processes

# ==================== IPC Monitor Core ====================

class IPCMonitor:
    """Main IPC monitoring and analysis engine"""

    def __init__(self):
        self.processes = {}
        self.messages = deque(maxlen=Config.MAX_LOG_ENTRIES)
        self.performance_metrics = PerformanceMetrics()
        self.deadlock_detector = DeadlockDetector()
        self.is_monitoring = False
        self.monitor_thread = None
        self.lock = threading.Lock()

        # IPC simulators
        self.ipc_simulators = {
            IPCMethod.PIPE: PipeSimulator(),
            IPCMethod.QUEUE: QueueSimulator(),
            IPCMethod.SHARED_MEMORY: SharedMemorySimulator()
        }

        # Performance tracking
        self.latency_samples = deque(maxlen=Config.PERFORMANCE_SAMPLE_SIZE)
        self.throughput_window = deque(maxlen=60)  # Last 60 seconds

    def start_monitoring(self):
        """Start monitoring IPC activities"""
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("IPC monitoring started")

    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        logger.info("IPC monitoring stopped")

    def _monitor_loop(self):
        """Main monitoring loop"""
        last_deadlock_check = time.time()

        while self.is_monitoring:
            try:
                # Update process information
                self._update_processes()

                # Check for deadlocks periodically
                if time.time() - last_deadlock_check > Config.DEADLOCK_CHECK_INTERVAL:
                    self._check_deadlocks()
                    last_deadlock_check = time.time()

                # Update performance metrics
                self._update_performance_metrics()

                time.sleep(0.1)

            except Exception as e:
                logger.error(f"Monitor loop error: {e}")

    def _update_processes(self):
        """Update process information"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                pid = proc.info['pid']

                with self.lock:
                    if pid not in self.processes:
                        self.processes[pid] = ProcessNode(
                            pid=pid,
                            name=proc.info['name'],
                            state=ProcessState.RUNNING,
                            cpu_percent=proc.info['cpu_percent'] or 0,
                            memory_mb=proc.info['memory_info'].rss / 1024 / 1024 if proc.info['memory_info'] else 0
                        )
                    else:
                        self.processes[pid].cpu_percent = proc.info['cpu_percent'] or 0
                        self.processes[pid].memory_mb = proc.info['memory_info'].rss / 1024 / 1024 if proc.info['memory_info'] else 0

        except Exception as e:
            logger.error(f"Process update error: {e}")

    def _check_deadlocks(self):
        """Check for potential deadlocks"""
        deadlocked = self.deadlock_detector.detect_deadlock()
        if deadlocked:
            logger.warning(f"Deadlock detected involving processes: {deadlocked}")
            self.performance_metrics.error_rate += 1

    def _update_performance_metrics(self):
        """Update performance metrics"""
        with self.lock:
            if self.latency_samples:
                self.performance_metrics.avg_latency = sum(self.latency_samples) / len(self.latency_samples)
                self.performance_metrics.max_latency = max(self.latency_samples)
                self.performance_metrics.min_latency = min(self.latency_samples)

            # Calculate throughput
            current_time = time.time()
            self.throughput_window.append((current_time, self.performance_metrics.total_messages))
            if len(self.throughput_window) > 1:
                time_diff = self.throughput_window[-1][0] - self.throughput_window[0][0]
                msg_diff = self.throughput_window[-1][1] - self.throughput_window[0][1]
                if time_diff > 0:
                    self.performance_metrics.throughput = msg_diff / time_diff

    def send_message(self, source_pid: int, dest_pid: int, method: IPCMethod, data: Any):
        """Simulate sending an IPC message"""
        start_time = time.time()

        message = IPCMessage(
            id=f"{source_pid}_{dest_pid}_{int(time.time()*1000)}",
            timestamp=datetime.now(),
            source_pid=source_pid,
            dest_pid=dest_pid,
            method=method,
            data_size=sys.getsizeof(data),
            data=data
        )

        # Simulate sending through appropriate method
        simulator = self.ipc_simulators.get(method)
        if simulator:
            success = simulator.send(data)
            message.status = "Success" if success else "Failed"

        # Calculate latency
        message.latency_ms = (time.time() - start_time) * 1000

        # Update metrics
        with self.lock:
            self.messages.append(message)
            self.performance_metrics.total_messages += 1
            self.performance_metrics.total_bytes += message.data_size
            self.latency_samples.append(message.latency_ms)

            # Update process connections
            if source_pid in self.processes and dest_pid in self.processes:
                self.processes[source_pid].ipc_connections[dest_pid] = method

        return message

    def get_statistics(self) -> dict:
        """Get current statistics"""
        with self.lock:
            return {
                'total_processes': len(self.processes),
                'active_processes': sum(1 for p in self.processes.values() if p.state == ProcessState.RUNNING),
                'total_messages': self.performance_metrics.total_messages,
                'total_bytes': self.performance_metrics.total_bytes,
                'avg_latency': f"{self.performance_metrics.avg_latency:.2f} ms",
                'throughput': f"{self.performance_metrics.throughput:.2f} msg/s",
                'error_rate': f"{self.performance_metrics.error_rate:.2%}"
            }

# ==================== GUI Implementation ====================

class IPCDebuggerGUI:
    """Main GUI for IPC Debugger"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("IPC Debugger - Professional Tool")
        self.root.geometry(f"{Config.GUI_WIDTH}x{Config.GUI_HEIGHT}")

        # Apply modern theme
        self.root.configure(bg='#2C3E50')
        style = ttk.Style()
        style.theme_use('clam')

        # Initialize monitor
        self.monitor = IPCMonitor()

        # GUI state
        self.selected_process = None
        self.auto_refresh = tk.BooleanVar(value=True)

        # Build GUI
        self._create_menu()
        self._create_main_layout()
        self._create_status_bar()

        # Start monitoring
        self.monitor.start_monitoring()
        self._start_gui_refresh()

    def _create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root, bg='#34495E', fg='white')
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Logs", command=self._export_logs)
        file_menu.add_command(label="Load Session", command=self._load_session)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Monitor menu
        monitor_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Monitor", menu=monitor_menu)
        monitor_menu.add_command(label="Start Monitoring", command=self._start_monitoring)
        monitor_menu.add_command(label="Stop Monitoring", command=self._stop_monitoring)
        monitor_menu.add_command(label="Clear Logs", command=self._clear_logs)

        # Test menu
        test_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Test", menu=test_menu)
        test_menu.add_command(label="Simulate Pipe Communication", command=lambda: self._simulate_ipc(IPCMethod.PIPE))
        test_menu.add_command(label="Simulate Queue Communication", command=lambda: self._simulate_ipc(IPCMethod.QUEUE))
        test_menu.add_command(label="Simulate Shared Memory", command=lambda: self._simulate_ipc(IPCMethod.SHARED_MEMORY))
        test_menu.add_command(label="Simulate Deadlock", command=self._simulate_deadlock)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self._show_help)
        help_menu.add_command(label="About", command=self._show_about)

    def _create_main_layout(self):
        """Create main layout with panes"""
        # Main container
        main_container = ttk.PanedWindow(self.root, orient='horizontal')
        main_container.pack(fill='both', expand=True, padx=5, pady=5)

        # Left panel - Process list and controls
        left_panel = ttk.Frame(main_container)
        main_container.add(left_panel, weight=1)

        # Center panel - Visualization
        center_panel = ttk.Frame(main_container)
        main_container.add(center_panel, weight=2)

        # Right panel - Details and logs
        right_panel = ttk.Frame(main_container)
        main_container.add(right_panel, weight=1)

        # === LEFT PANEL ===
        self._create_process_list(left_panel)
        self._create_controls(left_panel)

        # === CENTER PANEL ===
        self._create_visualization(center_panel)
        self._create_statistics(center_panel)

        # === RIGHT PANEL ===
        self._create_details_view(right_panel)
        self._create_log_view(right_panel)

    def _create_process_list(self, parent):
        """Create process list view"""
        frame = ttk.LabelFrame(parent, text="Processes", padding=10)
        frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Treeview for process list
        columns = ('PID', 'Name', 'State', 'CPU%', 'Memory')
        self.process_tree = ttk.Treeview(frame, columns=columns, show='tree headings', height=15)

        # Configure columns
        self.process_tree.heading('#0', text='')
        self.process_tree.column('#0', width=0, stretch=False)

        for col in columns:
            self.process_tree.heading(col, text=col)
            self.process_tree.column(col, width=60 if col in ['PID', 'CPU%'] else 80)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=scrollbar.set)

        self.process_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Bind selection
        self.process_tree.bind('<<TreeviewSelect>>', self._on_process_select)

    def _create_controls(self, parent):
        """Create control buttons"""
        frame = ttk.LabelFrame(parent, text="Controls", padding=10)
        frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(frame, text="Refresh", command=self._refresh_processes).pack(side='left', padx=2)
        ttk.Button(frame, text="Filter", command=self._show_filter_dialog).pack(side='left', padx=2)
        ttk.Checkbutton(frame, text="Auto Refresh", variable=self.auto_refresh).pack(side='left', padx=5)

    def _create_visualization(self, parent):
        """Create visualization canvas"""
        frame = ttk.LabelFrame(parent, text="IPC Visualization", padding=10)
        frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(frame, bg='#1A1A2E', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

        # Process nodes storage
        self.node_positions = {}
        self.node_items = {}

    def _create_statistics(self, parent):
        """Create statistics display"""
        frame = ttk.LabelFrame(parent, text="Performance Metrics", padding=10)
        frame.pack(fill='x', padx=5, pady=5)

        self.stats_text = tk.Text(frame, height=4, bg='#2C3E50', fg='white', font=('Consolas', 10))
        self.stats_text.pack(fill='x')

    def _create_details_view(self, parent):
        """Create detailed view for selected process"""
        frame = ttk.LabelFrame(parent, text="Process Details", padding=10)
        frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.details_text = scrolledtext.ScrolledText(
            frame, height=10, bg='#2C3E50', fg='white', font=('Consolas', 9)
        )
        self.details_text.pack(fill='both', expand=True)

    def _create_log_view(self, parent):
        """Create log viewer"""
        frame = ttk.LabelFrame(parent, text="Communication Logs", padding=10)
        frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Log tree view
        columns = ('Time', 'Source', 'Target', 'Method', 'Size', 'Latency', 'Status')
        self.log_tree = ttk.Treeview(frame, columns=columns, show='headings', height=10)

        for col in columns:
            self.log_tree.heading(col, text=col)
            self.log_tree.column(col, width=70)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(frame, orient='vertical', command=self.log_tree.yview)
        h_scrollbar = ttk.Scrollbar(frame, orient='horizontal', command=self.log_tree.xview)
        self.log_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.log_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

    def _create_status_bar(self):
        """Create status bar"""
        self.status_bar = ttk.Label(
            self.root, text="Ready", relief='sunken', anchor='w'
        )
        self.status_bar.pack(side='bottom', fill='x')

    # ==================== GUI Update Methods ====================

    def _start_gui_refresh(self):
        """Start automatic GUI refresh"""
        if self.auto_refresh.get():
            self._refresh_all()
        self.root.after(Config.REFRESH_RATE, self._start_gui_refresh)

    def _refresh_all(self):
        """Refresh all GUI components"""
        self._refresh_processes()
        self._refresh_visualization()
        self._refresh_statistics()
        self._refresh_logs()

    def _refresh_processes(self):
        """Refresh process list"""
        # Clear existing items
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)

        # Add processes (make a copy to avoid dictionary changing during iteration)
        with self.monitor.lock:
            processes_copy = dict(self.monitor.processes)

        for pid, process in processes_copy.items():
            color_tag = self._get_state_color_tag(process.state)
            self.process_tree.insert('', 'end', values=(
                pid,
                process.name[:20],
                process.state.value,
                f"{process.cpu_percent:.1f}",
                f"{process.memory_mb:.1f}M"
            ), tags=(color_tag,))

        # Configure tags
        self.process_tree.tag_configure('running', foreground=Config.COLOR_ACTIVE)
        self.process_tree.tag_configure('blocked', foreground=Config.COLOR_BLOCKED)
        self.process_tree.tag_configure('waiting', foreground=Config.COLOR_WAITING)

    def _refresh_visualization(self):
        """Refresh visualization canvas"""
        self.canvas.delete('all')

        with self.monitor.lock:
            has_processes = bool(self.monitor.processes)

        if not has_processes:
            return

        # Calculate positions for processes
        self._calculate_node_positions()

        # Draw connections first (so they appear behind nodes)
        self._draw_connections()

        # Draw process nodes
        self._draw_process_nodes()

        # Draw active communications
        self._draw_active_communications()

    def _calculate_node_positions(self):
        """Calculate positions for process nodes in a circle"""
        self.node_positions.clear()

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1:  # Canvas not yet rendered
            return

        center_x = canvas_width / 2
        center_y = canvas_height / 2
        radius = min(canvas_width, canvas_height) * 0.35

        with self.monitor.lock:
            processes = list(self.monitor.processes.values())
        num_processes = len(processes)

        if num_processes == 0:
            return

        angle_step = 2 * 3.14159 / num_processes

        for i, process in enumerate(processes):
            angle = i * angle_step
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.node_positions[process.pid] = (x, y)

    def _draw_process_nodes(self):
        """Draw process nodes on canvas"""
        import math

        self.node_items.clear()

        with self.monitor.lock:
            processes_copy = dict(self.monitor.processes)

        for pid, (x, y) in self.node_positions.items():
            process = processes_copy.get(pid)
            if not process:
                continue

            # Determine color based on state
            color = self._get_state_color(process.state)

            # Draw node circle
            node_size = 30 + min(process.cpu_percent, 50) / 2  # Size based on CPU usage
            node = self.canvas.create_oval(
                x - node_size, y - node_size,
                x + node_size, y + node_size,
                fill=color, outline='white', width=2
            )

            # Draw PID text
            text = self.canvas.create_text(
                x, y, text=str(pid), fill='white', font=('Arial', 10, 'bold')
            )

            # Draw process name below
            name_text = self.canvas.create_text(
                x, y + node_size + 10,
                text=process.name[:15],
                fill='white',
                font=('Arial', 8)
            )

            self.node_items[pid] = (node, text, name_text)

            # Bind click event
            for item in (node, text, name_text):
                self.canvas.tag_bind(item, '<Button-1>', lambda e, p=pid: self._on_node_click(p))

    def _draw_connections(self):
        """Draw IPC connections between processes"""
        drawn_connections = set()

        with self.monitor.lock:
            processes_copy = dict(self.monitor.processes)

        for pid, process in processes_copy.items():
            if pid not in self.node_positions:
                continue

            for target_pid, method in process.ipc_connections.items():
                if target_pid not in self.node_positions:
                    continue

                # Avoid drawing duplicate connections
                connection_key = tuple(sorted([pid, target_pid]))
                if connection_key in drawn_connections:
                    continue
                drawn_connections.add(connection_key)

                # Get positions
                x1, y1 = self.node_positions[pid]
                x2, y2 = self.node_positions[target_pid]

                # Draw connection line
                color = self._get_method_color(method)
                line = self.canvas.create_line(
                    x1, y1, x2, y2,
                    fill=color, width=2, dash=(5, 3),
                    arrow='last', arrowshape=(10, 12, 5)
                )

                # Draw method label
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2
                self.canvas.create_text(
                    mid_x, mid_y,
                    text=method.value,
                    fill='yellow',
                    font=('Arial', 8),
                    anchor='center'
                )

    def _draw_active_communications(self):
        """Draw animated active communications"""
        recent_messages = list(self.monitor.messages)[-10:]  # Last 10 messages

        for msg in recent_messages:
            if msg.source_pid not in self.node_positions or msg.dest_pid not in self.node_positions:
                continue

            # Calculate animation position based on time
            elapsed = (datetime.now() - msg.timestamp).total_seconds()
            if elapsed > 2:  # Animation lasts 2 seconds
                continue

            progress = elapsed / 2.0

            x1, y1 = self.node_positions[msg.source_pid]
            x2, y2 = self.node_positions[msg.dest_pid]

            # Interpolate position
            curr_x = x1 + (x2 - x1) * progress
            curr_y = y1 + (y2 - y1) * progress

            # Draw moving packet
            self.canvas.create_oval(
                curr_x - 5, curr_y - 5,
                curr_x + 5, curr_y + 5,
                fill='yellow', outline='orange', width=2
            )

    def _refresh_statistics(self):
        """Refresh statistics display"""
        stats = self.monitor.get_statistics()

        self.stats_text.delete(1.0, tk.END)
        stats_str = f"""
Active Processes: {stats['active_processes']}/{stats['total_processes']}
Total Messages: {stats['total_messages']} | Data: {stats['total_bytes']} bytes
Average Latency: {stats['avg_latency']} | Throughput: {stats['throughput']}
Error Rate: {stats['error_rate']}
"""
        self.stats_text.insert(1.0, stats_str)

    def _refresh_logs(self):
        """Refresh communication logs"""
        # Clear existing logs
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)

        # Add recent messages
        for msg in list(self.monitor.messages)[-50:]:  # Last 50 messages
            self.log_tree.insert('', 0, values=(
                msg.timestamp.strftime('%H:%M:%S'),
                msg.source_pid,
                msg.dest_pid,
                msg.method.value,
                f"{msg.data_size}B",
                f"{msg.latency_ms:.2f}ms",
                msg.status
            ))

    # ==================== Event Handlers ====================

    def _on_process_select(self, event):
        """Handle process selection"""
        selection = self.process_tree.selection()
        if selection:
            item = self.process_tree.item(selection[0])
            pid = item['values'][0]
            self._show_process_details(pid)

    def _on_node_click(self, pid):
        """Handle node click in visualization"""
        self._show_process_details(pid)

    def _show_process_details(self, pid):
        """Show detailed information for a process"""
        with self.monitor.lock:
            process = self.monitor.processes.get(pid)
            processes_copy = dict(self.monitor.processes)

        if not process:
            return

        self.details_text.delete(1.0, tk.END)

        details = f"""
Process Information:
====================
PID: {process.pid}
Name: {process.name}
State: {process.state.value}
CPU Usage: {process.cpu_percent:.2f}%
Memory: {process.memory_mb:.2f} MB
Threads: {process.threads}
Created: {process.created_time.strftime('%Y-%m-%d %H:%M:%S')}

IPC Connections:
================
"""
        for target_pid, method in process.ipc_connections.items():
            target = processes_copy.get(target_pid)
            target_name = target.name if target else "Unknown"
            details += f"→ PID {target_pid} ({target_name}) via {method.value}\n"

        self.details_text.insert(1.0, details)

    # ==================== Simulation Methods ====================

    def _simulate_ipc(self, method: IPCMethod):
        """Simulate IPC communication"""
        processes = list(self.monitor.processes.keys())
        if len(processes) < 2:
            messagebox.showwarning("Warning", "Need at least 2 processes for simulation")
            return

        # Select random source and destination
        source_pid = random.choice(processes)
        dest_pid = random.choice([p for p in processes if p != source_pid])

        # Create test message
        test_data = {
            'type': 'test',
            'content': f"Test message from {source_pid} to {dest_pid}",
            'timestamp': datetime.now().isoformat()
        }

        # Send message
        msg = self.monitor.send_message(source_pid, dest_pid, method, test_data)

        self._update_status(f"Simulated {method.value} from PID {source_pid} to {dest_pid}")

    def _simulate_deadlock(self):
        """Simulate a deadlock scenario"""
        # Define deadlock functions locally (can't import due to multiprocessing)
        def process_a(lock1, lock2, shared_value):
            with lock1:
                time.sleep(0.1)
                with lock2:
                    pass

        def process_b(lock1, lock2, shared_value):
            with lock2:
                time.sleep(0.1)
                with lock1:
                    pass

        lock1 = multiprocessing.Lock()
        lock2 = multiprocessing.Lock()

        p1 = Process(target=process_a, args=(lock1, lock2, None))
        p2 = Process(target=process_b, args=(lock1, lock2, None))

        p1.start()
        p2.start()

        # Simulate deadlock detection
        self.monitor.deadlock_detector.request_resource(p1.pid, "lock1")
        self.monitor.deadlock_detector.request_resource(p2.pid, "lock2")
        time.sleep(0.1)
        self.monitor.deadlock_detector.request_resource(p1.pid, "lock2")
        self.monitor.deadlock_detector.request_resource(p2.pid, "lock1")

        # Check for deadlock
        deadlocked = self.monitor.deadlock_detector.detect_deadlock()
        if deadlocked:
            messagebox.showwarning("Deadlock Detected!", f"Processes {deadlocked} are in deadlock!")

        # Clean up
        p1.terminate()
        p2.terminate()
        p1.join()
        p2.join()

        self._update_status("Deadlock simulation completed")

    # ==================== Menu Actions ====================

    def _start_monitoring(self):
        """Start IPC monitoring"""
        self.monitor.start_monitoring()
        self._update_status("Monitoring started")

    def _stop_monitoring(self):
        """Stop IPC monitoring"""
        self.monitor.stop_monitoring()
        self._update_status("Monitoring stopped")

    def _clear_logs(self):
        """Clear all logs"""
        with self.monitor.lock:
            self.monitor.messages.clear()
        self._refresh_logs()
        self._update_status("Logs cleared")

    def _export_logs(self):
        """Export logs to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            try:
                logs = []
                for msg in self.monitor.messages:
                    logs.append({
                        'id': msg.id,
                        'timestamp': msg.timestamp.isoformat(),
                        'source_pid': msg.source_pid,
                        'dest_pid': msg.dest_pid,
                        'method': msg.method.value,
                        'data_size': msg.data_size,
                        'latency_ms': msg.latency_ms,
                        'status': msg.status
                    })

                with open(filename, 'w') as f:
                    json.dump(logs, f, indent=2)

                messagebox.showinfo("Success", f"Logs exported to {filename}")
                self._update_status(f"Logs exported: {filename}")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to export logs: {str(e)}")

    def _load_session(self):
        """Load a previous session"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)

                # Clear current data
                self.monitor.messages.clear()

                # Load messages
                for item in data:
                    msg = IPCMessage(
                        id=item['id'],
                        timestamp=datetime.fromisoformat(item['timestamp']),
                        source_pid=item['source_pid'],
                        dest_pid=item['dest_pid'],
                        method=IPCMethod(item['method']),
                        data_size=item['data_size'],
                        data=None,
                        latency_ms=item['latency_ms'],
                        status=item['status']
                    )
                    self.monitor.messages.append(msg)

                self._refresh_logs()
                messagebox.showinfo("Success", f"Session loaded from {filename}")
                self._update_status(f"Session loaded: {filename}")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to load session: {str(e)}")

    def _show_filter_dialog(self):
        """Show filter dialog"""
        dialog = FilterDialog(self.root, self.monitor)
        dialog.show()

    def _show_help(self):
        """Show help dialog"""
        help_text = """
IPC Debugger - User Guide
========================

Features:
---------
1. Process Monitoring: View all running processes with CPU and memory usage
2. IPC Visualization: See real-time communication between processes
3. Deadlock Detection: Automatically detect circular dependencies
4. Performance Metrics: Monitor throughput, latency, and error rates

How to Use:
-----------
1. Start monitoring from Monitor menu
2. Select a process to view details
3. Use Test menu to simulate different IPC methods
4. Check logs for communication history
5. Export logs for analysis

IPC Methods:
------------
• Pipe: One-directional data transfer (like water pipe)
• Message Queue: Messages in a queue (like WhatsApp messages)
• Shared Memory: Common storage (like shared Google Doc)
• Socket: Network communication (like video call)

Visualization:
--------------
• Green nodes: Running processes
• Red nodes: Blocked processes
• Yellow nodes: Waiting processes
• Arrows show communication direction
• Node size indicates CPU usage

Keyboard Shortcuts:
-------------------
Ctrl+S: Export logs
Ctrl+O: Load session
Ctrl+R: Refresh
F1: Show this help
"""
        help_window = tk.Toplevel(self.root)
        help_window.title("User Guide")
        help_window.geometry("600x500")

        text = scrolledtext.ScrolledText(help_window, wrap=tk.WORD)
        text.pack(fill='both', expand=True, padx=10, pady=10)
        text.insert(1.0, help_text)
        text.config(state='disabled')

        ttk.Button(help_window, text="Close", command=help_window.destroy).pack(pady=5)

    def _show_about(self):
        """Show about dialog"""
        about_text = """
IPC Debugger
Version 2.0

A professional tool for debugging and monitoring
Inter-Process Communication in real-time.

Features:
• Real-time process monitoring
• IPC visualization
• Deadlock detection
• Performance analysis
• Multiple IPC method support

Developed for developers and system administrators
to diagnose and optimize IPC operations.

© 2024 IPC Debug Team
"""
        messagebox.showinfo("About IPC Debugger", about_text)

    # ==================== Helper Methods ====================

    def _get_state_color(self, state: ProcessState) -> str:
        """Get color for process state"""
        color_map = {
            ProcessState.RUNNING: Config.COLOR_ACTIVE,
            ProcessState.BLOCKED: Config.COLOR_BLOCKED,
            ProcessState.WAITING: Config.COLOR_WAITING,
            ProcessState.READY: Config.COLOR_NORMAL,
            ProcessState.TERMINATED: '#95A5A6'
        }
        return color_map.get(state, Config.COLOR_NORMAL)

    def _get_state_color_tag(self, state: ProcessState) -> str:
        """Get color tag for tree view"""
        tag_map = {
            ProcessState.RUNNING: 'running',
            ProcessState.BLOCKED: 'blocked',
            ProcessState.WAITING: 'waiting',
            ProcessState.READY: 'normal',
            ProcessState.TERMINATED: 'terminated'
        }
        return tag_map.get(state, 'normal')

    def _get_method_color(self, method: IPCMethod) -> str:
        """Get color for IPC method"""
        color_map = {
            IPCMethod.PIPE: '#3498DB',
            IPCMethod.QUEUE: '#9B59B6',
            IPCMethod.SHARED_MEMORY: '#E67E22',
            IPCMethod.SOCKET: '#16A085'
        }
        return color_map.get(method, '#95A5A6')

    def _update_status(self, message: str):
        """Update status bar"""
        self.status_bar.config(text=f" {message}")

    def run(self):
        """Start the GUI application"""
        try:
            # Set up window close handler
            self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

            # Start main loop
            self.root.mainloop()

        except Exception as e:
            logger.error(f"GUI error: {e}")
            messagebox.showerror("Error", f"Application error: {str(e)}")

    def _on_closing(self):
        """Handle window closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.monitor.stop_monitoring()
            self.root.destroy()

# ==================== Additional Dialogs ====================

class FilterDialog:
    """Dialog for filtering processes and messages"""

    def __init__(self, parent, monitor):
        self.parent = parent
        self.monitor = monitor
        self.dialog = None

    def show(self):
        """Show filter dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Filter Settings")
        self.dialog.geometry("400x300")

        # Process name filter
        ttk.Label(self.dialog, text="Process Name Contains:").pack(pady=5)
        self.name_entry = ttk.Entry(self.dialog, width=30)
        self.name_entry.pack(pady=5)

        # PID range filter
        ttk.Label(self.dialog, text="PID Range:").pack(pady=5)
        pid_frame = ttk.Frame(self.dialog)
        pid_frame.pack(pady=5)

        ttk.Label(pid_frame, text="From:").pack(side='left', padx=5)
        self.pid_from = ttk.Entry(pid_frame, width=10)
        self.pid_from.pack(side='left', padx=5)

        ttk.Label(pid_frame, text="To:").pack(side='left', padx=5)
        self.pid_to = ttk.Entry(pid_frame, width=10)
        self.pid_to.pack(side='left', padx=5)

        # IPC method filter
        ttk.Label(self.dialog, text="IPC Methods:").pack(pady=5)
        method_frame = ttk.Frame(self.dialog)
        method_frame.pack(pady=5)

        self.method_vars = {}
        for method in IPCMethod:
            var = tk.BooleanVar(value=True)
            ttk.Checkbutton(method_frame, text=method.value, variable=var).pack(side='left', padx=5)
            self.method_vars[method] = var

        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=20)

        ttk.Button(button_frame, text="Apply", command=self._apply_filter).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Reset", command=self._reset_filter).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Close", command=self.dialog.destroy).pack(side='left', padx=5)

    def _apply_filter(self):
        """Apply filters"""
        # Implement filter logic here
        messagebox.showinfo("Filter", "Filters applied successfully")
        self.dialog.destroy()

    def _reset_filter(self):
        """Reset all filters"""
        self.name_entry.delete(0, tk.END)
        self.pid_from.delete(0, tk.END)
        self.pid_to.delete(0, tk.END)
        for var in self.method_vars.values():
            var.set(True)

# ==================== Main Entry Point ====================

def main():
    """Main entry point of the application"""
    try:
        # Create and run the application
        app = IPCDebuggerGUI()

        # Set up test processes if needed
        if len(sys.argv) > 1 and sys.argv[1] == '--test':
            test_manager = TestProcessManager()
            test_manager.create_pipe_test()
            test_manager.create_queue_test()

        # Run the GUI
        app.run()

    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Enable multiprocessing support for Windows
    if sys.platform.startswith('win'):
        multiprocessing.freeze_support()

    main()
