/**
 * @file bootloader_debug_uart.c
 * @brief Bit-banged UART debug library matching ble_uart implementation
 */

#include "bootloader_debug_uart.h"
#include "nrf_gpio.h"
#include "nrf_delay.h"

#define DEBUG_UART_PIN          4                                           /**< P0.04 for debug UART output */
#define DEBUG_UART_BAUD         9600                                        /**< 9600 baud for reliable communication */
#define DEBUG_UART_BIT_TIME_US  (1000000 / DEBUG_UART_BAUD)                /**< Bit time in microseconds (~104us) */

static bool uart_initialized = false;

void bootloader_debug_uart_init(void)
{
    if (uart_initialized) {
        return;
    }
    
    // Configure pin as output, start HIGH (idle state) - SAME AS BLE_UART
    nrf_gpio_cfg_output(DEBUG_UART_PIN);
    nrf_gpio_pin_set(DEBUG_UART_PIN);
    
    // Wait to ensure line is stable - SAME AS BLE_UART
    nrf_delay_ms(10);
    
    uart_initialized = true;
    
    // Also configure LED for visual feedback
    nrf_gpio_cfg_output(13);  // LED 1
    nrf_gpio_pin_clear(13);   // LED ON
    
    // Send test message - SAME PATTERN AS BLE_UART
    bootloader_debug_uart_puts("=== BOOTLOADER DEBUG UART ===\r\n");
    bootloader_debug_uart_puts("Bit-banged @ 9600 baud\r\n");
    bootloader_debug_uart_puts("P0.04 - Same as ble_uart\r\n");
    bootloader_debug_uart_puts("Testing 1-2-3...\r\n\r\n");
    
    nrf_gpio_pin_set(13);  // LED OFF when done
}

void bootloader_debug_uart_putc(char c)
{
    if (!uart_initialized) {
        return;
    }
    
    uint8_t data = (uint8_t)c;
    
    // Start bit (LOW) - SAME AS BLE_UART
    nrf_gpio_pin_clear(DEBUG_UART_PIN);
    nrf_delay_us(DEBUG_UART_BIT_TIME_US);
    
    // Data bits (LSB first) - SAME AS BLE_UART
    for (int i = 0; i < 8; i++) {
        if (data & (1 << i)) {
            nrf_gpio_pin_set(DEBUG_UART_PIN);    // HIGH for '1'
        } else {
            nrf_gpio_pin_clear(DEBUG_UART_PIN);  // LOW for '0'
        }
        nrf_delay_us(DEBUG_UART_BIT_TIME_US);
    }
    
    // Stop bit (HIGH) - SAME AS BLE_UART
    nrf_gpio_pin_set(DEBUG_UART_PIN);
    nrf_delay_us(DEBUG_UART_BIT_TIME_US);
}

void bootloader_debug_uart_puts(const char* str)
{
    if (!str || !uart_initialized) {
        return;
    }
    
    while(*str) {
        bootloader_debug_uart_putc(*str++);
        // Small delay between characters for reliability - SAME AS BLE_UART
        nrf_delay_ms(1);
    }
}

void bootloader_debug_uart_hex(uint32_t value)
{
    if (!uart_initialized) {
        return;
    }
    
    const char hex[] = "0123456789ABCDEF";
    bootloader_debug_uart_puts("0x");
    
    for(int i = 7; i >= 0; i--) {
        bootloader_debug_uart_putc(hex[(value >> (i*4)) & 0xF]);
    }
}

void bootloader_debug_uart_dec(uint32_t value)
{
    if (!uart_initialized) {
        return;
    }
    
    if (value == 0) {
        bootloader_debug_uart_putc('0');
        return;
    }
    
    char buffer[12];
    int pos = 0;
    
    while (value > 0) {
        buffer[pos++] = '0' + (value % 10);
        value /= 10;
    }
    
    for (int i = pos - 1; i >= 0; i--) {
        bootloader_debug_uart_putc(buffer[i]);
    }
}

void bootloader_debug_uart_msg_hex(const char* prefix, uint32_t value, const char* suffix)
{
    if (!uart_initialized) {
        return;
    }
    
    if (prefix) {
        bootloader_debug_uart_puts(prefix);
    }
    
    bootloader_debug_uart_hex(value);
    
    if (suffix) {
        bootloader_debug_uart_puts(suffix);
    }
}