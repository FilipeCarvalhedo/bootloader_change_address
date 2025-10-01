#!/usr/bin/env python3
"""
Halted Memory Dump Comparison Script
Compares two nRF52840 memory dumps taken with MCU halted at consistent points

Usage:
    python compare_halted_dumps.py direct_dump_halted.txt bootloader_dump_halted.txt comparison_halted_report.txt
"""

import sys
import re
import datetime

class HaltedDumpComparator:
    def __init__(self, direct_file, bootloader_file, output_file):
        self.direct_file = direct_file
        self.bootloader_file = bootloader_file
        self.output_file = output_file
        
    def parse_halted_dump_file(self, filename):
        """Parse a halted dump file and extract structured data"""
        data = {
            'cpu_registers': {},
            'critical_registers': {},
            'execution_context': {},
            'vectors': {},
            'mbr_settings': {},
            'device_info': {}
        }
        
        try:
            with open(filename, 'r') as f:
                content = f.read()
                
            # Parse CPU registers
            cpu_section = self.extract_section(content, "CPU REGISTERS")
            if cpu_section:
                for line in cpu_section.split('\n'):
                    if ':' in line and ('R' in line or 'PRIMASK' in line or 'CONTROL' in line):
                        parts = line.split(':')
                        if len(parts) >= 2:
                            reg_name = parts[0].strip()
                            reg_value = parts[1].strip()
                            data['cpu_registers'][reg_name] = reg_value
            
            # Parse critical system registers
            critical_section = self.extract_section(content, "CRITICAL REGISTERS")
            if critical_section:
                for line in critical_section.split('\n'):
                    if '0x' in line and ':' in line and '(' in line:
                        # Format: "REG_NAME (0xADDRESS): value"
                        parts = line.split(':')
                        if len(parts) >= 2:
                            reg_name = parts[0].strip()
                            reg_value = parts[1].strip()
                            data['critical_registers'][reg_name] = reg_value
            
            # Parse execution context
            exec_section = self.extract_section(content, "EXECUTION CONTEXT")
            if exec_section:
                for line in exec_section.split('\n'):
                    if ':' in line and ('Program Counter' in line or 'Stack Pointer' in line or 'Link Register' in line):
                        parts = line.split(':')
                        if len(parts) >= 2:
                            context_name = parts[0].strip()
                            context_value = parts[1].strip()
                            data['execution_context'][context_name] = context_value
            
            # Parse vector tables
            vector_section = self.extract_section(content, "VECTOR TABLES")
            if vector_section:
                current_table = None
                for line in vector_section.split('\n'):
                    if 'Vector Table' in line and '0x' in line:
                        current_table = line.strip()
                        data['vectors'][current_table] = {}
                    elif current_table and ('Stack Pointer:' in line or 'Reset Vector:' in line):
                        parts = line.split(':')
                        if len(parts) >= 2:
                            vector_type = parts[0].strip()
                            vector_value = parts[1].strip()
                            data['vectors'][current_table][vector_type] = vector_value
            
            # Parse MBR settings
            mbr_section = self.extract_section(content, "MBR SETTINGS")
            if mbr_section:
                for line in mbr_section.split('\n'):
                    if '0x' in line and ':' in line and ('MBR' in line or 'UICR' in line):
                        parts = line.split(':')
                        if len(parts) >= 2:
                            setting_name = parts[0].strip()
                            setting_value = parts[1].strip()
                            data['mbr_settings'][setting_name] = setting_value
            
            return data
            
        except FileNotFoundError:
            print("Error: File {} not found".format(filename))
            return None
        except Exception as e:
            print("Error parsing {}: {}".format(filename, e))
            return None
    
    def extract_section(self, content, section_name):
        """Extract a specific section from dump content"""
        pattern = r"={80}\n\s*{}\s*\n={80}\n(.*?)\n={80}".format(re.escape(section_name))
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1) if match else None
    
    def compare_cpu_registers(self, direct_data, bootloader_data):
        """Compare CPU registers between halted dumps"""
        differences = []
        
        direct_regs = direct_data.get('cpu_registers', {})
        bootloader_regs = bootloader_data.get('cpu_registers', {})
        
        all_regs = set(direct_regs.keys()) | set(bootloader_regs.keys())
        
        for reg in sorted(all_regs):
            direct_val = direct_regs.get(reg, 'NOT_FOUND')
            bootloader_val = bootloader_regs.get(reg, 'NOT_FOUND')
            
            if direct_val != bootloader_val:
                differences.append({
                    'type': 'CPU_REGISTER',
                    'name': reg,
                    'direct': direct_val,
                    'bootloader': bootloader_val,
                    'critical': self.is_critical_cpu_register(reg)
                })
        
        return differences
    
    def compare_critical_registers(self, direct_data, bootloader_data):
        """Compare critical system registers between halted dumps"""
        differences = []
        
        direct_regs = direct_data.get('critical_registers', {})
        bootloader_regs = bootloader_data.get('critical_registers', {})
        
        all_regs = set(direct_regs.keys()) | set(bootloader_regs.keys())
        
        for reg in sorted(all_regs):
            direct_val = direct_regs.get(reg, 'NOT_FOUND')
            bootloader_val = bootloader_regs.get(reg, 'NOT_FOUND')
            
            if direct_val != bootloader_val:
                differences.append({
                    'type': 'CRITICAL_REGISTER',
                    'name': reg,
                    'direct': direct_val,
                    'bootloader': bootloader_val,
                    'critical': self.is_critical_system_register(reg)
                })
        
        return differences
    
    def compare_execution_context(self, direct_data, bootloader_data):
        """Compare execution context between halted dumps"""
        differences = []
        
        direct_ctx = direct_data.get('execution_context', {})
        bootloader_ctx = bootloader_data.get('execution_context', {})
        
        all_ctx = set(direct_ctx.keys()) | set(bootloader_ctx.keys())
        
        for ctx in sorted(all_ctx):
            direct_val = direct_ctx.get(ctx, 'NOT_FOUND')
            bootloader_val = bootloader_ctx.get(ctx, 'NOT_FOUND')
            
            if direct_val != bootloader_val:
                differences.append({
                    'type': 'EXECUTION_CONTEXT',
                    'name': ctx,
                    'direct': direct_val,
                    'bootloader': bootloader_val,
                    'critical': True  # All execution context differences are important
                })
        
        return differences
    
    def compare_vectors(self, direct_data, bootloader_data):
        """Compare vector tables between halted dumps"""
        differences = []
        
        direct_vectors = direct_data.get('vectors', {})
        bootloader_vectors = bootloader_data.get('vectors', {})
        
        all_tables = set(direct_vectors.keys()) | set(bootloader_vectors.keys())
        
        for table in sorted(all_tables):
            direct_table = direct_vectors.get(table, {})
            bootloader_table = bootloader_vectors.get(table, {})
            
            all_vectors = set(direct_table.keys()) | set(bootloader_table.keys())
            
            for vector in sorted(all_vectors):
                direct_val = direct_table.get(vector, 'NOT_FOUND')
                bootloader_val = bootloader_table.get(vector, 'NOT_FOUND')
                
                if direct_val != bootloader_val:
                    differences.append({
                        'type': 'VECTOR',
                        'name': "{} - {}".format(table, vector),
                        'direct': direct_val,
                        'bootloader': bootloader_val,
                        'critical': True  # All vector differences are critical
                    })
        
        return differences
    
    def compare_mbr_settings(self, direct_data, bootloader_data):
        """Compare MBR settings between halted dumps"""
        differences = []
        
        direct_mbr = direct_data.get('mbr_settings', {})
        bootloader_mbr = bootloader_data.get('mbr_settings', {})
        
        all_settings = set(direct_mbr.keys()) | set(bootloader_mbr.keys())
        
        for setting in sorted(all_settings):
            direct_val = direct_mbr.get(setting, 'NOT_FOUND')
            bootloader_val = bootloader_mbr.get(setting, 'NOT_FOUND')
            
            if direct_val != bootloader_val:
                differences.append({
                    'type': 'MBR_SETTING',
                    'name': setting,
                    'direct': direct_val,
                    'bootloader': bootloader_val,
                    'critical': True  # All MBR differences are critical
                })
        
        return differences
    
    def is_critical_cpu_register(self, reg_name):
        """Determine if a CPU register difference is critical"""
        critical_keywords = ['PC', 'SP', 'LR', 'PSR', 'PRIMASK', 'BASEPRI', 'FAULTMASK', 'CONTROL']
        return any(keyword.upper() in reg_name.upper() for keyword in critical_keywords)
    
    def is_critical_system_register(self, reg_name):
        """Determine if a system register difference is critical for boot"""
        critical_keywords = [
            'VTOR', 'AIRCR', 'SCR', 'CCR', 'NVIC', 'UICR', 'BOOTLOADER',
            'RESET', 'POWER', 'CLOCK', 'SHPR', 'SHCSR', 'CFSR', 'HFSR'
        ]
        return any(keyword.upper() in reg_name.upper() for keyword in critical_keywords)
    
    def analyze_execution_state(self, direct_data, bootloader_data):
        """Analyze execution state differences"""
        analysis = []
        
        # Check PC values
        direct_pc = direct_data.get('execution_context', {}).get('Program Counter (PC)', '')
        bootloader_pc = bootloader_data.get('execution_context', {}).get('Program Counter (PC)', '')
        
        if direct_pc != bootloader_pc:
            analysis.append("EXECUTION POINT DIFFERENCE:")
            analysis.append("  Direct Flash PC: {}".format(direct_pc))
            analysis.append("  Bootloader PC:   {}".format(bootloader_pc))
            analysis.append("  → MCU halted at different execution points")
        
        # Check stack pointers
        direct_sp = direct_data.get('execution_context', {}).get('Stack Pointer (SP)', '')
        bootloader_sp = bootloader_data.get('execution_context', {}).get('Stack Pointer (SP)', '')
        
        if direct_sp != bootloader_sp:
            analysis.append("STACK POINTER DIFFERENCE:")
            analysis.append("  Direct Flash SP: {}".format(direct_sp))
            analysis.append("  Bootloader SP:   {}".format(bootloader_sp))
            analysis.append("  → Different stack usage or initialization")
        
        return analysis
    
    def generate_report(self):
        """Generate comprehensive comparison report for halted dumps"""
        print("Parsing direct flash halted dump...")
        direct_data = self.parse_halted_dump_file(self.direct_file)
        
        print("Parsing bootloader halted dump...")
        bootloader_data = self.parse_halted_dump_file(self.bootloader_file)
        
        if not direct_data or not bootloader_data:
            print("Error: Could not parse halted dump files")
            return
        
        print("Comparing halted dumps...")
        
        # Compare all sections
        cpu_diffs = self.compare_cpu_registers(direct_data, bootloader_data)
        critical_diffs = self.compare_critical_registers(direct_data, bootloader_data)
        exec_diffs = self.compare_execution_context(direct_data, bootloader_data)
        vector_diffs = self.compare_vectors(direct_data, bootloader_data)
        mbr_diffs = self.compare_mbr_settings(direct_data, bootloader_data)
        
        all_diffs = cpu_diffs + critical_diffs + exec_diffs + vector_diffs + mbr_diffs
        critical_diffs_all = [d for d in all_diffs if d['critical']]
        
        # Analyze execution state
        exec_analysis = self.analyze_execution_state(direct_data, bootloader_data)
        
        # Generate report
        with open(self.output_file, 'w') as f:
            # Header
            f.write("=" * 80 + "\n")
            f.write("nRF52840 HALTED MEMORY DUMP COMPARISON REPORT\n".center(80))
            f.write("=" * 80 + "\n")
            f.write("Direct Flash File: {}\n".format(self.direct_file))
            f.write("Bootloader File: {}\n".format(self.bootloader_file))
            f.write("Generated: {}\n".format(datetime.datetime.now()))
            f.write("IMPORTANT: Both dumps taken with MCU HALTED at consistent points\n")
            f.write("Total Differences: {}\n".format(len(all_diffs)))
            f.write("Critical Differences: {}\n".format(len(critical_diffs_all)))
            f.write("\n")
            
            # Summary
            f.write("=" * 80 + "\n")
            f.write("SUMMARY\n".center(80))
            f.write("=" * 80 + "\n")
            f.write("CPU Register Differences: {}\n".format(len(cpu_diffs)))
            f.write("Critical Register Differences: {}\n".format(len(critical_diffs)))
            f.write("Execution Context Differences: {}\n".format(len(exec_diffs)))
            f.write("Vector Table Differences: {}\n".format(len(vector_diffs)))
            f.write("MBR Setting Differences: {}\n".format(len(mbr_diffs)))
            f.write("\n")
            
            # Execution state analysis
            if exec_analysis:
                f.write("=" * 80 + "\n")
                f.write("EXECUTION STATE ANALYSIS\n".center(80))
                f.write("=" * 80 + "\n")
                for line in exec_analysis:
                    f.write(line + "\n")
                f.write("\n")
            
            # Critical differences first
            if critical_diffs_all:
                f.write("=" * 80 + "\n")
                f.write("CRITICAL DIFFERENCES (HALTED STATE COMPARISON)\n".center(80))
                f.write("=" * 80 + "\n")
                
                for diff in critical_diffs_all:
                    f.write("[{}] {}\n".format(diff['type'], diff['name']))
                    f.write("  Direct Flash: {}\n".format(diff['direct']))
                    f.write("  Bootloader:   {}\n".format(diff['bootloader']))
                    f.write("\n")
            
            # All differences by category
            f.write("=" * 80 + "\n")
            f.write("ALL DIFFERENCES BY CATEGORY\n".center(80))
            f.write("=" * 80 + "\n")
            
            for category in ['CPU_REGISTER', 'CRITICAL_REGISTER', 'EXECUTION_CONTEXT', 'VECTOR', 'MBR_SETTING']:
                category_diffs = [d for d in all_diffs if d['type'] == category]
                if category_diffs:
                    f.write("\n{} DIFFERENCES:\n".format(category))
                    f.write("-" * 40 + "\n")
                    
                    for diff in category_diffs:
                        status = "[CRITICAL]" if diff['critical'] else "[INFO]"
                        f.write("{} {}\n".format(status, diff['name']))
                        f.write("  Direct:    {}\n".format(diff['direct']))
                        f.write("  Bootloader: {}\n".format(diff['bootloader']))
                        f.write("\n")
            
            # Analysis and recommendations
            f.write("=" * 80 + "\n")
            f.write("ANALYSIS AND RECOMMENDATIONS (HALTED STATE)\n".center(80))
            f.write("=" * 80 + "\n")
            
            if not critical_diffs_all:
                f.write("✅ NO CRITICAL DIFFERENCES FOUND IN HALTED STATE\n")
                f.write("Both MCUs were halted at consistent points with identical register states.\n")
                f.write("This suggests the issue is dynamic/timing-related, not static register differences.\n")
            else:
                f.write("⚠️  CRITICAL DIFFERENCES DETECTED IN HALTED STATE\n")
                f.write("These are true register state differences, not timing artifacts:\n\n")
                
                # Provide specific analysis based on differences found
                for diff in critical_diffs_all:
                    if 'VTOR' in diff['name']:
                        f.write("• VTOR difference: Vector table offset mismatch in halted state\n")
                        f.write("  → Application vector table not properly configured\n")
                    elif 'PC' in diff['name']:
                        f.write("• Program Counter difference: MCU halted at different execution points\n")
                        f.write("  → Execution flow differs between direct flash and bootloader\n")
                    elif 'SP' in diff['name']:
                        f.write("• Stack Pointer difference: Different stack initialization\n")
                        f.write("  → Stack setup differs between boot methods\n")
                    elif 'NVIC' in diff['name']:
                        f.write("• NVIC difference: Interrupt configuration differs\n")
                        f.write("  → Bootloader leaves interrupts in different state\n")
                    elif 'MBR' in diff['name']:
                        f.write("• MBR difference: Master Boot Record configuration differs\n")
                        f.write("  → Bootloader changes MBR forward addresses\n")
        
        print("Halted comparison report saved to: {}".format(self.output_file))
        print("Found {} critical differences in halted state".format(len(critical_diffs_all)))

def main():
    if len(sys.argv) != 4:
        print("Usage: python compare_halted_dumps.py <direct_dump_halted.txt> <bootloader_dump_halted.txt> <output_report.txt>")
        sys.exit(1)
    
    direct_file = sys.argv[1]
    bootloader_file = sys.argv[2]
    output_file = sys.argv[3]
    
    comparator = HaltedDumpComparator(direct_file, bootloader_file, output_file)
    comparator.generate_report()

if __name__ == "__main__":
    main()



