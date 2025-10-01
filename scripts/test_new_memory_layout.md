# Teste do Novo Layout de Memória Sequencial

## Novo Layout Implementado (SEQUENCIAL)

- **Bootloader**: 0x27000 - 0x2EFFF (32KB) - mantém
- **MBR params**: 0x2F000 - 0x2FFFF (4KB) - **MOVIDO de 0xFE000**
- **Bootloader Settings**: 0x30000 - 0x30FFF (4KB) - **MOVIDO de 0xFF000**
- **Aplicação**: 0x31000 - 0xFDFFF (~820KB) - **NOVO ENDEREÇO**

## Vantagens do Layout Sequencial

1. **Organização lógica**: Bootloader → MBR → Settings → App
2. **Sem fragmentação**: Todos os componentes estão em sequência
3. **Facilita debugging**: Layout mais intuitivo
4. **Libera espaço no final**: Não usa mais 0xFE000-0xFFFFF

## Arquivos Alterados

### 1. Linker Scripts
- `examples/dfu/secure_bootloader/pca10056_s140_ble/armgcc/secure_bootloader_gcc_nrf52.ld`
  - MBR params movido para 0x2F000
  - Bootloader settings movido para 0x30000

- `examples/ble_uart/armgcc/ble_app_uart_gcc_nrf52.ld`
- `examples/blink/armgcc/blinky_gcc_nrf52.ld`
  - Aplicação movida para 0x31000
  - Tamanho ajustado para 0xcd000

### 2. Configurações DFU
- `components/libraries/bootloader/dfu/nrf_dfu_types.h`
  - BOOTLOADER_SETTINGS_ADDRESS para nRF52840: 0xFF000 → 0x30000
  - NRF_MBR_PARAMS_PAGE_ADDRESS para nRF52840: 0xFE000 → 0x2F000

- `components/libraries/bootloader/dfu/nrf_dfu_utils.c`
  - nrf_dfu_bank0_start_addr(): 0x2F000 → 0x31000

### 3. Scripts e CMakeLists
- CMakeLists.txt dos exemplos atualizados para novo endereço da aplicação (0x31000)
- Scripts de análise atualizados para refletir novo layout sequencial

## Como Testar

1. **Rebuild do bootloader:**
   ```bash
   cd examples/dfu/secure_bootloader/pca10056_s140_ble/armgcc
   make clean && make
   ```

2. **Rebuild das aplicações:**
   ```bash
   cd examples/ble_uart/ble_uart
   mkdir build && cd build
   cmake .. && make
   ```

3. **Flash do sistema completo:**
   ```bash
   # 1. Apagar chip
   nrfjprog -f nrf52 --eraseall

   # 2. Programar SoftDevice
   nrfjprog -f nrf52 --program s140_nrf52_7.2.0_softdevice.hex --sectorerase

   # 3. Programar bootloader
   nrfjprog -f nrf52 --program secure_bootloader.hex --sectorerase

   # 4. Programar aplicação via CMake target
   make flash_program
   ```

## Verificação

Após o flash, o bootloader deve:
1. Encontrar MBR params em 0x2F000
2. Encontrar bootloader settings em 0x30000
3. Inicializar a aplicação em 0x31000
4. O sistema deve funcionar normalmente

Se houver problemas, verifique:
- MBR params estão sendo criados em 0x2F000
- Bootloader settings estão sendo criados em 0x30000
- Aplicação está sendo linkada para 0x31000
- Não há conflitos de memória no layout sequencial
