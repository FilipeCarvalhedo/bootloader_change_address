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

#include "bootloader_debug_uart.h"
#include "nrf_gpio.h"
#include "nrf_delay.h"
#include <stdio.h>
#include <stdarg.h>
#include <string.h>

// Debug UART configuration
#define DEBUG_UART_PIN                      4                                       /**< P0.04 for debug UART output */
#define DEBUG_UART_BAUD                     9600                                    /**< 9600 baud for reliable communication */
#define DEBUG_UART_BIT_TIME_US              (1000000 / DEBUG_UART_BAUD)            /**< Bit time in microseconds (~104us) */

static bool m_uart_initialized = false;

void bootloader_debug_uart_init(void)
{
    if (m_uart_initialized) return;
    
    // Configure pin as output, initially high (idle state)
    nrf_gpio_cfg_output(DEBUG_UART_PIN);
    nrf_gpio_pin_set(DEBUG_UART_PIN);
    
    // Brief delay to stabilize
    nrf_delay_us(DEBUG_UART_BIT_TIME_US * 10);
    
    m_uart_initialized = true;
}

void bootloader_debug_uart_putc(char ch)
{
    if (!m_uart_initialized) {
        bootloader_debug_uart_init();
    }
    
    uint32_t data = ch;
    
    // Start bit (low)
    nrf_gpio_pin_clear(DEBUG_UART_PIN);
    nrf_delay_us(DEBUG_UART_BIT_TIME_US);
    
    // 8 data bits (LSB first)
    for (int i = 0; i < 8; i++) {
        if (data & (1 << i)) {
            nrf_gpio_pin_set(DEBUG_UART_PIN);
        } else {
            nrf_gpio_pin_clear(DEBUG_UART_PIN);
        }
        nrf_delay_us(DEBUG_UART_BIT_TIME_US);
    }
    
    // Stop bit (high)
    nrf_gpio_pin_set(DEBUG_UART_PIN);
    nrf_delay_us(DEBUG_UART_BIT_TIME_US);
}

void bootloader_debug_uart_puts(const char* str)
{
    if (!str) return;
    
    while (*str) {
        bootloader_debug_uart_putc(*str++);
    }
}

void bootloader_debug_uart_printf(const char* fmt, ...)
{
    char buffer[256];
    va_list args;
    
    va_start(args, fmt);
    int len = vsnprintf(buffer, sizeof(buffer), fmt, args);
    va_end(args);
    
    if (len > 0 && len < sizeof(buffer)) {
        bootloader_debug_uart_puts(buffer);
    }
}

void bootloader_debug_uart_msg_hex(const char* prefix, uint32_t value, const char* suffix)
{
    char buffer[64];
    
    if (prefix) {
        bootloader_debug_uart_puts(prefix);
    }
    
    snprintf(buffer, sizeof(buffer), "0x%08lX", (unsigned long)value);
    bootloader_debug_uart_puts(buffer);
    
    if (suffix) {
        bootloader_debug_uart_puts(suffix);
    }
}