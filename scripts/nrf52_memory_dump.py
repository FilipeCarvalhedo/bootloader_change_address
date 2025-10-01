#!/usr/bin/env python3
"""
nRF52840 Complete Memory and Register Dump Script
Dumps flash memory, RAM, and critical registers for comparison between:
1. Direct flash programming
2. Bootloader + DFU programming

Usage:
    python nrf52_memory_dump.py --mode direct --output direct_dump.txt
    python nrf52_memory_dump.py --mode bootloader --output bootloader_dump.txt
"""

import subprocess
import argparse
import datetime
import sys
import os

class NRF52MemoryDumper:
    def __init__(self, output_file):
        self.output_file = output_file
        self.nrfjprog = "nrfjprog"
        
    def run_nrfjprog(self, args):
        """Run nrfjprog command and return output"""
        try:
            cmd = [self.nrfjprog, "-f", "nrf52"] + args
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            return "ERROR: {}".format(e.stderr)
        except FileNotFoundError:
            return "ERROR: nrfjprog not found in PATH"
    
    def write_section(self, f, title, content):
        """Write a section to the output file"""
        f.write(f"\n{'='*80}\n")
        f.write(f"{title:^80}\n")
        f.write(f"{'='*80}\n")
        f.write(content)
        f.write("\n")
    
    def dump_flash_memory(self, f):
        """Dump complete flash memory (0x00000000 - 0x00100000)"""
        print("Dumping flash memory...")
        
        # Complete flash dump in hex format
        flash_hex = self.run_nrfjprog(["--readcode", "--output", "temp_flash.hex"])
        
        # Read flash in binary and convert to readable format
        flash_regions = [
            ("MBR (0x0000-0x0FFF)", 0x00000000, 0x1000),
            ("SoftDevice (0x1000-0x26FFF)", 0x00001000, 0x26000),
            ("Bootloader (0x27000-0x2EFFF)", 0x00027000, 0x8000),
            ("MBR Params (0x2F000-0x2FFFF)", 0x0002F000, 0x1000),
            ("Settings Page (0x30000-0x30FFF)", 0x00030000, 0x1000),
            ("Application (0x31000-0xFDFFF)", 0x00031000, 0xCD000),
        ]
        
        flash_content = "FLASH MEMORY DUMP:\n\n"
        
        for region_name, start_addr, size in flash_regions:
            flash_content += f"{region_name}:\n"
            flash_content += f"Start: 0x{start_addr:08X}, Size: 0x{size:08X}\n"
            
            # Read first 256 bytes of each region for analysis
            hex_data = self.run_nrfjprog(["--memrd", f"0x{start_addr:08X}", "--n", "256"])
            flash_content += f"First 256 bytes:\n{hex_data}\n"
            
            # For vector table regions, read more detail
            if "MBR" in region_name or "Application" in region_name:
                vector_data = self.run_nrfjprog(["--memrd", f"0x{start_addr:08X}", "--n", "1024"])
                flash_content += f"Vector table area (1KB):\n{vector_data}\n"
            
            flash_content += "-" * 60 + "\n\n"
        
        self.write_section(f, "FLASH MEMORY", flash_content)
    
    def dump_critical_registers(self, f):
        """Dump critical CPU and system registers"""
        print("Dumping critical registers...")
        
        critical_regs = [
            # ARM Cortex-M4 Core Registers
            ("VTOR (Vector Table Offset)", 0xE000ED08),
            ("AIRCR (App Interrupt/Reset Control)", 0xE000ED0C),
            ("SCR (System Control)", 0xE000ED10),
            ("CCR (Configuration Control)", 0xE000ED14),
            ("SHPR1 (System Handler Priority 1)", 0xE000ED18),
            ("SHPR2 (System Handler Priority 2)", 0xE000ED1C),
            ("SHPR3 (System Handler Priority 3)", 0xE000ED20),
            ("SHCSR (System Handler Control/State)", 0xE000ED24),
            ("CFSR (Configurable Fault Status)", 0xE000ED28),
            ("HFSR (HardFault Status)", 0xE000ED2C),
            ("DFSR (Debug Fault Status)", 0xE000ED30),
            ("MMFAR (MemManage Fault Address)", 0xE000ED34),
            ("BFAR (BusFault Address)", 0xE000ED38),
            
            # NVIC Registers
            ("NVIC_ISER0 (Interrupt Set-Enable 0)", 0xE000E100),
            ("NVIC_ISER1 (Interrupt Set-Enable 1)", 0xE000E104),
            ("NVIC_ICER0 (Interrupt Clear-Enable 0)", 0xE000E180),
            ("NVIC_ICER1 (Interrupt Clear-Enable 1)", 0xE000E184),
            ("NVIC_ISPR0 (Interrupt Set-Pending 0)", 0xE000E200),
            ("NVIC_ISPR1 (Interrupt Set-Pending 1)", 0xE000E204),
            ("NVIC_ICPR0 (Interrupt Clear-Pending 0)", 0xE000E280),
            ("NVIC_ICPR1 (Interrupt Clear-Pending 1)", 0xE000E284),
            
            # nRF52840 Specific
            ("UICR_BOOTLOADERADDR", 0x10001014),
            ("UICR_MBR_PARAMS_PAGE", 0x10001018),
            ("UICR_APPROTECT", 0x10001208),
            ("UICR_DEBUGCTRL", 0x1000120C),
            
            # Clock and Power
            ("CLOCK_HFCLKSTAT", 0x40000408),
            ("CLOCK_LFCLKSTAT", 0x40000418),
            ("POWER_RESETREAS", 0x40000400),
            ("POWER_GPREGRET", 0x4000051C),
            ("POWER_GPREGRET2", 0x40000520),
        ]
        
        reg_content = "CRITICAL REGISTERS:\n\n"
        
        for reg_name, reg_addr in critical_regs:
            reg_data = self.run_nrfjprog(["--memrd", f"0x{reg_addr:08X}", "--n", "4"])
            reg_content += f"{reg_name:40} (0x{reg_addr:08X}): {reg_data.strip()}\n"
        
        self.write_section(f, "CRITICAL REGISTERS", reg_content)
    
    def dump_vector_tables(self, f):
        """Dump vector tables from key locations"""
        print("Dumping vector tables...")
        
        vector_locations = [
            ("MBR Vector Table", 0x00000000),
            ("SoftDevice Vector Table", 0x00001000),
            ("Bootloader Vector Table", 0x00027000),
            ("Application Vector Table", 0x0002F000),
        ]
        
        vector_content = "VECTOR TABLES:\n\n"
        
        for table_name, base_addr in vector_locations:
            vector_content += f"{table_name} (0x{base_addr:08X}):\n"
            
            # Read first 16 vectors (64 bytes)
            vector_data = self.run_nrfjprog(["--memrd", f"0x{base_addr:08X}", "--n", "64"])
            lines = vector_data.strip().split('\n')
            
            for i, line in enumerate(lines):
                if line.strip() and not line.startswith('ERROR'):
                    vector_content += f"  Vector {i*4:2d}: {line.strip()}\n"
            
            # Read stack pointer and reset vector specifically
            sp_data = self.run_nrfjprog(["--memrd", f"0x{base_addr:08X}", "--n", "4"])
            reset_data = self.run_nrfjprog(["--memrd", f"0x{base_addr+4:08X}", "--n", "4"])
            
            vector_content += f"  Stack Pointer: {sp_data.strip()}\n"
            vector_content += f"  Reset Vector:  {reset_data.strip()}\n"
            vector_content += "-" * 50 + "\n\n"
        
        self.write_section(f, "VECTOR TABLES", vector_content)
    
    def dump_mbr_settings(self, f):
        """Dump MBR settings and forward addresses"""
        print("Dumping MBR settings...")
        
        mbr_content = "MBR SETTINGS:\n\n"
        
        # MBR parameter page (if exists)
        uicr_mbr_params = self.run_nrfjprog(["--memrd", "0x10001018", "--n", "4"])
        mbr_content += f"UICR MBR Params Page: {uicr_mbr_params.strip()}\n"
        
        # MBR forward addresses in RAM
        mbr_addresses = [
            ("MBR Forward IRQ", 0x20000000),
            ("MBR Forward Reset", 0x20000004),
            ("MBR Bootloader Addr", 0x00000FF8),
            ("MBR Bootloader Addr Alt", 0x00000FFC),
        ]
        
        for addr_name, addr in mbr_addresses:
            addr_data = self.run_nrfjprog(["--memrd", f"0x{addr:08X}", "--n", "4"])
            mbr_content += f"{addr_name:25} (0x{addr:08X}): {addr_data.strip()}\n"
        
        self.write_section(f, "MBR SETTINGS", mbr_content)
    
    def dump_device_info(self, f):
        """Dump device information and status"""
        print("Dumping device info...")
        
        device_content = "DEVICE INFORMATION:\n\n"
        
        # Device info
        device_content += "Device ID:\n"
        device_content += self.run_nrfjprog(["--ids"]) + "\n"
        
        device_content += "Device Info:\n"
        device_content += self.run_nrfjprog(["--deviceinfo"]) + "\n"
        
        # Reset reason
        reset_reason = self.run_nrfjprog(["--memrd", "0x40000400", "--n", "4"])
        device_content += f"Reset Reason: {reset_reason.strip()}\n"
        
        self.write_section(f, "DEVICE INFORMATION", device_content)
    
    def create_complete_dump(self, mode):
        """Create complete memory dump"""
        print(f"Creating complete memory dump for mode: {mode}")
        
        with open(self.output_file, 'w') as f:
            # Header
            header = f"nRF52840 Complete Memory Dump\n"
            header += f"Mode: {mode}\n"
            header += f"Timestamp: {datetime.datetime.now()}\n"
            header += f"Generated by: nrf52_memory_dump.py\n"
            
            self.write_section(f, "HEADER", header)
            
            # Dump all sections
            self.dump_device_info(f)
            self.dump_critical_registers(f)
            self.dump_vector_tables(f)
            self.dump_mbr_settings(f)
            self.dump_flash_memory(f)
            
            # Footer
            footer = f"Dump completed at: {datetime.datetime.now()}\n"
            self.write_section(f, "FOOTER", footer)
        
        print(f"Complete dump saved to: {self.output_file}")

def main():
    parser = argparse.ArgumentParser(description='nRF52840 Memory and Register Dumper')
    parser.add_argument('--mode', required=True, choices=['direct', 'bootloader'], 
                       help='Dump mode: direct flash or bootloader+DFU')
    parser.add_argument('--output', required=True, help='Output file name')
    
    args = parser.parse_args()
    
    dumper = NRF52MemoryDumper(args.output)
    dumper.create_complete_dump(args.mode)

if __name__ == "__main__":
    main()
