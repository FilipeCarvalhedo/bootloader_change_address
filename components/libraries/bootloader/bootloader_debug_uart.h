/**
 * @file bootloader_debug_uart.h
 * @brief Simple UART debug library for bootloader using SDK app_uart
 */

#ifndef BOOTLOADER_DEBUG_UART_H
#define BOOTLOADER_DEBUG_UART_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @brief Initialize UART for bootloader debug
 */
void bootloader_debug_uart_init(void);

/**
 * @brief Send a character via UART
 * @param c Character to send
 */
void bootloader_debug_uart_putc(char c);

/**
 * @brief Send a string via UART
 * @param str String to send
 */
void bootloader_debug_uart_puts(const char* str);

/**
 * @brief Send a 32-bit value as hexadecimal
 * @param value Value to send
 */
void bootloader_debug_uart_hex(uint32_t value);

/**
 * @brief Send a 32-bit value as decimal
 * @param value Value to send
 */
void bootloader_debug_uart_dec(uint32_t value);

/**
 * @brief Send a message with hex value
 * @param msg Prefix message
 * @param value Hex value
 * @param suffix Suffix message
 */
void bootloader_debug_uart_msg_hex(const char* msg, uint32_t value, const char* suffix);

#endif // BOOTLOADER_DEBUG_UART_H