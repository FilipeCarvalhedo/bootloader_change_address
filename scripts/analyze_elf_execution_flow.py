#!/usr/bin/env python3
"""
ELF Execution Flow Analyzer
Analyzes an ELF file to understand execution flow between systemControl.c and rccMainVostio.c

Usage:
    python analyze_elf_execution_flow.py path/to/app.elf
"""

import subprocess
import sys
import re
import argparse

class ELFAnalyzer:
    def __init__(self, elf_file):
        self.elf_file = elf_file
        self.objdump = "arm-none-eabi-objdump"
        self.nm = "arm-none-eabi-nm"
        
    def run_command(self, cmd):
        """Run a command and return output"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {' '.join(cmd)}")
            print(f"Error: {e.stderr}")
            return ""
        except FileNotFoundError:
            print(f"Command not found: {cmd[0]}")
            return ""
    
    def get_symbols(self):
        """Get all symbols from ELF file"""
        print("Extracting symbols from ELF file...")
        cmd = [self.nm, "-C", "-n", self.elf_file]
        output = self.run_command(cmd)
        
        symbols = {}
        for line in output.split('\n'):
            if line.strip():
                parts = line.strip().split()
                if len(parts) >= 3:
                    addr = parts[0]
                    symbol_type = parts[1]
                    symbol_name = ' '.join(parts[2:])
                    
                    try:
                        addr_int = int(addr, 16)
                        symbols[addr_int] = {
                            'name': symbol_name,
                            'type': symbol_type,
                            'address': addr
                        }
                    except ValueError:
                        continue
        
        return symbols
    
    def find_system_control_functions(self, symbols):
        """Find functions related to system control"""
        system_functions = []
        
        for addr, symbol in symbols.items():
            name = symbol['name'].lower()
            if any(keyword in name for keyword in ['systemcontrol', 'system_control', 'init', 'rccmain']):
                system_functions.append((addr, symbol))
        
        return sorted(system_functions, key=lambda x: x[0])
    
    def get_disassembly(self, start_addr=None, end_addr=None):
        """Get disassembly of specific address range"""
        print(f"Getting disassembly...")
        
        cmd = [self.objdump, "-d", "-C", self.elf_file]
        
        if start_addr and end_addr:
            cmd.extend(["--start-address", f"0x{start_addr:x}", "--stop-address", f"0x{end_addr:x}"])
        
        output = self.run_command(cmd)
        return output
    
    def find_function_calls(self, symbols):
        """Find function calls and their relationships"""
        print("Analyzing function calls...")
        
        # Get full disassembly
        disasm = self.get_disassembly()
        
        function_calls = {}
        current_function = None
        
        for line in disasm.split('\n'):
            # Check for function start
            func_match = re.match(r'^([0-9a-f]+)\s+<([^>]+)>:', line)
            if func_match:
                addr = int(func_match.group(1), 16)
                func_name = func_match.group(2)
                current_function = func_name
                if current_function not in function_calls:
                    function_calls[current_function] = {
                        'address': addr,
                        'calls': [],
                        'called_by': []
                    }
            
            # Check for function calls (bl, blx instructions)
            elif current_function and ('bl ' in line or 'blx ' in line):
                call_match = re.search(r'bl[x]?\s+([0-9a-f]+)\s+<([^>]+)>', line)
                if call_match:
                    target_addr = int(call_match.group(1), 16)
                    target_name = call_match.group(2)
                    
                    function_calls[current_function]['calls'].append({
                        'target': target_name,
                        'address': target_addr
                    })
                    
                    if target_name not in function_calls:
                        function_calls[target_name] = {
                            'address': target_addr,
                            'calls': [],
                            'called_by': []
                        }
                    
                    function_calls[target_name]['called_by'].append(current_function)
        
        return function_calls
    
    def trace_execution_path(self, function_calls, start_func, target_func):
        """Trace execution path from start_func to target_func"""
        print(f"Tracing path from {start_func} to {target_func}...")
        
        def find_path(current, target, path, visited):
            if current == target:
                return [path + [current]]
            
            if current in visited:
                return []
            
            visited.add(current)
            all_paths = []
            
            if current in function_calls:
                for call in function_calls[current]['calls']:
                    sub_paths = find_path(call['target'], target, path + [current], visited.copy())
                    all_paths.extend(sub_paths)
            
            return all_paths
        
        paths = find_path(start_func, target_func, [], set())
        return paths
    
    def analyze_init_sequence(self):
        """Analyze initialization sequence"""
        print("="*80)
        print("ELF EXECUTION FLOW ANALYSIS")
        print("="*80)
        
        # Get symbols
        symbols = self.get_symbols()
        print(f"Found {len(symbols)} symbols")
        
        # Find system control related functions
        system_functions = self.find_system_control_functions(symbols)
        print(f"\nSystem Control Related Functions:")
        print("-" * 40)
        
        for addr, symbol in system_functions:
            print(f"0x{addr:08x}: {symbol['name']} ({symbol['type']})")
        
        # Get function calls
        function_calls = self.find_function_calls(symbols)
        
        # Look for specific functions
        systemcontrol_funcs = [name for name in function_calls.keys() if 'systemcontrol' in name.lower()]
        rccmain_funcs = [name for name in function_calls.keys() if 'rccmain' in name.lower()]
        init_funcs = [name for name in function_calls.keys() if 'init' in name.lower()]
        
        print(f"\nSystemControl Functions Found:")
        for func in systemcontrol_funcs:
            print(f"  - {func}")
            if func in function_calls:
                print(f"    Calls: {[call['target'] for call in function_calls[func]['calls']]}")
        
        print(f"\nRccMain Functions Found:")
        for func in rccmain_funcs:
            print(f"  - {func}")
            if func in function_calls:
                print(f"    Called by: {function_calls[func]['called_by']}")
        
        print(f"\nInit Functions Found ({len(init_funcs)} total):")
        for func in init_funcs[:10]:  # Show first 10
            print(f"  - {func}")
        if len(init_funcs) > 10:
            print(f"  ... and {len(init_funcs) - 10} more")
        
        # Try to trace paths
        if systemcontrol_funcs and rccmain_funcs:
            for sys_func in systemcontrol_funcs:
                for rcc_func in rccmain_funcs:
                    paths = self.trace_execution_path(function_calls, sys_func, rcc_func)
                    if paths:
                        print(f"\nExecution paths from {sys_func} to {rcc_func}:")
                        for i, path in enumerate(paths[:3]):  # Show first 3 paths
                            print(f"  Path {i+1}: {' -> '.join(path)}")
        
        # Look for main function and trace from there
        main_funcs = [name for name in function_calls.keys() if name == 'main' or 'main' in name.lower()]
        if main_funcs:
            print(f"\nMain Functions Found:")
            for func in main_funcs:
                print(f"  - {func}")
                if func in function_calls:
                    print(f"    First few calls: {[call['target'] for call in function_calls[func]['calls'][:5]]}")
        
        return {
            'symbols': symbols,
            'function_calls': function_calls,
            'system_functions': system_functions
        }

def main():
    parser = argparse.ArgumentParser(description='Analyze ELF execution flow')
    parser.add_argument('elf_file', help='Path to ELF file')
    
    args = parser.parse_args()
    
    analyzer = ELFAnalyzer(args.elf_file)
    results = analyzer.analyze_init_sequence()

if __name__ == "__main__":
    main()



