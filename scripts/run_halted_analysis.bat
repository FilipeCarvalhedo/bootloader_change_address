@echo off
REM nRF52840 HALTED Boot Analysis Script for Windows
REM This version ensures MCU is halted at consistent points for accurate comparison
REM Usage: run_halted_analysis.bat

echo ================================================================================
echo nRF52840 HALTED BOOT ANALYSIS TOOL
echo ================================================================================
echo This tool will:
echo 1. Program application via direct flash and halt MCU at reset
echo 2. Capture complete register dump in halted state
echo 3. Program application via bootloader+DFU and halt when bootloader starts app
echo 4. Capture complete register dump in halted state  
echo 5. Compare both dumps to find TRUE register differences (not timing artifacts)
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python and add to PATH.
    pause
    exit /b 1
)

REM Check if nrfjprog is available
nrfjprog --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: nrfjprog not found. Please install nRF Command Line Tools.
    pause
    exit /b 1
)

echo ================================================================================
echo STEP 1: DIRECT FLASH HALTED DUMP
echo ================================================================================
echo This will program the application directly and halt immediately after reset...
echo.
pause

REM Generate timestamp for file names
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "timestamp=%YYYY%%MM%%DD%_%HH%%Min%%Sec%"

set DIRECT_DUMP=direct_flash_halted_%timestamp%.txt
set BOOTLOADER_DUMP=bootloader_dfu_halted_%timestamp%.txt
set COMPARISON_REPORT=halted_analysis_report_%timestamp%.txt

echo Capturing direct flash halted dump...
python nrf52_memory_dump_halted.py --mode direct --output %DIRECT_DUMP%

if errorlevel 1 (
    echo ERROR: Direct flash halted dump failed.
    pause
    exit /b 1
)

echo ✅ Direct flash halted dump saved to: %DIRECT_DUMP%
echo.

echo ================================================================================
echo STEP 2: BOOTLOADER+DFU HALTED DUMP
echo ================================================================================
echo This will program via bootloader+DFU and halt when bootloader tries to start app...
echo.
echo IMPORTANT: Make sure you have:
echo - Bootloader programmed at 0x27000
echo - Application programmed via DFU to 0x31000
echo - Device ready to boot from bootloader
echo.
pause

echo Capturing bootloader+DFU halted dump...
python nrf52_memory_dump_halted.py --mode bootloader --output %BOOTLOADER_DUMP%

if errorlevel 1 (
    echo ERROR: Bootloader halted dump failed.
    pause
    exit /b 1
)

echo ✅ Bootloader+DFU halted dump saved to: %BOOTLOADER_DUMP%
echo.

echo ================================================================================
echo STEP 3: COMPARING HALTED DUMPS
echo ================================================================================
echo Comparing register states from both halted dumps...
echo.

python compare_halted_dumps.py %DIRECT_DUMP% %BOOTLOADER_DUMP% %COMPARISON_REPORT%

if errorlevel 1 (
    echo ERROR: Comparison failed.
    pause
    exit /b 1
)

echo ✅ Comparison report saved to: %COMPARISON_REPORT%
echo.

echo ================================================================================
echo ANALYSIS COMPLETED!
echo ================================================================================
echo Generated files:
echo 📊 %DIRECT_DUMP%      (Direct flash halted state)
echo 📊 %BOOTLOADER_DUMP%  (Bootloader+DFU halted state)  
echo 📋 %COMPARISON_REPORT%          (Detailed comparison and analysis)
echo.

REM Show quick summary
echo 🔍 QUICK SUMMARY:
if exist "%COMPARISON_REPORT%" (
    findstr /C:"Critical Differences:" "%COMPARISON_REPORT%" 2>nul
    if errorlevel 1 (
        echo Could not read summary from report
    ) else (
        echo.
        echo 💡 Check the detailed report for complete analysis.
    )
) else (
    echo Report file not found.
)

echo.
echo ================================================================================
echo ADVANTAGES OF HALTED ANALYSIS:
echo ================================================================================
echo ✅ MCU halted at CONSISTENT execution points in both scenarios
echo ✅ No timing artifacts or race conditions
echo ✅ TRUE register state differences identified
echo ✅ CPU registers, system registers, and execution context compared
echo ✅ Reliable identification of root cause
echo.
echo 🎯 This analysis shows ACTUAL register differences, not timing issues!
echo.
pause



