# IPC Debugger - Professional Inter-Process Communication Debugging Tool

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## 🎯 Overview

IPC Debugger is a comprehensive tool for monitoring, analyzing, and debugging Inter-Process Communication in real-time. It helps developers identify bottlenecks, deadlocks, and performance issues in multi-process applications.

## ✨ Features

### Core Features
- 📊 **Real-time Process Monitoring** - Track all running processes with CPU and memory usage
- 🔄 **IPC Visualization** - Interactive graph showing communication between processes
- 🔒 **Deadlock Detection** - Automatic detection of circular dependencies
- 📈 **Performance Analysis** - Detailed metrics on throughput, latency, and resource usage
- 🎨 **Visual Communication Flow** - Animated data transfer visualization

### Supported IPC Methods
- **Pipes** - One-directional data flow
- **Message Queues** - Ordered message passing with buffering
- **Shared Memory** - Fast memory-based data sharing
- **Sockets** - Network-based communication

### Advanced Features
- Pattern recognition (Request-Response, Pub-Sub, Pipeline)
- Bottleneck identification and analysis
- Performance recommendations
- HTML report generation
- Export/Import session data

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ipc-debugger.git
cd ipc-debugger

# Install requirements
pip install -r requirements.txt

# Run quick start
python quick_start.py
```
Manual Start
```bash
# Start the debugger
python ipc_debugger.py

# Run with test scenarios
python ipc_debugger.py --test
```

## 📦 Requirements

Python 3.8 or higher
psutil
matplotlib
numpy
tkinter (usually included with Python)

## 🎮 Usage

### Basic Workflow

1. **Start Monitoring**
   - Launch the application
   - Click "Start Monitoring" in the Monitor menu

2. **View Processes**
   - See all running processes in the left panel
   - Click on a process to view details

3. **Analyze Communications**
   - Watch real-time visualization in the center panel
   - Check logs in the right panel

4. **Run Tests**
   - Use Test menu to simulate different IPC scenarios
   - Try deadlock simulation to see detection in action

### Keyboard Shortcuts

- Ctrl+S - Export logs
- Ctrl+O - Load session
- Ctrl+R - Refresh display
- F1 - Show help
- Ctrl+Q - Quit application

## 📊 Understanding the Display

### Process Colors
- 🟢 **Green** - Running normally
- 🔴 **Red** - Blocked/Deadlocked
- 🟡 **Yellow** - Waiting for resources
- 🔵 **Blue** - Ready state

### Connection Lines
- **Solid Arrow** - Active communication
- **Dashed Line** - Idle connection
- **Line Thickness** - Represents data volume

### Node Size
- Larger nodes indicate higher CPU usage

## 🧪 Test Scenarios

Run specific test scenarios:

```bash
# Pipe communication test
python test_ipc_scenarios.py pipe

# Queue with multiple producers
python test_ipc_scenarios.py queue

# Shared memory test
python test_ipc_scenarios.py shared

# Deadlock simulation
python test_ipc_scenarios.py deadlock

# All scenarios
python test_ipc_scenarios.py all
```

## 📝 Configuration

Edit `config.json` to customize:

- GUI settings (size, refresh rate)
- Monitoring parameters
- Color schemes
- Performance thresholds

## 📈 Performance Tips

### High CPU Usage
- Reduce refresh rate in config
- Limit number of monitored processes

### Memory Issues
- Decrease max_log_entries
- Enable log rotation

### Slow Visualization
- Reduce animation complexity
- Filter unnecessary processes

## 🐛 Troubleshooting

### Common Issues

**Issue: GUI not starting**
```bash
# Check tkinter installation
python -c "import tkinter; print('Tkinter OK')"
```

**Issue: Permission errors**
```bash
# Run with elevated privileges (Linux/Mac)
sudo python ipc_debugger.py
```

**Issue: Missing processes**
- Some system processes require admin privileges
- Check process filter settings

## 📊 Export Formats

The tool supports multiple export formats:

- **JSON** - Complete data with all details
- **HTML** - Professional report with charts
- **CSV** - For spreadsheet analysis

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

---

**Developed for developers and system administrators to diagnose and optimize IPC operations.**
