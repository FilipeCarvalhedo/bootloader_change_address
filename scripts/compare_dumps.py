#!/usr/bin/env python3
"""
Memory Dump Comparison Script
Compares two nRF52840 memory dumps to identify differences between
direct flash and bootloader+DFU programming modes.

Usage:
    python compare_dumps.py direct_dump.txt bootloader_dump.txt comparison_report.txt
"""

import sys
import re
import datetime

class DumpComparator:
    def __init__(self, direct_file, bootloader_file, output_file):
        self.direct_file = direct_file
        self.bootloader_file = bootloader_file
        self.output_file = output_file
        
    def parse_dump_file(self, filename):
        """Parse a dump file and extract structured data"""
        data = {
            'registers': {},
            'vectors': {},
            'mbr_settings': {},
            'flash_regions': {},
            'device_info': {}
        }
        
        try:
            with open(filename, 'r') as f:
                content = f.read()
                
            # Parse critical registers
            reg_section = self.extract_section(content, "CRITICAL REGISTERS")
            if reg_section:
                for line in reg_section.split('\n'):
                    if '0x' in line and ':' in line:
                        parts = line.split(':')
                        if len(parts) >= 2:
                            reg_name = parts[0].strip()
                            reg_value = parts[1].strip()
                            data['registers'][reg_name] = reg_value
            
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
                    if '0x' in line and ':' in line:
                        parts = line.split(':')
                        if len(parts) >= 2:
                            setting_name = parts[0].strip()
                            setting_value = parts[1].strip()
                            data['mbr_settings'][setting_name] = setting_value
            
            return data
            
        except FileNotFoundError:
            print(f"Error: File {filename} not found")
            return None
        except Exception as e:
            print(f"Error parsing {filename}: {e}")
            return None
    
    def extract_section(self, content, section_name):
        """Extract a specific section from dump content"""
        pattern = f"={'{'}80{'}'}\n{section_name:^80}\n={'='*80}\n(.*?)\n={'='*80}"
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1) if match else None
    
    def compare_registers(self, direct_data, bootloader_data):
        """Compare critical registers between dumps"""
        differences = []
        
        direct_regs = direct_data.get('registers', {})
        bootloader_regs = bootloader_data.get('registers', {})
        
        all_regs = set(direct_regs.keys()) | set(bootloader_regs.keys())
        
        for reg in sorted(all_regs):
            direct_val = direct_regs.get(reg, 'NOT_FOUND')
            bootloader_val = bootloader_regs.get(reg, 'NOT_FOUND')
            
            if direct_val != bootloader_val:
                differences.append({
                    'type': 'REGISTER',
                    'name': reg,
                    'direct': direct_val,
                    'bootloader': bootloader_val,
                    'critical': self.is_critical_register(reg)
                })
        
        return differences
    
    def compare_vectors(self, direct_data, bootloader_data):
        """Compare vector tables between dumps"""
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
                        'name': f"{table} - {vector}",
                        'direct': direct_val,
                        'bootloader': bootloader_val,
                        'critical': True  # All vector differences are critical
                    })
        
        return differences
    
    def compare_mbr_settings(self, direct_data, bootloader_data):
        """Compare MBR settings between dumps"""
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
    
    def is_critical_register(self, reg_name):
        """Determine if a register difference is critical for boot"""
        critical_keywords = [
            'VTOR', 'AIRCR', 'SCR', 'CCR', 'NVIC', 'UICR', 'BOOTLOADER',
            'RESET', 'POWER', 'CLOCK', 'Vector', 'Stack'
        ]
        
        return any(keyword.upper() in reg_name.upper() for keyword in critical_keywords)
    
    def generate_report(self):
        """Generate comprehensive comparison report"""
        print("Parsing direct flash dump...")
        direct_data = self.parse_dump_file(self.direct_file)
        
        print("Parsing bootloader dump...")
        bootloader_data = self.parse_dump_file(self.bootloader_file)
        
        if not direct_data or not bootloader_data:
            print("Error: Could not parse dump files")
            return
        
        print("Comparing dumps...")
        
        # Compare all sections
        reg_diffs = self.compare_registers(direct_data, bootloader_data)
        vector_diffs = self.compare_vectors(direct_data, bootloader_data)
        mbr_diffs = self.compare_mbr_settings(direct_data, bootloader_data)
        
        all_diffs = reg_diffs + vector_diffs + mbr_diffs
        critical_diffs = [d for d in all_diffs if d['critical']]
        
        # Generate report
        with open(self.output_file, 'w') as f:
            # Header
            f.write("=" * 80 + "\n")
            f.write("nRF52840 MEMORY DUMP COMPARISON REPORT\n".center(80))
            f.write("=" * 80 + "\n")
            f.write(f"Direct Flash File: {self.direct_file}\n")
            f.write(f"Bootloader File: {self.bootloader_file}\n")
            f.write(f"Generated: {datetime.datetime.now()}\n")
            f.write(f"Total Differences: {len(all_diffs)}\n")
            f.write(f"Critical Differences: {len(critical_diffs)}\n")
            f.write("\n")
            
            # Summary
            f.write("=" * 80 + "\n")
            f.write("SUMMARY\n".center(80))
            f.write("=" * 80 + "\n")
            f.write(f"Register Differences: {len(reg_diffs)}\n")
            f.write(f"Vector Table Differences: {len(vector_diffs)}\n")
            f.write(f"MBR Setting Differences: {len(mbr_diffs)}\n")
            f.write("\n")
            
            # Critical differences first
            if critical_diffs:
                f.write("=" * 80 + "\n")
                f.write("CRITICAL DIFFERENCES (LIKELY BOOT ISSUES)\n".center(80))
                f.write("=" * 80 + "\n")
                
                for diff in critical_diffs:
                    f.write(f"[{diff['type']}] {diff['name']}\n")
                    f.write(f"  Direct Flash: {diff['direct']}\n")
                    f.write(f"  Bootloader:   {diff['bootloader']}\n")
                    f.write("\n")
            
            # All differences
            f.write("=" * 80 + "\n")
            f.write("ALL DIFFERENCES\n".center(80))
            f.write("=" * 80 + "\n")
            
            for category in ['REGISTER', 'VECTOR', 'MBR_SETTING']:
                category_diffs = [d for d in all_diffs if d['type'] == category]
                if category_diffs:
                    f.write(f"\n{category} DIFFERENCES:\n")
                    f.write("-" * 40 + "\n")
                    
                    for diff in category_diffs:
                        status = "[CRITICAL]" if diff['critical'] else "[INFO]"
                        f.write(f"{status} {diff['name']}\n")
                        f.write(f"  Direct:    {diff['direct']}\n")
                        f.write(f"  Bootloader: {diff['bootloader']}\n")
                        f.write("\n")
            
            # Analysis and recommendations
            f.write("=" * 80 + "\n")
            f.write("ANALYSIS AND RECOMMENDATIONS\n".center(80))
            f.write("=" * 80 + "\n")
            
            if not critical_diffs:
                f.write("✅ NO CRITICAL DIFFERENCES FOUND\n")
                f.write("The memory states are very similar. Boot issues may be timing-related.\n")
            else:
                f.write("⚠️  CRITICAL DIFFERENCES DETECTED\n")
                f.write("These differences likely explain the boot failure:\n\n")
                
                # Analyze specific critical differences
                for diff in critical_diffs:
                    if 'VTOR' in diff['name']:
                        f.write("• VTOR difference: Vector table offset mismatch\n")
                        f.write("  → Check if application vector table is correctly set\n")
                    elif 'Stack Pointer' in diff['name']:
                        f.write("• Stack Pointer difference: Initial SP mismatch\n")
                        f.write("  → Check if stack is correctly initialized\n")
                    elif 'Reset Vector' in diff['name']:
                        f.write("• Reset Vector difference: Entry point mismatch\n")
                        f.write("  → Check if reset handler address is correct\n")
                    elif 'BOOTLOADER' in diff['name']:
                        f.write("• Bootloader address difference: MBR configuration issue\n")
                        f.write("  → Check MBR forward address setup\n")
        
        print(f"Comparison report saved to: {self.output_file}")
        print(f"Found {len(critical_diffs)} critical differences")

def main():
    if len(sys.argv) != 4:
        print("Usage: python compare_dumps.py <direct_dump.txt> <bootloader_dump.txt> <output_report.txt>")
        sys.exit(1)
    
    direct_file = sys.argv[1]
    bootloader_file = sys.argv[2]
    output_file = sys.argv[3]
    
    comparator = DumpComparator(direct_file, bootloader_file, output_file)
    comparator.generate_report()

if __name__ == "__main__":
    main()



