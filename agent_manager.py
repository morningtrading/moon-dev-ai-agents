#!/usr/bin/env python3
"""
🌙 Moon Dev AI Agent Manager
Interactive control panel for managing all AI agents

Usage:
    python agent_manager.py              # Interactive menu
    python agent_manager.py status       # Show status of all agents
    python agent_manager.py start all    # Start all enabled agents
    python agent_manager.py stop all     # Stop all running agents
"""

import os
import sys
import yaml
import subprocess
import signal
import time
from pathlib import Path
from datetime import datetime
from termcolor import colored, cprint
import psutil

class AgentManager:
    def __init__(self, config_file="agent_config.yaml"):
        self.project_root = Path(__file__).parent
        self.config_file = self.project_root / config_file
        self.config = self.load_config()
        
        # Setup directories
        self.log_dir = self.project_root / self.config['settings']['log_directory']
        self.pid_dir = self.project_root / self.config['settings']['pid_directory']
        self.python_path = self.config['settings']['python_path']
        
        # Ensure directories exist
        self.log_dir.mkdir(exist_ok=True)
        self.pid_dir.mkdir(exist_ok=True)
        
    def load_config(self):
        """Load configuration from YAML file"""
        try:
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            cprint(f"❌ Config file not found: {self.config_file}", "red")
            sys.exit(1)
        except yaml.YAMLError as e:
            cprint(f"❌ Error parsing config file: {e}", "red")
            sys.exit(1)
    
    def save_config(self):
        """Save current configuration to YAML file"""
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            return True
        except Exception as e:
            cprint(f"❌ Error saving config: {e}", "red")
            return False
    
    def get_pid_file(self, agent_name):
        """Get PID file path for an agent"""
        return self.pid_dir / f"{agent_name}.pid"
    
    def get_log_file(self, agent_name):
        """Get log file path for an agent"""
        return self.log_dir / f"{agent_name}.log"
    
    def is_process_running(self, pid):
        """Check if a process is running"""
        try:
            process = psutil.Process(pid)
            return process.is_running()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
    
    def get_agent_pid(self, agent_name):
        """Get PID of running agent"""
        pid_file = self.get_pid_file(agent_name)
        if pid_file.exists():
            try:
                with open(pid_file, 'r') as f:
                    pid = int(f.read().strip())
                if self.is_process_running(pid):
                    return pid
                else:
                    # Clean up stale PID file
                    pid_file.unlink()
            except (ValueError, ProcessLookupError):
                pid_file.unlink()
        return None
    
    def start_agent(self, agent_name):
        """Start an agent"""
        if agent_name not in self.config['agents']:
            cprint(f"❌ Unknown agent: {agent_name}", "red")
            return False
        
        agent_config = self.config['agents'][agent_name]
        
        # Check if already running
        pid = self.get_agent_pid(agent_name)
        if pid:
            cprint(f"⚠️  {agent_name} is already running (PID: {pid})", "yellow")
            return False
        
        # Check if agent script exists
        script_path = self.project_root / agent_config['script']
        if not script_path.exists():
            cprint(f"❌ Agent script not found: {script_path}", "red")
            return False
        
        # Show warning if agent has one
        if 'warning' in agent_config:
            cprint(f"⚠️  WARNING: {agent_config['warning']}", "yellow", attrs=['bold'])
            response = input(colored("   Continue? (yes/no): ", "yellow"))
            if response.lower() not in ['yes', 'y']:
                cprint("   Cancelled.", "cyan")
                return False
        
        # Start the agent
        log_file = self.get_log_file(agent_name)
        
        try:
            # Use nohup to run in background
            cmd = [
                'nohup',
                'env',
                f'PYTHONPATH={self.python_path}',
                'python',
                '-u',  # Unbuffered output
                str(script_path)
            ]
            
            with open(log_file, 'w') as log:
                process = subprocess.Popen(
                    cmd,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    cwd=self.project_root,
                    preexec_fn=os.setpgrp  # Create new process group
                )
            
            # Save PID
            pid_file = self.get_pid_file(agent_name)
            with open(pid_file, 'w') as f:
                f.write(str(process.pid))
            
            # Wait a moment and check if it's still running
            time.sleep(2)
            if self.is_process_running(process.pid):
                cprint(f"✅ Started {agent_name} (PID: {process.pid})", "green")
                return True
            else:
                cprint(f"❌ {agent_name} failed to start. Check logs: {log_file}", "red")
                return False
                
        except Exception as e:
            cprint(f"❌ Error starting {agent_name}: {e}", "red")
            return False
    
    def stop_agent(self, agent_name):
        """Stop an agent"""
        pid = self.get_agent_pid(agent_name)
        
        if not pid:
            cprint(f"⚠️  {agent_name} is not running", "yellow")
            return False
        
        try:
            # Try graceful shutdown first (SIGTERM)
            os.kill(pid, signal.SIGTERM)
            
            # Wait up to 5 seconds for process to terminate
            for _ in range(50):
                if not self.is_process_running(pid):
                    break
                time.sleep(0.1)
            
            # Force kill if still running
            if self.is_process_running(pid):
                os.kill(pid, signal.SIGKILL)
                time.sleep(0.5)
            
            # Clean up PID file
            pid_file = self.get_pid_file(agent_name)
            if pid_file.exists():
                pid_file.unlink()
            
            cprint(f"✅ Stopped {agent_name}", "green")
            return True
            
        except ProcessLookupError:
            # Process already dead
            pid_file = self.get_pid_file(agent_name)
            if pid_file.exists():
                pid_file.unlink()
            cprint(f"⚠️  {agent_name} was not running", "yellow")
            return False
        except Exception as e:
            cprint(f"❌ Error stopping {agent_name}: {e}", "red")
            return False
    
    def restart_agent(self, agent_name):
        """Restart an agent"""
        cprint(f"🔄 Restarting {agent_name}...", "cyan")
        self.stop_agent(agent_name)
        time.sleep(1)
        return self.start_agent(agent_name)
    
    def get_agent_status(self, agent_name):
        """Get status of an agent"""
        pid = self.get_agent_pid(agent_name)
        agent_config = self.config['agents'][agent_name]
        
        status = {
            'name': agent_name,
            'enabled': agent_config.get('enabled', False),
            'running': pid is not None,
            'pid': pid,
            'description': agent_config.get('description', 'No description'),
            'log_file': self.get_log_file(agent_name),
            'check_interval': agent_config.get('check_interval_minutes', None)
        }
        
        if pid:
            try:
                process = psutil.Process(pid)
                status['uptime'] = time.time() - process.create_time()
                status['memory_mb'] = process.memory_info().rss / 1024 / 1024
                
                # Calculate next check if interval is known
                if status['check_interval']:
                    interval_seconds = status['check_interval'] * 60
                    uptime_seconds = status['uptime']
                    # Calculate time until next check
                    time_since_last = uptime_seconds % interval_seconds
                    time_until_next = interval_seconds - time_since_last
                    status['next_check_seconds'] = time_until_next
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return status
    
    def status_all(self):
        """Show status of all agents"""
        print("\n" + "=" * 80)
        cprint("🌙 Moon Dev Agent Manager - Status", "cyan", attrs=['bold'])
        print("=" * 80 + "\n")
        
        running_count = 0
        enabled_count = 0
        
        for agent_name in self.config['agents']:
            status = self.get_agent_status(agent_name)
            
            # Status indicator
            if status['running']:
                indicator = colored("●", "green")
                running_count += 1
            elif status['enabled']:
                indicator = colored("○", "yellow")
            else:
                indicator = colored("○", "white")
            
            if status['enabled']:
                enabled_count += 1
            
            # Format output
            name_str = f"{indicator} {agent_name}".ljust(30)
            
            if status['running']:
                pid_str = colored(f"PID: {status['pid']}", "green")
                parts = [pid_str]
                
                # Add next check countdown if available
                if 'next_check_seconds' in status:
                    seconds = int(status['next_check_seconds'])
                    if seconds >= 60:
                        mins = seconds // 60
                        secs = seconds % 60
                        next_str = f"Next: {mins}m{secs:02d}s"
                    else:
                        next_str = f"Next: {seconds}s"
                    parts.append(colored(next_str, "cyan"))
                elif 'uptime' in status:
                    uptime_str = f"Up: {int(status['uptime']//60)}m"
                    parts.append(uptime_str)
                
                # Add memory
                if 'memory_mb' in status:
                    memory_str = f"RAM: {status['memory_mb']:.1f}MB"
                    parts.append(memory_str)
                
                info_str = "  ".join(parts)
            elif status['enabled']:
                info_str = colored("Enabled (not running)", "yellow")
            else:
                info_str = colored("Disabled", "white")
            
            print(f"{name_str} {info_str}")
        
        print("\n" + "=" * 80)
        print(f"Total: {len(self.config['agents'])} agents  |  " +
              f"Enabled: {enabled_count}  |  " +
              f"Running: {running_count}")
        print("=" * 80 + "\n")
    
    def start_all_enabled(self):
        """Start all enabled agents"""
        cprint("\n🚀 Starting all enabled agents...\n", "cyan", attrs=['bold'])
        
        started = 0
        failed = 0
        
        for agent_name, config in self.config['agents'].items():
            if config.get('enabled', False):
                if self.start_agent(agent_name):
                    started += 1
                else:
                    failed += 1
                time.sleep(1)  # Delay between starts
        
        print()
        if started > 0:
            cprint(f"✅ Successfully started {started} agent(s)", "green")
        if failed > 0:
            cprint(f"❌ Failed to start {failed} agent(s)", "red")
    
    def stop_all(self):
        """Stop all running agents"""
        cprint("\n🛑 Stopping all agents...\n", "cyan", attrs=['bold'])
        
        stopped = 0
        for agent_name in self.config['agents']:
            if self.get_agent_pid(agent_name):
                if self.stop_agent(agent_name):
                    stopped += 1
        
        print()
        cprint(f"✅ Stopped {stopped} agent(s)", "green")
    
    def view_logs(self, agent_name, lines=50):
        """View recent logs for an agent"""
        log_file = self.get_log_file(agent_name)
        
        if not log_file.exists():
            cprint(f"❌ No log file found for {agent_name}", "red")
            return
        
        cprint(f"\n📋 Last {lines} lines of {agent_name} logs:\n", "cyan")
        print("=" * 80)
        
        try:
            result = subprocess.run(['tail', f'-n{lines}', str(log_file)], 
                                  capture_output=True, text=True)
            print(result.stdout)
        except Exception as e:
            cprint(f"❌ Error reading logs: {e}", "red")
        
        print("=" * 80 + "\n")
    
    def toggle_agent(self, agent_name):
        """Toggle agent enabled/disabled"""
        if agent_name not in self.config['agents']:
            cprint(f"❌ Unknown agent: {agent_name}", "red")
            return False
        
        current = self.config['agents'][agent_name].get('enabled', False)
        self.config['agents'][agent_name]['enabled'] = not current
        
        if self.save_config():
            status = "enabled" if not current else "disabled"
            cprint(f"✅ {agent_name} is now {status}", "green")
            return True
        return False
    
    def interactive_menu(self):
        """Interactive menu for managing agents"""
        while True:
            os.system('clear' if os.name != 'nt' else 'cls')
            
            print("\n" + "=" * 80)
            cprint("🌙 Moon Dev AI Agent Manager", "cyan", attrs=['bold'])
            print("=" * 80 + "\n")
            
            cprint("Main Menu:", "yellow", attrs=['bold'])
            print("  1. Show status of all agents")
            print("  2. Start all enabled agents")
            print("  3. Stop all running agents")
            print("  4. Start specific agent")
            print("  5. Stop specific agent")
            print("  6. Restart specific agent")
            print("  7. Enable/disable agent")
            print("  8. View agent logs")
            print("  9. Refresh/reload config")
            print("  0. Exit")
            print()
            
            choice = input(colored("Select option: ", "cyan"))
            
            if choice == '1':
                self.status_all()
                input(colored("\nPress Enter to continue...", "cyan"))
            
            elif choice == '2':
                self.start_all_enabled()
                input(colored("\nPress Enter to continue...", "cyan"))
            
            elif choice == '3':
                self.stop_all()
                input(colored("\nPress Enter to continue...", "cyan"))
            
            elif choice == '4':
                agent_name = input(colored("\nEnter agent name: ", "cyan"))
                self.start_agent(agent_name)
                input(colored("\nPress Enter to continue...", "cyan"))
            
            elif choice == '5':
                agent_name = input(colored("\nEnter agent name: ", "cyan"))
                self.stop_agent(agent_name)
                input(colored("\nPress Enter to continue...", "cyan"))
            
            elif choice == '6':
                agent_name = input(colored("\nEnter agent name: ", "cyan"))
                self.restart_agent(agent_name)
                input(colored("\nPress Enter to continue...", "cyan"))
            
            elif choice == '7':
                agent_name = input(colored("\nEnter agent name: ", "cyan"))
                self.toggle_agent(agent_name)
                input(colored("\nPress Enter to continue...", "cyan"))
            
            elif choice == '8':
                agent_name = input(colored("\nEnter agent name: ", "cyan"))
                lines = input(colored("Number of lines (default 50): ", "cyan")) or "50"
                self.view_logs(agent_name, int(lines))
                input(colored("\nPress Enter to continue...", "cyan"))
            
            elif choice == '9':
                self.config = self.load_config()
                cprint("\n✅ Config reloaded", "green")
                time.sleep(1)
            
            elif choice == '0':
                cprint("\n👋 Goodbye!\n", "cyan")
                break
            
            else:
                cprint("\n❌ Invalid option", "red")
                time.sleep(1)

def main():
    manager = AgentManager()
    
    if len(sys.argv) == 1:
        # Interactive mode
        manager.interactive_menu()
    else:
        # Command line mode
        command = sys.argv[1].lower()
        
        if command == 'status':
            manager.status_all()
        
        elif command == 'start':
            if len(sys.argv) > 2:
                if sys.argv[2] == 'all':
                    manager.start_all_enabled()
                else:
                    manager.start_agent(sys.argv[2])
            else:
                cprint("❌ Usage: agent_manager.py start <agent_name|all>", "red")
        
        elif command == 'stop':
            if len(sys.argv) > 2:
                if sys.argv[2] == 'all':
                    manager.stop_all()
                else:
                    manager.stop_agent(sys.argv[2])
            else:
                cprint("❌ Usage: agent_manager.py stop <agent_name|all>", "red")
        
        elif command == 'restart':
            if len(sys.argv) > 2:
                manager.restart_agent(sys.argv[2])
            else:
                cprint("❌ Usage: agent_manager.py restart <agent_name>", "red")
        
        elif command == 'logs':
            if len(sys.argv) > 2:
                lines = int(sys.argv[3]) if len(sys.argv) > 3 else 50
                manager.view_logs(sys.argv[2], lines)
            else:
                cprint("❌ Usage: agent_manager.py logs <agent_name> [lines]", "red")
        
        elif command == 'enable' or command == 'disable':
            if len(sys.argv) > 2:
                manager.toggle_agent(sys.argv[2])
            else:
                cprint(f"❌ Usage: agent_manager.py {command} <agent_name>", "red")
        
        else:
            cprint(f"❌ Unknown command: {command}", "red")
            print("\nAvailable commands:")
            print("  status              - Show status of all agents")
            print("  start <agent|all>   - Start agent(s)")
            print("  stop <agent|all>    - Stop agent(s)")
            print("  restart <agent>     - Restart agent")
            print("  logs <agent> [n]    - View agent logs")
            print("  enable <agent>      - Enable agent")
            print("  disable <agent>     - Disable agent")

if __name__ == "__main__":
    main()
