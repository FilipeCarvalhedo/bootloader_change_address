/**
 * @file lk_mbr_flash_params.h
 * @brief Escrita segura das palavras do MBR em flash (0xFF8 / 0xFFC) no nRF52.
 *
 * - lk_mbr_flash_params_set_boot_secure(): em nrf_bootloader_fw_activation.c — sd_activate() (update SoftDevice)
 *   e bl_activate() imediatamente antes de nrf_dfu_mbr_copy_bl. Não em updates só de aplicação (app_activate).
 * - lk_mbr_flash_params_clear(): antes da aplicação arrancar (nrf_bootloader_app_start_final), para
 *   restaurar boot por UICR (ex. chainload CB → boot_secure).
 *
 * Página 0: backup, patch, VTOR -> boot_secure, erase, write. Sem nrf_log.
 */
#ifndef LK_MBR_FLASH_PARAMS_H__
#define LK_MBR_FLASH_PARAMS_H__

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#ifndef LK_MBR_FLASH_BOOT_SECURE_ADDR
/** Endereço do vector table do boot_secure (segundo estágio); deve coincidir com o linker. */
#define LK_MBR_FLASH_BOOT_SECURE_ADDR (0x00027000UL)
#endif

/**
 * @brief Define 0xFF8 = LK_MBR_FLASH_BOOT_SECURE_ADDR e 0xFFC = página de params do MBR (NRF_MBR_PARAMS_PAGE_ADDRESS).
 *
 * Usar antes de SD_MBR_COMMAND_COPY_BL. Se já estiver correto, não escreve na flash.
 *
 * @return NRF_SUCCESS ou NRF_ERROR_INTERNAL.
 */
uint32_t lk_mbr_flash_params_set_boot_secure(void);

/**
 * @brief Define 0xFF8 e 0xFFC para 0xFFFFFFFF (MBR volta a usar UICR na cadeia de boot).
 *
 * Se já estiverem apagadas, não escreve na flash.
 *
 * @return NRF_SUCCESS ou NRF_ERROR_INTERNAL.
 */
uint32_t lk_mbr_flash_params_clear(void);

#ifdef __cplusplus
}
#endif

#endif /* LK_MBR_FLASH_PARAMS_H__ */
