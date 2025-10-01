# ✅ ble_app_hrs_freertos Atualizado para Layout Sequencial

## 🔄 Alterações Realizadas:

### **1. Linker Script**
**Arquivo**: `examples/ble_app_hrs_freertos/armgcc/ble_app_hrs_freertos_gcc_nrf52.ld`

```diff
- FLASH (rx) : ORIGIN = 0x2F000, LENGTH = 0xd1000
+ FLASH (rx) : ORIGIN = 0x31000, LENGTH = 0xcd000
```

### **2. CMakeLists.txt** 
**Arquivo**: `examples/ble_app_hrs_freertos/ble_app_hrs_freertos/CMakeLists.txt`

- ✅ **Aplicação**: Movida para 0x31000
- ✅ **Bootloader settings**: Geradas e relocadas de 0xFF000 → 0x30000
- ✅ **srec_cat**: Usando ferramenta profissional para relocação
- ✅ **Flash process**: Completo com aplicação + settings relocadas

### **3. Código da Aplicação**
**Arquivo**: `examples/ble_app_hrs_freertos/ble_app_hrs_freertos/main.c`

```diff
- } else if (app_start == 0x2F000) {
-     debug_uart_puts("*** BOOTLOADER MODE (0x2F000) ***\r\n");
+ } else if (app_start == 0x31000) {
+     debug_uart_puts("*** BOOTLOADER MODE (0x31000) ***\r\n");

- if (app_start == 0x2F000) {
+ if (app_start == 0x31000) {
```

## 🎯 Novo Layout Sequencial:

```
0x27000 ├─ Bootloader (32KB)
0x2F000 ├─ MBR params (4KB)        ← Relocado
0x30000 ├─ Bootloader Settings (4KB) ← Relocado  
0x31000 ├─ Application (~820KB)     ← ble_app_hrs_freertos
0xFE000 ├─ [LIVRE] (8KB)           ← Espaço liberado
```

## 🧪 Como Testar:

```bash
cd examples/ble_app_hrs_freertos/ble_app_hrs_freertos
mkdir build && cd build
cmake .. && make
make flash_program
```

## ✅ Status dos Projetos:

| Projeto | Layout Sequencial | flash_program | Status |
|---------|------------------|---------------|--------|
| **ble_uart** | ✅ | ✅ | **Funcionando** |
| **blink** | ✅ | ✅ | **Funcionando** |
| **ble_app_hrs_freertos** | ✅ | ✅ | **Atualizado** |

Todos os três projetos agora estão usando o **layout de memória sequencial** com **srec_cat** para relocação profissional das bootloader settings!
