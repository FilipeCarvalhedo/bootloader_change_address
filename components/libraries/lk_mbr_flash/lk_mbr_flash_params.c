/**
 * @file lk_mbr_flash_params.c
 */

#include "lk_mbr_flash_params.h"

#include "nrf_dfu_types.h"
#include "nrf_error.h"
#include "nrf_mbr.h"
#include "nrf_nvmc.h"
#include "nrf.h"

/** VTOR durante erase/write da página 0 (código a correr não pode estar na página 0). */
#define LK_MBR_PATCH_VTOR LK_MBR_FLASH_BOOT_SECURE_ADDR

static uint32_t lk_mbr_patch_page0(uint32_t word_ff8, uint32_t word_ffc)
{
    static uint32_t page_backup[CODE_PAGE_SIZE / sizeof(uint32_t)];
    uint32_t        num_words = CODE_PAGE_SIZE / sizeof(uint32_t);

    for (uint32_t i = 0; i < num_words; i++)
    {
        page_backup[i] = ((volatile uint32_t *)0)[i];
    }

    page_backup[MBR_BOOTLOADER_ADDR / sizeof(uint32_t)] = word_ff8;
    page_backup[MBR_PARAM_PAGE_ADDR / sizeof(uint32_t)]  = word_ffc;

    __disable_irq();
    SCB->VTOR = LK_MBR_PATCH_VTOR;
    __DSB();
    __ISB();

    nrf_nvmc_page_erase(0);
    nrf_nvmc_write_words(0, page_backup, num_words);

    uint32_t const got8 = *(volatile uint32_t *)MBR_BOOTLOADER_ADDR;
    uint32_t const gotc = *(volatile uint32_t *)MBR_PARAM_PAGE_ADDR;
    if (got8 != word_ff8 || gotc != word_ffc)
    {
        return NRF_ERROR_INTERNAL;
    }

    return NRF_SUCCESS;
}

uint32_t lk_mbr_flash_params_set_boot_secure(void)
{
    uint32_t const want_bl    = LK_MBR_FLASH_BOOT_SECURE_ADDR;
    uint32_t const want_param = NRF_MBR_PARAMS_PAGE_ADDRESS;

    uint32_t cur_bl    = *(volatile uint32_t *)MBR_BOOTLOADER_ADDR;
    uint32_t cur_param = *(volatile uint32_t *)MBR_PARAM_PAGE_ADDR;

    if (cur_bl == want_bl && cur_param == want_param)
    {
        return NRF_SUCCESS;
    }

    return lk_mbr_patch_page0(want_bl, want_param);
}

uint32_t lk_mbr_flash_params_clear(void)
{
    uint32_t cur_bl    = *(volatile uint32_t *)MBR_BOOTLOADER_ADDR;
    uint32_t cur_param = *(volatile uint32_t *)MBR_PARAM_PAGE_ADDR;

    if (cur_bl == 0xFFFFFFFFUL && cur_param == 0xFFFFFFFFUL)
    {
        return NRF_SUCCESS;
    }

    return lk_mbr_patch_page0(0xFFFFFFFFUL, 0xFFFFFFFFUL);
}
