# Integrar `lk_mbr_flash` no build

O `git status` dentro de `components/libraries/` só mostra a pasta nova porque os **.c modificados ficam noutros subdiretórios**. Na raiz do submódulo `bootloader_change_address` corre:

```bash
cd ext/sdk_custom/nordic/bootloader_change_address
git status
git diff components/libraries/bootloader/
git diff components/libraries/bootloader/dfu/nrf_dfu_mbr.c
```

Se **não** houver diff nesses ficheiros, falta aplicar os passos abaixo.

---

## 1. Submódulo `bootloader_change_address`

### 1.1 Ficheiros desta pasta (já criados)

- `lk_mbr_flash_params.h`
- `lk_mbr_flash_params.c`

```bash
git add components/libraries/lk_mbr_flash/
```

### 1.2 `components/libraries/bootloader/nrf_bootloader_app_start_final.c`

- Depois de `#include "nrf_mbr.h"` (ou junto aos outros includes Nordic), adicionar:

```c
#include "lk_mbr_flash_params.h"
```

- No **início** de `void nrf_bootloader_app_start_final(uint32_t vector_table_addr)`, **antes** de `#if !defined(LK_DISABLE_ACL_PROTECTION)` / proteção ACL, adicionar:

```c
    /* MBR 0xFF8/0xFFC -> 0xFFFFFFFF antes da app (UICR / chainload). */
    {
        uint32_t const mbr_clr = lk_mbr_flash_params_clear();
        if (mbr_clr != NRF_SUCCESS)
        {
            NRF_LOG_ERROR("lk_mbr_flash_params_clear failed: 0x%x", mbr_clr);
        }
        else
        {
            NRF_LOG_INFO("MBR 0xFF8/0xFFC cleared before app");
        }
    }

```

### 1.3 `components/libraries/bootloader/dfu/nrf_dfu_mbr.c`

- Incluir (com os outros includes):

```c
#include "lk_mbr_flash_params.h"
```

- Em `nrf_dfu_mbr_copy_bl`, **depois** de `sd_softdevice_disable();` e `__disable_irq();`, **antes** de montar `sd_mbr_command_t` / `SD_MBR_COMMAND_COPY_BL`, adicionar:

```c
    {
        uint32_t mbr_prog = lk_mbr_flash_params_set_boot_secure();
        if (mbr_prog != NRF_SUCCESS)
        {
            return (uint32_t)mbr_prog;
        }
    }
```

- Nos `NRF_LOG_INFO` do `COPY_BL`, usar `LK_MBR_FLASH_BOOT_SECURE_ADDR` (definido no header) em vez de um `#define` local `0x27000`, se ainda existir.

Remover includes só usados por código antigo de patch MBR inline (`nrf_nvmc.h`, `nrf.h`) se deixarem de ser necessários.

---

## 2. Repositório pai `loopkey-nrf51` (projeto `boot_secure`)

### 2.1 `projects/boot_secure/external/external_nrf52840-mbs.cmake`

Em `include_directories`:

```cmake
    ${EXT_SDK}/components/libraries/lk_mbr_flash
```

Em `add_mcu_sources` (junto às outras fontes):

```cmake
    ${EXT_SDK}/components/libraries/lk_mbr_flash/lk_mbr_flash_params.c
```

(`EXT_SDK` já aponta para `bootloader_change_address`.)

### 2.2 `projects/boot_secure/src/core/bootloader/nrf52840-mbs/bootloader/nrf_bootloader.c`

- Include:

```c
#include "lk_mbr_flash_params.h"
```

- Dentro de `if (dfu_enter) { ... }`, **depois** de `nrf_dfu_init(dfu_observer)` com sucesso e **antes** de `loop_forever()`:

```c
        {
            uint32_t const mbr_set = lk_mbr_flash_params_set_boot_secure();
            if (mbr_set != NRF_SUCCESS)
            {
                NRF_LOG_ERROR("lk_mbr_flash_params_set_boot_secure after DFU init failed: 0x%x", mbr_set);
            }
            else
            {
                NRF_LOG_INFO("MBR 0xFF8/0xFFC set after DFU init");
            }
        }
```

---

## 3. Commits sugeridos

1. No **submódulo** `bootloader_change_address`: commit com `lk_mbr_flash/` + alterações em `nrf_bootloader_app_start_final.c` e `nrf_dfu_mbr.c`.
2. No **loopkey-nrf51**: commit com CMake + `nrf_bootloader.c` e **ponteiro do submódulo** atualizado (`git add ext/sdk_custom/nordic/bootloader_change_address`).

---

## 4. Include path

O compilador precisa de `-I.../components/libraries/lk_mbr_flash` (o CMake acima faz isso). O include nos .c é sempre:

```c
#include "lk_mbr_flash_params.h"
```
