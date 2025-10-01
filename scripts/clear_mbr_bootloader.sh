#!/bin/bash

echo "========================================"
echo "CLEARING MBR BOOTLOADER CONFIGURATION"
echo "========================================"
echo
echo "This script will:"
echo "1. Clear MBR bootloader address (0x00000FF8)"
echo "2. Clear MBR settings page (0x00000FFC)" 
echo "3. Reset the device"
echo
echo "WARNING: This will remove bootloader configuration!"
echo
read -p "Press Enter to continue or Ctrl+C to cancel..."

echo
echo "=== Step 1: Clearing MBR Bootloader Address (0x00000FF8) ==="
nrfjprog -f nrf52 --memwr 0x00000FF8 --val 0xFFFFFFFF
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to clear MBR bootloader address"
    exit 1
fi
echo "SUCCESS: MBR bootloader address cleared"

echo
echo "=== Step 2: Clearing MBR Settings Page (0x00000FFC) ==="
nrfjprog -f nrf52 --memwr 0x00000FFC --val 0xFFFFFFFF
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to clear MBR settings page"
    exit 1
fi
echo "SUCCESS: MBR settings page cleared"

echo
echo "=== Step 3: Verifying MBR Clear ==="
echo "Checking MBR bootloader addresses:"
nrfjprog -f nrf52 --memrd 0x00000FF8
nrfjprog -f nrf52 --memrd 0x00000FFC

echo
echo "=== Step 4: Resetting Device ==="
nrfjprog -f nrf52 --reset
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to reset device"
    exit 1
fi
echo "SUCCESS: Device reset"

echo
echo "========================================"
echo "MBR BOOTLOADER CONFIGURATION CLEARED!"
echo "========================================"
echo
echo "Now test your application:"
echo "1. Flash your application normally"
echo "2. Check if it boots without the reset loop"
echo "3. Run GDB analysis again to compare"
echo



