cmake_minimum_required(VERSION 3.15)

# Set toolchain before project() call
set(CMAKE_TOOLCHAIN_FILE "${CMAKE_CURRENT_SOURCE_DIR}/cmake/arm-none-eabi-gcc.cmake")

# Project definition
project(ble_app_uart_pca10056_s140 
    LANGUAGES C ASM
    VERSION 1.0.0
    DESCRIPTION "Nordic nRF52840 BLE UART Application with SoftDevice S140"
)

# SDK root path
set(SDK_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../../..")

# Project directories
set(PROJ_DIR "${CMAKE_CURRENT_SOURCE_DIR}")
set(CONFIG_DIR "${CMAKE_CURRENT_SOURCE_DIR}/config")

# Target MCU configuration
set(NRF_TARGET "nrf52840")
set(SOFTDEVICE "s140")
set(BOARD "PCA10056")

# Source files
set(SOURCES
    # MDK and startup
    ${SDK_ROOT}/modules/nrfx/mdk/gcc_startup_nrf52840.S
    ${SDK_ROOT}/modules/nrfx/mdk/system_nrf52840.c
    
    # Logging
    ${SDK_ROOT}/components/libraries/log/src/nrf_log_backend_rtt.c
    ${SDK_ROOT}/components/libraries/log/src/nrf_log_backend_serial.c
    ${SDK_ROOT}/components/libraries/log/src/nrf_log_default_backends.c
    ${SDK_ROOT}/components/libraries/log/src/nrf_log_frontend.c
    ${SDK_ROOT}/components/libraries/log/src/nrf_log_str_formatter.c
    
    # Application components
    ${SDK_ROOT}/components/libraries/button/app_button.c
    ${SDK_ROOT}/components/libraries/fifo/app_fifo.c
    ${SDK_ROOT}/components/libraries/scheduler/app_scheduler.c
    ${SDK_ROOT}/components/libraries/timer/app_timer2.c
    ${SDK_ROOT}/components/libraries/uart/app_uart_fifo.c
    ${SDK_ROOT}/components/libraries/timer/drv_rtc.c
    ${SDK_ROOT}/components/libraries/uart/retarget.c
    
    # Board support and BSP
    ${SDK_ROOT}/components/boards/boards.c
    ${SDK_ROOT}/components/libraries/bsp/bsp.c
    ${SDK_ROOT}/components/libraries/bsp/bsp_btn_ble.c
    
    # Utilities
    ${SDK_ROOT}/components/libraries/util/app_error.c
    ${SDK_ROOT}/components/libraries/util/app_error_handler_gcc.c
    ${SDK_ROOT}/components/libraries/util/app_error_weak.c
    ${SDK_ROOT}/components/libraries/util/app_util_platform.c
    ${SDK_ROOT}/components/libraries/util/nrf_assert.c
    ${SDK_ROOT}/components/libraries/strerror/nrf_strerror.c
    ${SDK_ROOT}/components/libraries/hardfault/hardfault_implementation.c
    
    # Atomic operations and memory
    ${SDK_ROOT}/components/libraries/atomic_fifo/nrf_atfifo.c
    ${SDK_ROOT}/components/libraries/atomic_flags/nrf_atflags.c
    ${SDK_ROOT}/components/libraries/atomic/nrf_atomic.c
    ${SDK_ROOT}/components/libraries/balloc/nrf_balloc.c
    ${SDK_ROOT}/components/libraries/memobj/nrf_memobj.c
    ${SDK_ROOT}/components/libraries/pwr_mgmt/nrf_pwr_mgmt.c
    ${SDK_ROOT}/components/libraries/ringbuf/nrf_ringbuf.c
    ${SDK_ROOT}/components/libraries/experimental_section_vars/nrf_section_iter.c
    ${SDK_ROOT}/components/libraries/sortlist/nrf_sortlist.c
    
    # Printf support
    ${SDK_ROOT}/external/fprintf/nrf_fprintf.c
    ${SDK_ROOT}/external/fprintf/nrf_fprintf_format.c
    
    # SEGGER RTT
    ${SDK_ROOT}/external/segger_rtt/SEGGER_RTT.c
    ${SDK_ROOT}/external/segger_rtt/SEGGER_RTT_Syscalls_GCC.c
    ${SDK_ROOT}/external/segger_rtt/SEGGER_RTT_printf.c
    
    # NRFX drivers and legacy
    ${SDK_ROOT}/integration/nrfx/legacy/nrf_drv_clock.c
    ${SDK_ROOT}/integration/nrfx/legacy/nrf_drv_uart.c
    ${SDK_ROOT}/modules/nrfx/soc/nrfx_atomic.c
    ${SDK_ROOT}/modules/nrfx/drivers/src/nrfx_clock.c
    ${SDK_ROOT}/modules/nrfx/drivers/src/nrfx_gpiote.c
    ${SDK_ROOT}/modules/nrfx/drivers/src/prs/nrfx_prs.c
    ${SDK_ROOT}/modules/nrfx/drivers/src/nrfx_uart.c
    ${SDK_ROOT}/modules/nrfx/drivers/src/nrfx_uarte.c
    
    # BLE stack components
    ${SDK_ROOT}/components/ble/common/ble_advdata.c
    ${SDK_ROOT}/components/ble/ble_advertising/ble_advertising.c
    ${SDK_ROOT}/components/ble/common/ble_conn_params.c
    ${SDK_ROOT}/components/ble/common/ble_conn_state.c
    ${SDK_ROOT}/components/ble/ble_link_ctx_manager/ble_link_ctx_manager.c
    ${SDK_ROOT}/components/ble/common/ble_srv_common.c
    ${SDK_ROOT}/components/ble/nrf_ble_gatt/nrf_ble_gatt.c
    ${SDK_ROOT}/components/ble/nrf_ble_qwr/nrf_ble_qwr.c
    ${SDK_ROOT}/external/utf_converter/utf.c
    ${SDK_ROOT}/components/ble/ble_services/ble_nus/ble_nus.c
    
    # SoftDevice
    ${SDK_ROOT}/components/softdevice/common/nrf_sdh.c
    ${SDK_ROOT}/components/softdevice/common/nrf_sdh_ble.c
    ${SDK_ROOT}/components/softdevice/common/nrf_sdh_soc.c
    
    # Main application
    ${PROJ_DIR}/main.c
)

# Include directories
set(INCLUDE_DIRS
    # Local config and project
    ${CONFIG_DIR}
    ${PROJ_DIR}
    
    # SDK core components
    ${SDK_ROOT}/components
    ${SDK_ROOT}/modules/nrfx/mdk
    ${SDK_ROOT}/modules/nrfx/hal
    ${SDK_ROOT}/modules/nrfx
    ${SDK_ROOT}/modules/nrfx/drivers/include
    ${SDK_ROOT}/integration/nrfx
    ${SDK_ROOT}/integration/nrfx/legacy
    
    # SoftDevice headers
    ${SDK_ROOT}/components/softdevice/s140/headers
    ${SDK_ROOT}/components/softdevice/s140/headers/nrf52
    ${SDK_ROOT}/components/softdevice/common
    
    # Libraries
    ${SDK_ROOT}/components/libraries/strerror
    ${SDK_ROOT}/components/libraries/util
    ${SDK_ROOT}/components/libraries/balloc
    ${SDK_ROOT}/components/libraries/ringbuf
    ${SDK_ROOT}/components/libraries/bsp
    ${SDK_ROOT}/components/libraries/log
    ${SDK_ROOT}/components/libraries/log/src
    ${SDK_ROOT}/components/libraries/experimental_section_vars
    ${SDK_ROOT}/components/libraries/delay
    ${SDK_ROOT}/components/libraries/atomic
    ${SDK_ROOT}/components/libraries/atomic_fifo
    ${SDK_ROOT}/components/libraries/atomic_flags
    ${SDK_ROOT}/components/libraries/memobj
    ${SDK_ROOT}/components/libraries/pwr_mgmt
    ${SDK_ROOT}/components/libraries/queue
    ${SDK_ROOT}/components/libraries/scheduler
    ${SDK_ROOT}/components/libraries/slip
    ${SDK_ROOT}/components/libraries/sortlist
    ${SDK_ROOT}/components/libraries/timer
    ${SDK_ROOT}/components/libraries/uart
    ${SDK_ROOT}/components/libraries/button
    ${SDK_ROOT}/components/libraries/fifo
    ${SDK_ROOT}/components/libraries/hardfault
    ${SDK_ROOT}/components/libraries/gpiote
    ${SDK_ROOT}/components/libraries/mutex
    
    # BLE components
    ${SDK_ROOT}/components/ble/common
    ${SDK_ROOT}/components/ble/ble_advertising
    ${SDK_ROOT}/components/ble/ble_link_ctx_manager
    ${SDK_ROOT}/components/ble/nrf_ble_gatt
    ${SDK_ROOT}/components/ble/nrf_ble_qwr
    ${SDK_ROOT}/components/ble/ble_services/ble_nus
    
    # Boards and toolchain
    ${SDK_ROOT}/components/boards
    ${SDK_ROOT}/components/toolchain/cmsis/include
    
    # External components
    ${SDK_ROOT}/external/fprintf
    ${SDK_ROOT}/external/segger_rtt
    ${SDK_ROOT}/external/utf_converter
)

# Create the executable target
add_executable(${PROJECT_NAME} ${SOURCES})

# Set target properties
set_target_properties(${PROJECT_NAME} PROPERTIES
    OUTPUT_NAME "nrf52840_xxaa"
    SUFFIX ".elf"
)

# Include directories
target_include_directories(${PROJECT_NAME} PRIVATE ${INCLUDE_DIRS})

# Compiler definitions
target_compile_definitions(${PROJECT_NAME} PRIVATE
    APP_TIMER_V2
    APP_TIMER_V2_RTC1_ENABLED
    BOARD_PCA10056
    CONFIG_GPIO_AS_PINRESET
    FLOAT_ABI_HARD
    NRF52840_XXAA
    NRF_SD_BLE_API_VERSION=7
    S140
    SOFTDEVICE_PRESENT
    __HEAP_SIZE=8192
    __STACK_SIZE=8192
)

# Compiler options (toolchain already provides most flags)
target_compile_options(${PROJECT_NAME} PRIVATE
    -O3
    -g3
)

# Linker options
target_link_options(${PROJECT_NAME} PRIVATE
    -L${SDK_ROOT}/modules/nrfx/mdk
    -T${CMAKE_CURRENT_SOURCE_DIR}/../armgcc/ble_app_uart_gcc_nrf52.ld
)

# Link libraries
target_link_libraries(${PROJECT_NAME} PRIVATE
    c
    nosys
    m
)

# Custom commands for post-build
add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND ${CMAKE_OBJCOPY} -O ihex $<TARGET_FILE:${PROJECT_NAME}> ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}.hex
    COMMAND ${CMAKE_OBJCOPY} -O binary $<TARGET_FILE:${PROJECT_NAME}> ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}.bin
    COMMENT "Creating HEX and BIN files"
)

# Custom targets for flashing
add_custom_target(flash
    COMMAND nrfjprog -f nrf52 --program ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}.hex --sectorerase
    COMMAND nrfjprog -f nrf52 --reset
    DEPENDS ${PROJECT_NAME}
    COMMENT "Flashing the program"
)

add_custom_target(flash_softdevice
    COMMAND nrfjprog -f nrf52 --program ${SDK_ROOT}/components/softdevice/s140/hex/s140_nrf52_7.2.0_softdevice.hex --sectorerase
    COMMAND nrfjprog -f nrf52 --reset
    COMMENT "Flashing the SoftDevice"
)

add_custom_target(erase
    COMMAND nrfjprog -f nrf52 --eraseall
    COMMENT "Erasing chip"
)

# Print build information
message(STATUS "Project: ${PROJECT_NAME}")
message(STATUS "Target MCU: ${NRF_TARGET}")
message(STATUS "SoftDevice: ${SOFTDEVICE}")
message(STATUS "Board: ${BOARD}")
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}") 