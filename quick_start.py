#!/usr/bin/env python3
"""
Quick Start Script for IPC Debugger
Automatically sets up and launches the IPC Debugger with test scenarios
"""

import os
import sys
import subprocess
import time
import threading
from pathlib import Path

class QuickStart:
    """Quick start utility for IPC Debugger"""

    def __init__(self):
        self.debugger_process = None
        self.test_processes = []

    def check_requirements(self):
        """Check and install required packages"""
        required_packages = ['psutil', 'matplotlib', 'numpy']
        missing_packages = []

        for package in required_packages:
            try:
                __import__(package)
                print(f"[OK] {package} is installed")
            except ImportError:
                missing_packages.append(package)
                print(f"[MISSING] {package} is missing")

        if missing_packages:
            print("\nInstalling missing packages...")
            for package in missing_packages:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print("Installation complete!")

        return True

    def start_debugger(self):
        """Start the IPC Debugger"""
        print("\n[STARTING] IPC Debugger...")
        self.debugger_process = subprocess.Popen(
            [sys.executable, "ipc_debugger.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(2)  # Give it time to start
        print("[OK] IPC Debugger started")

    def start_test_scenarios(self, scenario="all"):
        """Start test scenarios"""
        print(f"\n[TEST] Starting test scenarios: {scenario}")
        test_process = subprocess.Popen(
            [sys.executable, "test_ipc_scenarios.py", scenario],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.test_processes.append(test_process)
        print("[OK] Test scenarios running")

    def monitor_output(self):
        """Monitor and display output"""
        def read_output(process, name):
            for line in iter(process.stdout.readline, b''):
                print(f"[{name}] {line.decode().strip()}")

        if self.debugger_process:
            thread = threading.Thread(
                target=read_output,
                args=(self.debugger_process, "Debugger")
            )
            thread.daemon = True
            thread.start()

    def run(self):
        """Main execution"""
        print("""
IPC DEBUGGER - QUICK START
==========================
This script will:
1. Check and install requirements
2. Start the IPC Debugger GUI
3. Launch test processes for demonstration
        """)

        # Check requirements
        if not self.check_requirements():
            return

        # Start debugger
        self.start_debugger()

        # Ask user for test scenario
        print("\n[SELECT] Test scenario:")
        print("1. Pipe Communication")
        print("2. Message Queue")
        print("3. Shared Memory")
        print("4. Deadlock Demo")
        print("5. All Scenarios")
        print("6. No Test (Manual)")

        choice = input("\nEnter choice (1-6): ").strip()

        scenario_map = {
            '1': 'pipe',
            '2': 'queue',
            '3': 'shared',
            '4': 'deadlock',
            '5': 'all',
            '6': None
        }

        scenario = scenario_map.get(choice, 'all')

        if scenario:
            self.start_test_scenarios(scenario)

        # Monitor output
        self.monitor_output()

        print("\n[SUCCESS] IPC Debugger is running!")
        print("Press Ctrl+C to stop all processes\n")

        try:
            # Keep running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n[STOP] Shutting down...")
            self.cleanup()

    def cleanup(self):
        """Clean up all processes"""
        if self.debugger_process:
            self.debugger_process.terminate()
            self.debugger_process.wait()

        for process in self.test_processes:
            process.terminate()
            process.wait()

        print("[DONE] All processes stopped")

if __name__ == "__main__":
    quick_start = QuickStart()
    quick_start.run()
