cmake_minimum_required(VERSION 3.15)

# Set toolchain before project() call
set(CMAKE_TOOLCHAIN_FILE "${CMAKE_CURRENT_SOURCE_DIR}/cmake/arm-none-eabi-gcc.cmake")

# Project definition
project(secure_bootloader_ble_s140_pca10056 
    LANGUAGES C ASM
    VERSION 1.0.0
    DESCRIPTION "Nordic nRF52840 Secure Bootloader with BLE DFU support"
)

# SDK root path
set(SDK_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../../..")

# Project directories
set(PROJ_DIR "${CMAKE_CURRENT_SOURCE_DIR}")
set(CONFIG_DIR "${CMAKE_CURRENT_SOURCE_DIR}/pca10056_s140_ble/config")

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
    ${SDK_ROOT}/components/libraries/log/src/nrf_log_frontend.c
    ${SDK_ROOT}/components/libraries/log/src/nrf_log_str_formatter.c
    
    # Utilities
    ${SDK_ROOT}/components/libraries/util/app_error_weak.c
    ${SDK_ROOT}/components/libraries/util/app_util_platform.c
    ${SDK_ROOT}/components/libraries/util/nrf_assert.c
    ${SDK_ROOT}/components/libraries/scheduler/app_scheduler.c
    ${SDK_ROOT}/components/libraries/crc32/crc32.c
    ${SDK_ROOT}/components/libraries/mem_manager/mem_manager.c
    ${SDK_ROOT}/components/libraries/strerror/nrf_strerror.c
    
    # Atomic operations and FIFO
    ${SDK_ROOT}/components/libraries/atomic_fifo/nrf_atfifo.c
    ${SDK_ROOT}/components/libraries/atomic/nrf_atomic.c
    ${SDK_ROOT}/components/libraries/balloc/nrf_balloc.c
    ${SDK_ROOT}/components/libraries/queue/nrf_queue.c
    ${SDK_ROOT}/components/libraries/ringbuf/nrf_ringbuf.c
    ${SDK_ROOT}/components/libraries/memobj/nrf_memobj.c
    
    # Storage
    ${SDK_ROOT}/components/libraries/fstorage/nrf_fstorage.c
    ${SDK_ROOT}/components/libraries/fstorage/nrf_fstorage_nvmc.c
    ${SDK_ROOT}/components/libraries/fstorage/nrf_fstorage_sd.c
    
    # Section variables
    ${SDK_ROOT}/components/libraries/experimental_section_vars/nrf_section_iter.c
    
    # Printf support
    ${SDK_ROOT}/external/fprintf/nrf_fprintf.c
    ${SDK_ROOT}/external/fprintf/nrf_fprintf_format.c
    
    # Cryptography (CC310 BL backend)
    ${SDK_ROOT}/components/libraries/crypto/backend/cc310_bl/cc310_bl_backend_ecc.c
    ${SDK_ROOT}/components/libraries/crypto/backend/cc310_bl/cc310_bl_backend_ecdsa.c
    ${SDK_ROOT}/components/libraries/crypto/backend/cc310_bl/cc310_bl_backend_hash.c
    ${SDK_ROOT}/components/libraries/crypto/backend/cc310_bl/cc310_bl_backend_init.c
    ${SDK_ROOT}/components/libraries/crypto/backend/cc310_bl/cc310_bl_backend_shared.c
    
    # Cryptography (Oberon backend)
    ${SDK_ROOT}/components/libraries/crypto/backend/oberon/oberon_backend_chacha_poly_aead.c
    ${SDK_ROOT}/components/libraries/crypto/backend/oberon/oberon_backend_ecc.c
    ${SDK_ROOT}/components/libraries/crypto/backend/oberon/oberon_backend_ecdh.c
    ${SDK_ROOT}/components/libraries/crypto/backend/oberon/oberon_backend_ecdsa.c
    ${SDK_ROOT}/components/libraries/crypto/backend/oberon/oberon_backend_eddsa.c
    ${SDK_ROOT}/components/libraries/crypto/backend/oberon/oberon_backend_hash.c
    ${SDK_ROOT}/components/libraries/crypto/backend/oberon/oberon_backend_hmac.c
    
    # Crypto core
    ${SDK_ROOT}/components/libraries/crypto/nrf_crypto_ecc.c
    ${SDK_ROOT}/components/libraries/crypto/nrf_crypto_ecdsa.c
    ${SDK_ROOT}/components/libraries/crypto/nrf_crypto_hash.c
    ${SDK_ROOT}/components/libraries/crypto/nrf_crypto_init.c
    ${SDK_ROOT}/components/libraries/crypto/nrf_crypto_shared.c
    
    # Board support
    ${SDK_ROOT}/components/boards/boards.c
    
    # SoftDevice
    ${SDK_ROOT}/components/softdevice/common/nrf_sdh.c
    ${SDK_ROOT}/components/softdevice/common/nrf_sdh_ble.c
    ${SDK_ROOT}/components/softdevice/common/nrf_sdh_soc.c
    
    # NRFX HAL
    ${SDK_ROOT}/modules/nrfx/hal/nrf_nvmc.c
    ${SDK_ROOT}/modules/nrfx/soc/nrfx_atomic.c
    
    # Main application
    ${PROJ_DIR}/../dfu_public_key.c
    ${PROJ_DIR}/main.c
    
    # DFU
    ${SDK_ROOT}/components/libraries/bootloader/dfu/nrf_dfu_svci.c
    ${SDK_ROOT}/components/libraries/bootloader/dfu/nrf_dfu_svci_handler.c
    ${SDK_ROOT}/components/libraries/svc/nrf_svc_handler.c
    ${SDK_ROOT}/components/ble/common/ble_srv_common.c
    
    # Bootloader
    ${SDK_ROOT}/components/libraries/bootloader/nrf_bootloader.c
    ${SDK_ROOT}/components/libraries/bootloader/nrf_bootloader_app_start.c
    ${SDK_ROOT}/components/libraries/bootloader/nrf_bootloader_app_start_final.c
    ${SDK_ROOT}/components/libraries/bootloader/nrf_bootloader_dfu_timers.c
    ${SDK_ROOT}/components/libraries/bootloader/nrf_bootloader_fw_activation.c
    ${SDK_ROOT}/components/libraries/bootloader/nrf_bootloader_info.c
    ${SDK_ROOT}/components/libraries/bootloader/nrf_bootloader_wdt.c
    
    # Protocol Buffers
    ${SDK_ROOT}/external/nano-pb/pb_common.c
    ${SDK_ROOT}/external/nano-pb/pb_decode.c
    ${SDK_ROOT}/components/libraries/bootloader/dfu/dfu-cc.pb.c
    
    # DFU implementation
    ${SDK_ROOT}/components/libraries/bootloader/dfu/nrf_dfu.c
    ${SDK_ROOT}/components/libraries/bootloader/ble_dfu/nrf_dfu_ble.c
    ${SDK_ROOT}/components/libraries/bootloader/dfu/nrf_dfu_flash.c
    ${SDK_ROOT}/components/libraries/bootloader/dfu/nrf_dfu_handling_error.c
    ${SDK_ROOT}/components/libraries/bootloader/dfu/nrf_dfu_mbr.c
    ${SDK_ROOT}/components/libraries/bootloader/dfu/nrf_dfu_req_handler.c
    ${SDK_ROOT}/components/libraries/bootloader/dfu/nrf_dfu_settings.c
    ${SDK_ROOT}/components/libraries/bootloader/dfu/nrf_dfu_settings_svci.c
    ${SDK_ROOT}/components/libraries/bootloader/dfu/nrf_dfu_transport.c
    ${SDK_ROOT}/components/libraries/bootloader/dfu/nrf_dfu_utils.c
    ${SDK_ROOT}/components/libraries/bootloader/dfu/nrf_dfu_validation.c
    ${SDK_ROOT}/components/libraries/bootloader/dfu/nrf_dfu_ver_validation.c
)

# Include directories
set(INCLUDE_DIRS
    # Local config
    ${CONFIG_DIR}
    ${PROJ_DIR}
    
    # SDK includes
    ${SDK_ROOT}/components/libraries/crypto/backend/micro_ecc
    ${SDK_ROOT}/components/libraries/memobj
    ${SDK_ROOT}/components/softdevice/s140/headers/nrf52
    ${SDK_ROOT}/components/libraries/crc32
    ${SDK_ROOT}/components/libraries/experimental_section_vars
    ${SDK_ROOT}/components/libraries/mem_manager
    ${SDK_ROOT}/components/libraries/fstorage
    ${SDK_ROOT}/components/libraries/util
    ${SDK_ROOT}/modules/nrfx
    ${SDK_ROOT}/external/nrf_oberon/include
    ${SDK_ROOT}/components/libraries/crypto/backend/oberon
    ${SDK_ROOT}/components/libraries/crypto/backend/cifra
    ${SDK_ROOT}/components/libraries/atomic
    ${SDK_ROOT}/integration/nrfx
    ${SDK_ROOT}/components/libraries/crypto/backend/cc310_bl
    ${SDK_ROOT}/external/nrf_cc310/include
    ${SDK_ROOT}/components/libraries/log/src
    ${SDK_ROOT}/components/libraries/bootloader/dfu
    ${SDK_ROOT}/components/ble/common
    ${SDK_ROOT}/components/libraries/delay
    ${SDK_ROOT}/components/libraries/svc
    ${SDK_ROOT}/components/libraries/stack_info
    ${SDK_ROOT}/components/libraries/crypto/backend/nrf_hw
    ${SDK_ROOT}/components/libraries/log
    ${SDK_ROOT}/external/nrf_oberon
    ${SDK_ROOT}/components/libraries/strerror
    ${SDK_ROOT}/components/libraries/crypto/backend/mbedtls
    ${SDK_ROOT}/components/boards
    ${SDK_ROOT}/components/libraries/crypto/backend/cc310
    ${SDK_ROOT}/components/libraries/bootloader
    ${SDK_ROOT}/components/softdevice/s140/headers
    ${SDK_ROOT}/components/libraries/crypto
    ${SDK_ROOT}/components/libraries/crypto/backend/optiga
    ${SDK_ROOT}/components/libraries/scheduler
    ${SDK_ROOT}/external/nrf_cc310_bl/include
    ${SDK_ROOT}/modules/nrfx/hal
    ${SDK_ROOT}/external/fprintf
    ${SDK_ROOT}/components/toolchain/cmsis/include
    ${SDK_ROOT}/components/libraries/balloc
    ${SDK_ROOT}/components/libraries/atomic_fifo
    ${SDK_ROOT}/components/libraries/crypto/backend/nrf_sw
    ${SDK_ROOT}/modules/nrfx/mdk
    ${SDK_ROOT}/components/libraries/bootloader/ble_dfu
    ${SDK_ROOT}/components/softdevice/common
    ${SDK_ROOT}/external/nano-pb
    ${SDK_ROOT}/components/libraries/queue
    ${SDK_ROOT}/components/libraries/mutex
    ${SDK_ROOT}/components/libraries/ringbuf
)

# Create the executable target
add_executable(${PROJECT_NAME} ${SOURCES})

# Set target properties
set_target_properties(${PROJECT_NAME} PROPERTIES
    OUTPUT_NAME "nrf52840_xxaa_s140"
    SUFFIX ".elf"
)

# Include directories
target_include_directories(${PROJECT_NAME} PRIVATE ${INCLUDE_DIRS})

# Compiler definitions
target_compile_definitions(${PROJECT_NAME} PRIVATE
    BLE_STACK_SUPPORT_REQD
    BOARD_PCA10056
    CONFIG_GPIO_AS_PINRESET
    FLOAT_ABI_HARD
    NRF52840_XXAA
    NRF_DFU_SETTINGS_VERSION=2
    NRF_DFU_SVCI_ENABLED
    NRF_SD_BLE_API_VERSION=7
    S140
    SOFTDEVICE_PRESENT
    SVC_INTERFACE_CALL_AS_NORMAL_FUNCTION
    __HEAP_SIZE=0
)

# Compiler options
target_compile_options(${PROJECT_NAME} PRIVATE
    -mcpu=cortex-m4
    -mthumb
    -mabi=aapcs
    -Wall
    -Werror
    -mfloat-abi=hard
    -mfpu=fpv4-sp-d16
    -ffunction-sections
    -fdata-sections
    -fno-strict-aliasing
    -fno-builtin
    -fshort-enums
    -Os
    -g3
    -flto
)

# Linker options
target_link_options(${PROJECT_NAME} PRIVATE
    -mcpu=cortex-m4
    -mthumb
    -mabi=aapcs
    -mfloat-abi=hard
    -mfpu=fpv4-sp-d16
    -Wl,--gc-sections
    -L${SDK_ROOT}/modules/nrfx/mdk
    -T${CMAKE_CURRENT_SOURCE_DIR}/pca10056_s140_ble/armgcc/secure_bootloader_gcc_nrf52.ld
)

# Link libraries
target_link_libraries(${PROJECT_NAME} PRIVATE
    ${SDK_ROOT}/external/nrf_oberon/lib/cortex-m4/hard-float/liboberon_3.0.8.a
    ${SDK_ROOT}/external/nrf_cc310_bl/lib/cortex-m4/hard-float/libnrf_cc310_bl_0.9.13.a
    c
    nosys
    m
)

# Custom commands for post-build
add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND ${CMAKE_OBJCOPY} -O ihex $<TARGET_FILE:${PROJECT_NAME}> ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}.hex
    COMMAND ${CMAKE_OBJCOPY} -O binary $<TARGET_FILE:${PROJECT_NAME}> ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}.bin
    COMMAND ${CMAKE_SIZE} $<TARGET_FILE:${PROJECT_NAME}>
    COMMENT "Creating HEX and BIN files, showing firmware size"
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