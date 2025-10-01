
# ============================================================================
# STACK CORRUPTION INVESTIGATION
# Execute this in GDB when stopped at systemControl.c:518
# ============================================================================

echo \n=== DETAILED STACK ANALYSIS ===\n

echo \n--- Current Stack Frame ---\n
info frame
info args
info locals

echo \n--- Extended Stack Dump (128 bytes before/after SP) ---\n
x/64wx $sp-128
echo \n--- Current SP Area ---\n
x/32wx $sp
echo \n--- Stack Above SP ---\n
x/64wx $sp+32

echo \n=== FUNCTION PARAMETER ANALYSIS ===\n

echo \n--- sysCtlInitialize Parameters ---\n
print resource
print initType
print/x (void*)resource
print/x initType

echo \n--- Check if resource pointer is valid ---\n
x/16wx resource
echo \n--- Check resource content ---\n
x/16bx resource

echo \n=== CALL STACK DETAILED ANALYSIS ===\n

echo \n--- Full Backtrace with Details ---\n
bt full

echo \n--- Frame 0 (sysCtlInitialize) ---\n
frame 0
info frame
info locals
info args

echo \n--- Frame 1 (systemControlStart) ---\n
frame 1
info frame
info locals
info args

echo \n--- Frame 2 (mbsMain) ---\n
frame 2
info frame
info locals
info args

echo \n=== MEMORY AROUND CRITICAL VALUES ===\n

echo \n--- Memory around 0x000fd25c (Direct Flash value) ---\n
x/16wx 0x000fd25c-32
x/16wx 0x000fd25c
x/16wx 0x000fd25c+32

echo \n--- Memory around 0x00027000 (Bootloader address) ---\n
x/16wx 0x00027000-32
x/16wx 0x00027000
x/16wx 0x00027000+32

echo \n=== REGISTER ANALYSIS CONTEXT ===\n

echo \n--- R5 and R9 Usage Context ---\n
disassemble sysCtlInitialize
echo \n--- Assembly around current PC ---\n
x/20i $pc-40
x/20i $pc
x/20i $pc+40

echo \n=== HEAP AND MEMORY STATE ===\n

echo \n--- ucHeap Analysis ---\n
print &ucHeap
x/32wx &ucHeap
x/32wx &ucHeap+832

echo \n--- Check for memory corruption patterns ---\n
find &ucHeap, &ucHeap+2048, 0x00027000
find &ucHeap, &ucHeap+2048, 0x000fd25c

echo \n=== SYSTEM CONTROL SPECIFIC ===\n

echo \n--- dispatchEvent function pointer ---\n
print dispatchEvent
disassemble dispatchEvent

echo \n--- SystemControlLevels enum values ---\n
print level
print (int)level

echo \n=== ANALYSIS COMPLETE ===\n
