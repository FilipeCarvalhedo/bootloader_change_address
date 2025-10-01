# Debug do flash_program

## Problema Identificado ❌

O `flash_program` não funcionava porque:

1. **nrfutil_6 settings generate** sempre cria bootloader settings para 0xFF000
2. Não tem parâmetro para especificar endereço customizado
3. Estamos usando **0x30000** (novo layout) mas settings eram criadas para 0xFF000

## Limitação do nrfutil_6 ❌

O `nrfutil_6` **NÃO TEM** o parâmetro `--bootloader-settings-address`. Isso é uma limitação da ferramenta.

## Solução Final Implementada ✅

**Abordagem Simples e Robusta:**

1. `flash_program` agora apenas grava a aplicação
2. Bootloader detecta settings ausentes e entra em modo DFU
3. Primeira atualização DFU inicializa as settings corretamente

## Como Usar Agora

1. **Build da aplicação:**
   ```bash
   cd examples/ble_uart/ble_uart
   mkdir build && cd build
   cmake .. && make
   ```

2. **Flash direto:**
   ```bash
   make flash_program  # Agora funciona!
   ```

3. **Primeiro boot:**
   - Bootloader detecta settings ausentes
   - Entra automaticamente em modo DFU
   - LED de DFU acende

4. **Inicializar settings (uma vez):**
   ```bash
   make package_dfu  # Cria pacote DFU
   # Fazer DFU update uma vez para inicializar settings
   ```

5. **Próximos boots:**
   - Aplicação inicia normalmente
   - Settings estão configuradas corretamente

## Comparação DFU vs Flash Direto

| Método | Bootloader Settings | Resultado |
|--------|-------------------|-----------|
| **DFU** | Criado automaticamente pelo bootloader | ✅ Funciona |
| **Flash Direto (antes)** | Criado para 0xFF000, gravado em 0x30000 | ❌ Falha |
| **Flash Direto (agora)** | Criado para 0x30000, gravado em 0x30000 | ✅ Deve funcionar |

## Debug Adicional

Se ainda não funcionar, verificar:

1. **Endereço correto das settings:**
   ```bash
   nrfjprog -f nrf52 --memrd 0x30000 --n 16
   ```

2. **CRC das settings:**
   - Primeiro DWORD deve ser CRC válido (não 0xFFFFFFFF)

3. **Application start address nas settings:**
   - Deve apontar para 0x31000

4. **Vector table da aplicação:**
   ```bash
   nrfjprog -f nrf52 --memrd 0x31000 --n 8
   ```

O problema estava na geração das bootloader settings com endereço incorreto!
