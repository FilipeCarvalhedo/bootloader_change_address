
# ============================================================================
# VECTOR TABLES AND SYSTEM STATE CAPTURE
# Execute this in GDB when stopped at systemControl.c:518
# ============================================================================

echo \n=== VECTOR TABLES ANALYSIS ===\n

echo \n--- MBR VECTOR TABLE (0x00000000) ---\n
x/16wx 0x00000000

echo \n--- SOFTDEVICE VECTOR TABLE (0x00001000) ---\n
x/16wx 0x00001000

echo \n--- APPLICATION VECTOR TABLE (0x0002F000) ---\n
x/16wx 0x0002F000

echo \n--- BOOTLOADER VECTOR TABLE (0x00027000) ---\n
x/16wx 0x00027000

echo \n=== CRITICAL SYSTEM REGISTERS ===\n

echo \n--- VECTOR TABLE OFFSET REGISTER (VTOR) ---\n
x/wx 0xE000ED08

echo \n--- AIRCR (Application Interrupt and Reset Control) ---\n
x/wx 0xE000ED0C

echo \n--- SCR (System Control Register) ---\n
x/wx 0xE000ED10

echo \n--- CCR (Configuration and Control Register) ---\n
x/wx 0xE000ED14

echo \n=== MBR FORWARD ADDRESSES ===\n

echo \n--- MBR Forward IRQ Address (0x20000000) ---\n
x/wx 0x20000000

echo \n--- MBR Forward Reset Address (0x20000004) ---\n
x/wx 0x20000004

echo \n--- MBR Bootloader Address (0x00000FF8) ---\n
x/wx 0x00000FF8

echo \n--- MBR Bootloader Address Alt (0x00000FFC) ---\n
x/wx 0x00000FFC

echo \n=== NVIC INTERRUPT STATE ===\n

echo \n--- NVIC_ISER0 (Interrupt Set-Enable 0) ---\n
x/wx 0xE000E100

echo \n--- NVIC_ISER1 (Interrupt Set-Enable 1) ---\n
x/wx 0xE000E104

echo \n--- NVIC_ISPR0 (Interrupt Set-Pending 0) ---\n
x/wx 0xE000E200

echo \n--- NVIC_ISPR1 (Interrupt Set-Pending 1) ---\n
x/wx 0xE000E204

echo \n--- NVIC_ICER0 (Interrupt Clear-Enable 0) ---\n
x/wx 0xE000E180

echo \n--- NVIC_ICER1 (Interrupt Clear-Enable 1) ---\n
x/wx 0xE000E184

echo \n=== SYSTEM HANDLER REGISTERS ===\n

echo \n--- SHPR1 (System Handler Priority 1) ---\n
x/wx 0xE000ED18

echo \n--- SHPR2 (System Handler Priority 2) ---\n
x/wx 0xE000ED1C

echo \n--- SHPR3 (System Handler Priority 3) ---\n
x/wx 0xE000ED20

echo \n--- SHCSR (System Handler Control and State) ---\n
x/wx 0xE000ED24

echo \n=== FAULT STATUS REGISTERS ===\n

echo \n--- CFSR (Configurable Fault Status) ---\n
x/wx 0xE000ED28

echo \n--- HFSR (HardFault Status) ---\n
x/wx 0xE000ED2C

echo \n--- DFSR (Debug Fault Status) ---\n
x/wx 0xE000ED30

echo \n=== NORDIC SPECIFIC REGISTERS ===\n

echo \n--- UICR_BOOTLOADERADDR ---\n
x/wx 0x10001014

echo \n--- UICR_MBR_PARAMS_PAGE ---\n
x/wx 0x10001018

echo \n--- POWER_RESETREAS (Reset Reason) ---\n
x/wx 0x40000400

echo \n--- CLOCK_HFCLKSTAT (High Freq Clock Status) ---\n
x/wx 0x40000408

echo \n--- CLOCK_LFCLKSTAT (Low Freq Clock Status) ---\n
x/wx 0x40000418

echo \n=== CURRENT EXECUTION STATE ===\n

echo \n--- Current Registers ---\n
info registers

echo \n--- Stack Pointer Analysis ---\n
print/x $sp
x/16wx $sp

echo \n--- Call Stack ---\n
bt

echo \n=== ANALYSIS COMPLETE ===\n
