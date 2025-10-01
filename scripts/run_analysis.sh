#!/bin/bash
# nRF52840 Boot Analysis Script for Linux/macOS
# Usage: ./run_analysis.sh path/to/app.hex path/to/bootloader.hex

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}🔧 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check arguments
if [ $# -ne 2 ]; then
    echo "Usage: $0 <app.hex> <bootloader.hex>"
    echo "Example: $0 ../examples/ble_app_hrs_freertos/build/ble_app_hrs_freertos.hex ../examples/dfu/secure_bootloader/build/secure_bootloader.hex"
    exit 1
fi

APP_HEX="$1"
BOOTLOADER_HEX="$2"

echo "================================================================================"
echo "nRF52840 BOOT ANALYSIS TOOL"
echo "================================================================================"
echo "App HEX: $APP_HEX"
echo "Bootloader HEX: $BOOTLOADER_HEX"
echo ""

# Check if files exist
if [ ! -f "$APP_HEX" ]; then
    print_error "Application hex file not found: $APP_HEX"
    exit 1
fi

if [ ! -f "$BOOTLOADER_HEX" ]; then
    print_error "Bootloader hex file not found: $BOOTLOADER_HEX"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    print_error "Python not found. Please install Python 3.6+ and add to PATH."
    exit 1
fi

# Determine Python command
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
MAJOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$MAJOR_VERSION" -lt 3 ] || ([ "$MAJOR_VERSION" -eq 3 ] && [ "$MINOR_VERSION" -lt 6 ]); then
    print_error "Python 3.6+ required. Found: $PYTHON_VERSION"
    exit 1
fi

print_success "Python $PYTHON_VERSION found"

# Check if nrfjprog is available
if ! command -v nrfjprog &> /dev/null; then
    print_error "nrfjprog not found. Please install nRF Command Line Tools."
    echo "Download from: https://www.nordicsemi.com/Products/Development-tools/nrf-command-line-tools"
    exit 1
fi

NRFJPROG_VERSION=$(nrfjprog --version 2>&1 | head -1)
print_success "nrfjprog found: $NRFJPROG_VERSION"

# Check if nrfutil is available
if ! command -v nrfutil &> /dev/null; then
    print_warning "nrfutil not found. DFU programming may fail."
    print_warning "Install with: pip install nrfutil"
    print_warning "Or program DFU manually when prompted."
else
    NRFUTIL_VERSION=$(nrfutil version 2>&1)
    print_success "nrfutil found: $NRFUTIL_VERSION"
fi

# Check if device is connected
print_status "Checking for connected nRF52 devices..."
if ! nrfjprog --ids &> /dev/null; then
    print_error "No nRF52 devices found. Please connect your nRF52840 via USB."
    exit 1
fi

DEVICE_IDS=$(nrfjprog --ids 2>/dev/null)
print_success "Found device(s): $DEVICE_IDS"

echo ""
print_status "Starting automated analysis..."
echo ""

# Run the automated analysis
if $PYTHON_CMD automated_analysis.py --app-hex "$APP_HEX" --bootloader-hex "$BOOTLOADER_HEX"; then
    echo ""
    echo "================================================================================"
    print_success "ANALYSIS COMPLETED SUCCESSFULLY!"
    echo "================================================================================"
    echo "Check the generated files:"
    echo "📊 *_direct_flash_dump_*.txt    (Direct flash memory state)"
    echo "📊 *_bootloader_dfu_dump_*.txt  (Bootloader+DFU memory state)"  
    echo "📋 *_boot_analysis_report_*.txt (Detailed comparison and analysis)"
    echo "📦 *_app_dfu_package_*.zip      (Generated DFU package)"
    echo ""
    echo "💡 Open the analysis report to see the root cause of boot issues."
    echo ""
    
    # Try to find and show the latest report
    LATEST_REPORT=$(ls -t *_boot_analysis_report_*.txt 2>/dev/null | head -1)
    if [ -n "$LATEST_REPORT" ]; then
        echo "📋 Latest report: $LATEST_REPORT"
        echo ""
        
        # Show quick summary from report
        if grep -q "CRITICAL DIFFERENCES" "$LATEST_REPORT"; then
            print_warning "Critical differences found in report!"
            echo "Key findings:"
            grep -A 5 "CRITICAL DIFFERENCES" "$LATEST_REPORT" | head -10
        elif grep -q "NO CRITICAL DIFFERENCES" "$LATEST_REPORT"; then
            print_success "No critical differences found."
            echo "Boot issues may be timing-related or software-specific."
        fi
    fi
    
else
    echo ""
    print_error "Analysis failed. Check output above for details."
    echo ""
    echo "Common issues:"
    echo "• Device not connected or in use by another application"
    echo "• Insufficient permissions (try with sudo on Linux)"
    echo "• nrfutil not installed (for DFU operations)"
    echo "• Hex files corrupted or invalid"
    echo ""
    exit 1
fi

# Cleanup function
cleanup() {
    if [ -f "temp_flash.hex" ]; then
        rm -f "temp_flash.hex"
        print_status "Cleaned up temporary files"
    fi
}

# Set trap to cleanup on exit
trap cleanup EXIT

echo "Analysis complete! 🎉"



