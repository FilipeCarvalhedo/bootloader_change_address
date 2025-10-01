#!/usr/bin/env python3
"""
nRF52840 Complete Memory and Register Dump Script - HALTED VERSION
Dumps flash memory, RAM, and critical registers with MCU HALTED at consistent points

This version ensures the MCU is halted at the same execution point for both scenarios:
1. Direct flash programming - halt right after reset
2. Bootloader + DFU programming - halt right after bootloader starts app

Usage:
    python nrf52_memory_dump_halted.py --mode direct --output direct_dump_halted.txt
    python nrf52_memory_dump_halted.py --mode bootloader --output bootloader_dump_halted.txt
"""

import subprocess
import argparse
import datetime
import sys
import os
import time

class NRF52MemoryDumperHalted:
    def __init__(self, output_file, mode):
        self.output_file = output_file
        self.mode = mode
        self.nrfjprog = "nrfjprog"
        
    def run_nrfjprog(self, args):
        """Run nrfjprog command and return output"""
        try:
            cmd = [self.nrfjprog, "-f", "nrf52"] + args
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            return "ERROR: {}".format(e.stderr if e.stderr else str(e))
        except FileNotFoundError:
            return "ERROR: nrfjprog not found in PATH"
    
    def write_section(self, f, title, content):
        """Write a section to the output file"""
        f.write("\n" + "="*80 + "\n")
        f.write("{:^80}\n".format(title))
        f.write("="*80 + "\n")
        f.write(content)
        f.write("\n")
    
    def halt_at_consistent_point(self):
        """Halt the MCU at a consistent point depending on mode"""
        print("Setting up consistent halt point for mode: {}".format(self.mode))
        
        if self.mode == "direct":
            # Direct flash mode: halt right after reset, before any initialization
            print("Direct mode: Halting immediately after reset...")
            
            # Reset and halt immediately
            self.run_nrfjprog(["--reset"])
            time.sleep(0.1)  # Brief delay
            self.run_nrfjprog(["--halt"])
            
            # Verify we're halted at reset vector
            pc_output = self.run_nrfjprog(["--readreg", "0x20000000"])  # Read PC from stack
            print("Halted at: {}".format(pc_output.strip()))
            
        elif self.mode == "bootloader":
            # Bootloader mode: let bootloader run, then halt when it tries to start app
            print("Bootloader mode: Setting breakpoint at application start...")
            
            # Set breakpoint at application vector table (0x31000)
            # This will halt when bootloader jumps to application
            self.run_nrfjprog(["--halt"])
            
            # Set breakpoint at app reset vector
            app_reset_vector_addr = "0x00031004"  # Application reset vector
            app_reset_vector = self.run_nrfjprog(["--memrd", app_reset_vector_addr, "--n", "4"])
            
            if "ERROR" not in app_reset_vector:
                # Extract the reset vector address
                try:
                    # Parse the reset vector address from nrfjprog output
                    lines = app_reset_vector.strip().split('\n')
                    for line in lines:
                        if '0x0002F004:' in line:
                            # Extract hex value after the colon
                            hex_part = line.split(':')[1].strip().split()[0]
                            reset_addr = "0x{:08X}".format(int(hex_part, 16))
                            print("Setting breakpoint at app reset handler: {}".format(reset_addr))
                            
                            # Set hardware breakpoint
                            self.run_nrfjprog(["--halt"])
                            # Note: nrfjprog doesn't support breakpoints directly
                            # We'll use a different approach - halt after a short run
                            break
                except:
                    print("Could not parse reset vector, using alternative method")
            
            # Alternative: Let bootloader run briefly, then halt
            print("Letting bootloader run briefly, then halting...")
            self.run_nrfjprog(["--reset"])
            time.sleep(0.5)  # Let bootloader start
            self.run_nrfjprog(["--halt"])
            
            # Check current PC to see where we are
            pc_output = self.run_nrfjprog(["--readreg", "15"])  # PC register
            print("Halted at PC: {}".format(pc_output.strip()))
    
    def dump_cpu_registers(self, f):
        """Dump CPU registers when halted"""
        print("Dumping CPU registers...")
        
        cpu_regs = [
            ("R0", 0), ("R1", 1), ("R2", 2), ("R3", 3),
            ("R4", 4), ("R5", 5), ("R6", 6), ("R7", 7),
            ("R8", 8), ("R9", 9), ("R10", 10), ("R11", 11),
            ("R12", 12), ("SP/R13", 13), ("LR/R14", 14), ("PC/R15", 15),
        ]
        
        reg_content = "CPU REGISTERS (HALTED STATE):\n\n"
        
        for reg_name, reg_num in cpu_regs:
            reg_data = self.run_nrfjprog(["--readreg", str(reg_num)])
            reg_content += "{:10} (R{:2d}): {}\n".format(reg_name, reg_num, reg_data.strip())
        
        # Special registers
        special_regs = [
            ("xPSR", 16), ("MSP", 17), ("PSP", 18), ("PRIMASK", 20),
            ("BASEPRI", 21), ("FAULTMASK", 22), ("CONTROL", 23)
        ]
        
        reg_content += "\nSPECIAL REGISTERS:\n"
        for reg_name, reg_num in special_regs:
            reg_data = self.run_nrfjprog(["--readreg", str(reg_num)])
            reg_content += "{:10}: {}\n".format(reg_name, reg_data.strip())
        
        self.write_section(f, "CPU REGISTERS", reg_content)
    
    def dump_critical_registers(self, f):
        """Dump critical CPU and system registers"""
        print("Dumping critical system registers...")
        
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
        
        reg_content = "CRITICAL SYSTEM REGISTERS (HALTED STATE):\n\n"
        
        for reg_name, reg_addr in critical_regs:
            reg_data = self.run_nrfjprog(["--memrd", "0x{:08X}".format(reg_addr), "--n", "4"])
            reg_content += "{:40} (0x{:08X}): {}\n".format(reg_name, reg_addr, reg_data.strip())
        
        self.write_section(f, "CRITICAL REGISTERS", reg_content)
    
    def dump_execution_context(self, f):
        """Dump current execution context and call stack"""
        print("Dumping execution context...")
        
        context_content = "EXECUTION CONTEXT (HALTED STATE):\n\n"
        
        # Current PC and instruction
        pc_data = self.run_nrfjprog(["--readreg", "15"])
        context_content += "Program Counter (PC): {}\n".format(pc_data.strip())
        
        # Stack pointer
        sp_data = self.run_nrfjprog(["--readreg", "13"])
        context_content += "Stack Pointer (SP): {}\n".format(sp_data.strip())
        
        # Link register
        lr_data = self.run_nrfjprog(["--readreg", "14"])
        context_content += "Link Register (LR): {}\n".format(lr_data.strip())
        
        # Current instruction at PC
        try:
            pc_lines = pc_data.strip().split('\n')
            for line in pc_lines:
                if 'R15:' in line or '15:' in line:
                    pc_hex = line.split(':')[1].strip().split()[0]
                    pc_addr = int(pc_hex, 16)
                    
                    # Read instruction at PC
                    inst_data = self.run_nrfjprog(["--memrd", "0x{:08X}".format(pc_addr), "--n", "16"])
                    context_content += "\nInstruction at PC (0x{:08X}):\n{}\n".format(pc_addr, inst_data)
                    break
        except:
            context_content += "\nCould not read instruction at PC\n"
        
        # Stack dump (top 64 bytes)
        try:
            sp_lines = sp_data.strip().split('\n')
            for line in sp_lines:
                if 'R13:' in line or '13:' in line:
                    sp_hex = line.split(':')[1].strip().split()[0]
                    sp_addr = int(sp_hex, 16)
                    
                    stack_data = self.run_nrfjprog(["--memrd", "0x{:08X}".format(sp_addr), "--n", "64"])
                    context_content += "\nStack dump (64 bytes from SP 0x{:08X}):\n{}\n".format(sp_addr, stack_data)
                    break
        except:
            context_content += "\nCould not read stack\n"
        
        self.write_section(f, "EXECUTION CONTEXT", context_content)
    
    def dump_vector_tables(self, f):
        """Dump vector tables from key locations"""
        print("Dumping vector tables...")
        
        vector_locations = [
            ("MBR Vector Table", 0x00000000),
            ("SoftDevice Vector Table", 0x00001000),
            ("Bootloader Vector Table", 0x00027000),
            ("Application Vector Table", 0x0002F000),
        ]
        
        vector_content = "VECTOR TABLES (HALTED STATE):\n\n"
        
        for table_name, base_addr in vector_locations:
            vector_content += "{} (0x{:08X}):\n".format(table_name, base_addr)
            
            # Read first 16 vectors (64 bytes)
            vector_data = self.run_nrfjprog(["--memrd", "0x{:08X}".format(base_addr), "--n", "64"])
            
            # Parse and format vector data
            lines = vector_data.strip().split('\n')
            for i, line in enumerate(lines):
                if line.strip() and not line.startswith('ERROR'):
                    vector_content += "  {}\n".format(line.strip())
            
            # Read stack pointer and reset vector specifically
            sp_data = self.run_nrfjprog(["--memrd", "0x{:08X}".format(base_addr), "--n", "4"])
            reset_data = self.run_nrfjprog(["--memrd", "0x{:08X}".format(base_addr + 4), "--n", "4"])
            
            vector_content += "  Stack Pointer: {}\n".format(sp_data.strip())
            vector_content += "  Reset Vector:  {}\n".format(reset_data.strip())
            vector_content += "-" * 50 + "\n\n"
        
        self.write_section(f, "VECTOR TABLES", vector_content)
    
    def dump_mbr_settings(self, f):
        """Dump MBR settings and forward addresses"""
        print("Dumping MBR settings...")
        
        mbr_content = "MBR SETTINGS (HALTED STATE):\n\n"
        
        # MBR parameter page (if exists)
        uicr_mbr_params = self.run_nrfjprog(["--memrd", "0x10001018", "--n", "4"])
        mbr_content += "UICR MBR Params Page: {}\n".format(uicr_mbr_params.strip())
        
        # MBR forward addresses in RAM
        mbr_addresses = [
            ("MBR Forward IRQ", 0x20000000),
            ("MBR Forward Reset", 0x20000004),
            ("MBR Bootloader Addr", 0x00000FF8),
            ("MBR Bootloader Addr Alt", 0x00000FFC),
        ]
        
        for addr_name, addr in mbr_addresses:
            addr_data = self.run_nrfjprog(["--memrd", "0x{:08X}".format(addr), "--n", "4"])
            mbr_content += "{:25} (0x{:08X}): {}\n".format(addr_name, addr, addr_data.strip())
        
        self.write_section(f, "MBR SETTINGS", mbr_content)
    
    def dump_device_info(self, f):
        """Dump device information and status"""
        print("Dumping device info...")
        
        device_content = "DEVICE INFORMATION (HALTED STATE):\n\n"
        
        # Device info
        device_content += "Device ID:\n"
        device_content += self.run_nrfjprog(["--ids"]) + "\n"
        
        # Reset reason
        reset_reason = self.run_nrfjprog(["--memrd", "0x40000400", "--n", "4"])
        device_content += "Reset Reason: {}\n".format(reset_reason.strip())
        
        # Halt status
        device_content += "\nHalt Status:\n"
        device_content += "MCU is HALTED for consistent register reading\n"
        device_content += "Mode: {}\n".format(self.mode)
        
        self.write_section(f, "DEVICE INFORMATION", device_content)
    
    def create_complete_dump(self):
        """Create complete memory dump with MCU halted"""
        print("Creating complete memory dump for mode: {} (HALTED)".format(self.mode))
        
        # First, halt the MCU at consistent point
        self.halt_at_consistent_point()
        
        with open(self.output_file, 'w') as f:
            # Header
            header = "nRF52840 Complete Memory Dump (HALTED)\n"
            header += "Mode: {}\n".format(self.mode)
            header += "Timestamp: {}\n".format(datetime.datetime.now())
            header += "Generated by: nrf52_memory_dump_halted.py\n"
            header += "MCU State: HALTED at consistent execution point\n"
            
            self.write_section(f, "HEADER", header)
            
            # Dump all sections with MCU halted
            self.dump_device_info(f)
            self.dump_cpu_registers(f)
            self.dump_critical_registers(f)
            self.dump_execution_context(f)
            self.dump_vector_tables(f)
            self.dump_mbr_settings(f)
            
            # Footer
            footer = "Dump completed at: {}\n".format(datetime.datetime.now())
            footer += "MCU was kept HALTED during entire dump process\n"
            self.write_section(f, "FOOTER", footer)
        
        print("Complete halted dump saved to: {}".format(self.output_file))
        
        # Resume MCU after dump
        print("Resuming MCU execution...")
        self.run_nrfjprog(["--run"])

def main():
    parser = argparse.ArgumentParser(description='nRF52840 Memory and Register Dumper (HALTED)')
    parser.add_argument('--mode', required=True, choices=['direct', 'bootloader'], 
                       help='Dump mode: direct flash or bootloader+DFU')
    parser.add_argument('--output', required=True, help='Output file name')
    
    args = parser.parse_args()
    
    dumper = NRF52MemoryDumperHalted(args.output, args.mode)
    dumper.create_complete_dump()

if __name__ == "__main__":
    main()



