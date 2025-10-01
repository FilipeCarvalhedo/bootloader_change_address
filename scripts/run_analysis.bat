@echo off
REM nRF52840 Boot Analysis Script for Windows
REM Usage: run_analysis.bat path\to\app.hex path\to\bootloader.hex

if "%~2"=="" (
    echo Usage: run_analysis.bat ^<app.hex^> ^<bootloader.hex^>
    echo Example: run_analysis.bat ..\examples\ble_app_hrs_freertos\build\ble_app_hrs_freertos.hex ..\examples\dfu\secure_bootloader\build\secure_bootloader.hex
    pause
    exit /b 1
)

set APP_HEX=%~1
set BOOTLOADER_HEX=%~2

echo ================================================================================
echo nRF52840 BOOT ANALYSIS TOOL
echo ================================================================================
echo App HEX: %APP_HEX%
echo Bootloader HEX: %BOOTLOADER_HEX%
echo.

REM Check if files exist
if not exist "%APP_HEX%" (
    echo ERROR: Application hex file not found: %APP_HEX%
    pause
    exit /b 1
)

if not exist "%BOOTLOADER_HEX%" (
    echo ERROR: Bootloader hex file not found: %BOOTLOADER_HEX%
    pause
    exit /b 1
)

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

REM Check if nrfutil is available
nrfutil version >nul 2>&1
if errorlevel 1 (
    echo WARNING: nrfutil not found. DFU programming may fail.
    echo Please install nrfutil or program DFU manually.
    echo.
)

echo Starting automated analysis...
echo.

REM Run the automated analysis
python automated_analysis.py --app-hex "%APP_HEX%" --bootloader-hex "%BOOTLOADER_HEX%"

if errorlevel 1 (
    echo.
    echo ERROR: Analysis failed. Check output above for details.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo ANALYSIS COMPLETED SUCCESSFULLY!
echo ================================================================================
echo Check the generated files:
echo - *_direct_flash_dump_*.txt    (Direct flash memory state)
echo - *_bootloader_dfu_dump_*.txt  (Bootloader+DFU memory state)  
echo - *_boot_analysis_report_*.txt (Detailed comparison and analysis)
echo.
echo Open the analysis report to see the root cause of boot issues.
echo.
pause



