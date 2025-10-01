#!/usr/bin/env python3
"""
Automated nRF52840 Boot Analysis Script
Automates the complete process of:
1. Programming via direct flash
2. Capturing memory dump
3. Programming via bootloader+DFU  
4. Capturing memory dump
5. Comparing and analyzing differences

Usage:
    python automated_analysis.py --app-hex path/to/app.hex --bootloader-hex path/to/bootloader.hex
"""

import subprocess
import argparse
import os
import sys
import time
import datetime

class BootAnalyzer:
    def __init__(self, app_hex, bootloader_hex, softdevice_hex=None):
        self.app_hex = app_hex
        self.bootloader_hex = bootloader_hex
        self.softdevice_hex = softdevice_hex or self.find_softdevice()
        self.nrfjprog = "nrfjprog"
        self.nrfutil = "nrfutil"
        
        # Output files
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.direct_dump = f"direct_flash_dump_{timestamp}.txt"
        self.bootloader_dump = f"bootloader_dfu_dump_{timestamp}.txt"
        self.comparison_report = f"boot_analysis_report_{timestamp}.txt"
        self.dfu_package = f"app_dfu_package_{timestamp}.zip"
        
    def find_softdevice(self):
        """Try to find SoftDevice hex file"""
        possible_paths = [
            "../components/softdevice/s140/hex/s140_nrf52_7.0.1_softdevice.hex",
            "../../components/softdevice/s140/hex/s140_nrf52_7.0.1_softdevice.hex",
            "../../../components/softdevice/s140/hex/s140_nrf52_7.0.1_softdevice.hex"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return "s140_nrf52_7.0.1_softdevice.hex"  # Assume in PATH
    
    def run_command(self, cmd, description, check=True):
        """Run a command and handle errors"""
        print(f"\n🔧 {description}")
        print(f"Command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=check)
            if result.stdout:
                print(f"Output: {result.stdout.strip()}")
            return result
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e}")
            print(f"Stderr: {e.stderr}")
            if check:
                raise
            return e
        except FileNotFoundError as e:
            print(f"❌ Command not found: {e}")
            if check:
                raise
            return e
    
    def erase_device(self):
        """Completely erase the device"""
        self.run_command([self.nrfjprog, "-f", "nrf52", "--eraseall"], "Erasing device")
        time.sleep(2)
    
    def program_direct_flash(self):
        """Program application directly to flash"""
        print(f"\n{'='*60}")
        print("PHASE 1: DIRECT FLASH PROGRAMMING")
        print(f"{'='*60}")
        
        # Erase device
        self.erase_device()
        
        # Program SoftDevice
        self.run_command([self.nrfjprog, "-f", "nrf52", "--program", self.softdevice_hex, "--sectorerase"], 
                        "Programming SoftDevice")
        
        # Program application directly at 0x31000 (new address after bootloader settings)
        self.run_command([self.nrfjprog, "-f", "nrf52", "--program", self.app_hex, "--sectorerase"], 
                        "Programming application (direct)")
        
        # Reset device
        self.run_command([self.nrfjprog, "-f", "nrf52", "--reset"], "Resetting device")
        
        # Wait for boot
        print("⏳ Waiting for application to boot...")
        time.sleep(3)
    
    def capture_direct_dump(self):
        """Capture memory dump after direct programming"""
        print(f"\n🔍 Capturing direct flash memory dump...")
        
        # Use the memory dump script
        dump_cmd = ["python", "nrf52_memory_dump.py", "--mode", "direct", "--output", self.direct_dump]
        self.run_command(dump_cmd, "Capturing direct flash dump")
        
        print(f"✅ Direct flash dump saved to: {self.direct_dump}")
    
    def program_bootloader_dfu(self):
        """Program via bootloader and DFU"""
        print(f"\n{'='*60}")
        print("PHASE 2: BOOTLOADER + DFU PROGRAMMING")  
        print(f"{'='*60}")
        
        # Erase device
        self.erase_device()
        
        # Program SoftDevice
        self.run_command([self.nrfjprog, "-f", "nrf52", "--program", self.softdevice_hex, "--sectorerase"], 
                        "Programming SoftDevice")
        
        # Program bootloader
        self.run_command([self.nrfjprog, "-f", "nrf52", "--program", self.bootloader_hex, "--sectorerase"], 
                        "Programming bootloader")
        
        # Generate bootloader settings
        settings_hex = "bootloader_settings_temp.hex"
        self.run_command([self.nrfutil, "settings", "generate", 
                         "--family", "NRF52840",
                         "--application", self.app_hex,
                         "--application-version", "1",
                         "--bootloader-version", "1", 
                         "--bl-settings-version", "2",
                         "--bootloader-settings-address", "0x30000",
                         settings_hex], "Generating bootloader settings")
        
        # Program bootloader settings
        self.run_command([self.nrfjprog, "-f", "nrf52", "--program", settings_hex, "--sectorerase"], 
                        "Programming bootloader settings")
        
        # Reset to bootloader
        self.run_command([self.nrfjprog, "-f", "nrf52", "--reset"], "Resetting to bootloader")
        
        # Wait for bootloader
        print("⏳ Waiting for bootloader to start...")
        time.sleep(3)
        
        # Create DFU package
        print("📦 Creating DFU package...")
        self.run_command([self.nrfutil, "pkg", "generate",
                         "--hw-version", "52",
                         "--sd-req", "0x0101",
                         "--application", self.app_hex,
                         "--application-version", "1",
                         self.dfu_package], "Creating DFU package")
        
        # Program via DFU (this might need manual intervention)
        print("🔄 Programming via DFU...")
        print("⚠️  Note: DFU programming may require manual intervention")
        print(f"   DFU package created: {self.dfu_package}")
        print("   You may need to manually program via nRF Connect or similar")
        
        # Try automatic DFU (might not work depending on setup)
        dfu_result = self.run_command([self.nrfutil, "dfu", "usb-serial", 
                                      "-pkg", self.dfu_package, 
                                      "-p", "COM3"],  # Adjust COM port as needed
                                     "Programming via DFU", check=False)
        
        if isinstance(dfu_result, Exception):
            print("⚠️  Automatic DFU failed. Please program manually and press Enter when done.")
            input("Press Enter when DFU programming is complete...")
        
        # Wait for application to boot (or fail)
        print("⏳ Waiting for application to boot...")
        time.sleep(5)
    
    def capture_bootloader_dump(self):
        """Capture memory dump after bootloader+DFU programming"""
        print(f"\n🔍 Capturing bootloader+DFU memory dump...")
        
        # Use the memory dump script
        dump_cmd = ["python", "nrf52_memory_dump.py", "--mode", "bootloader", "--output", self.bootloader_dump]
        self.run_command(dump_cmd, "Capturing bootloader+DFU dump")
        
        print(f"✅ Bootloader+DFU dump saved to: {self.bootloader_dump}")
    
    def compare_dumps(self):
        """Compare the two memory dumps"""
        print(f"\n{'='*60}")
        print("PHASE 3: ANALYSIS AND COMPARISON")
        print(f"{'='*60}")
        
        # Use the comparison script
        compare_cmd = ["python", "compare_dumps.py", self.direct_dump, self.bootloader_dump, self.comparison_report]
        self.run_command(compare_cmd, "Comparing memory dumps")
        
        print(f"✅ Comparison report saved to: {self.comparison_report}")
    
    def cleanup(self):
        """Clean up temporary files"""
        temp_files = ["bootloader_settings_temp.hex", "temp_flash.hex"]
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                print(f"🗑️  Cleaned up: {temp_file}")
    
    def run_complete_analysis(self):
        """Run the complete analysis process"""
        print(f"{'='*80}")
        print("nRF52840 AUTOMATED BOOT ANALYSIS")
        print(f"{'='*80}")
        print(f"Application: {self.app_hex}")
        print(f"Bootloader: {self.bootloader_hex}")
        print(f"SoftDevice: {self.softdevice_hex}")
        print(f"Started: {datetime.datetime.now()}")
        
        try:
            # Phase 1: Direct flash
            self.program_direct_flash()
            self.capture_direct_dump()
            
            # Phase 2: Bootloader + DFU
            self.program_bootloader_dfu()
            self.capture_bootloader_dump()
            
            # Phase 3: Analysis
            self.compare_dumps()
            
            # Results summary
            print(f"\n{'='*80}")
            print("ANALYSIS COMPLETE!")
            print(f"{'='*80}")
            print(f"📊 Direct flash dump: {self.direct_dump}")
            print(f"📊 Bootloader dump: {self.bootloader_dump}")
            print(f"📋 Analysis report: {self.comparison_report}")
            print(f"📦 DFU package: {self.dfu_package}")
            
            # Show report summary
            if os.path.exists(self.comparison_report):
                print("\n🔍 QUICK SUMMARY:")
                with open(self.comparison_report, 'r') as f:
                    content = f.read()
                    if "CRITICAL DIFFERENCES" in content:
                        print("⚠️  Critical differences found - check report for details")
                    else:
                        print("✅ No critical differences found")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            raise
        finally:
            self.cleanup()

def main():
    parser = argparse.ArgumentParser(description='Automated nRF52840 Boot Analysis')
    parser.add_argument('--app-hex', required=True, help='Application hex file')
    parser.add_argument('--bootloader-hex', required=True, help='Bootloader hex file')
    parser.add_argument('--softdevice-hex', help='SoftDevice hex file (auto-detected if not specified)')
    
    args = parser.parse_args()
    
    # Verify files exist
    for hex_file in [args.app_hex, args.bootloader_hex]:
        if not os.path.exists(hex_file):
            print(f"Error: File not found: {hex_file}")
            sys.exit(1)
    
    if args.softdevice_hex and not os.path.exists(args.softdevice_hex):
        print(f"Error: SoftDevice file not found: {args.softdevice_hex}")
        sys.exit(1)
    
    analyzer = BootAnalyzer(args.app_hex, args.bootloader_hex, args.softdevice_hex)
    analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()



