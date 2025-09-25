/**
 * Copyright (c) 2023, Nordic Semiconductor ASA
 *
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without modification,
 * are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice, this
 *    list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form, except as embedded into a Nordic
 *    Semiconductor ASA integrated circuit in a product or a software update for
 *    such product, must reproduce the above copyright notice, this list of
 *    conditions and the following disclaimer in the documentation and/or other
 *    materials provided with the distribution.
 *
 * 3. Neither the name of Nordic Semiconductor ASA nor the names of its
 *    contributors may be used to endorse or promote products derived from this
 *    software without specific prior written permission.
 *
 * 4. This software, with or without modification, must only be used with a
 *    Nordic Semiconductor ASA integrated circuit.
 *
 * 5. Any software provided in binary form under this license must not be reverse
 *    engineered, decompiled, modified and/or disassembled.
 *
 * THIS SOFTWARE IS PROVIDED BY NORDIC SEMICONDUCTOR ASA "AS IS" AND ANY EXPRESS
 * OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY, NONINFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL NORDIC SEMICONDUCTOR ASA OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
 * GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 */

/**@file
 *
 * @defgroup bootloader_debug_uart Bootloader Debug UART
 * @{
 * @ingroup nrf_bootloader
 * @brief Bootloader debug UART functionality.
 */

#ifndef BOOTLOADER_DEBUG_UART_H__
#define BOOTLOADER_DEBUG_UART_H__

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Function for initializing the debug UART.
 */
void bootloader_debug_uart_init(void);

/**
 * @brief Function for sending a single character via debug UART.
 *
 * @param[in] ch Character to send.
 */
void bootloader_debug_uart_putc(char ch);

/**
 * @brief Function for sending a string via debug UART.
 *
 * @param[in] str String to send.
 */
void bootloader_debug_uart_puts(const char* str);

/**
 * @brief Function for sending formatted string via debug UART.
 *
 * @param[in] fmt Format string.
 * @param[in] ... Arguments for format string.
 */
void bootloader_debug_uart_printf(const char* fmt, ...);

/**
 * @brief Function for sending a message with hex value via debug UART.
 *
 * @param[in] prefix Prefix string.
 * @param[in] value Hex value to display.
 * @param[in] suffix Suffix string.
 */
void bootloader_debug_uart_msg_hex(const char* prefix, uint32_t value, const char* suffix);

#ifdef __cplusplus
}
#endif

#endif // BOOTLOADER_DEBUG_UART_H__

/** @} */