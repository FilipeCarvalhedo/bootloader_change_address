cmake_minimum_required(VERSION 3.15)

# Set toolchain before project() call
set(CMAKE_TOOLCHAIN_FILE "${CMAKE_CURRENT_SOURCE_DIR}/cmake/arm-none-eabi-gcc.cmake")

# Project definition
project(blinky_pca10056 
    LANGUAGES C ASM
    VERSION 1.0.0
    DESCRIPTION "Nordic nRF52840 Blinky Example"
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
    ${SDK_ROOT}/components/libraries/log/src/nrf_log_frontend.c
    ${SDK_ROOT}/components/libraries/log/src/nrf_log_str_formatter.c
    
    # Board support
    ${SDK_ROOT}/components/boards/boards.c
    
    # Utilities
    ${SDK_ROOT}/components/libraries/util/app_error.c
    ${SDK_ROOT}/components/libraries/util/app_error_handler_gcc.c
    ${SDK_ROOT}/components/libraries/util/app_error_weak.c
    ${SDK_ROOT}/components/libraries/util/app_util_platform.c
    ${SDK_ROOT}/components/libraries/util/nrf_assert.c
    ${SDK_ROOT}/components/libraries/strerror/nrf_strerror.c
    
    # Atomic operations and memory
    ${SDK_ROOT}/components/libraries/atomic/nrf_atomic.c
    ${SDK_ROOT}/components/libraries/balloc/nrf_balloc.c
    ${SDK_ROOT}/components/libraries/memobj/nrf_memobj.c
    ${SDK_ROOT}/components/libraries/ringbuf/nrf_ringbuf.c
    
    # Printf support
    ${SDK_ROOT}/external/fprintf/nrf_fprintf.c
    ${SDK_ROOT}/external/fprintf/nrf_fprintf_format.c
    
    # NRFX
    ${SDK_ROOT}/modules/nrfx/soc/nrfx_atomic.c
    
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
    ${SDK_ROOT}/integration/nrfx
    
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
    ${SDK_ROOT}/components/libraries/memobj
    
    # Boards and toolchain
    ${SDK_ROOT}/components/boards
    ${SDK_ROOT}/components/toolchain/cmsis/include
    ${SDK_ROOT}/components/drivers_nrf/nrf_soc_nosd
    
    # Printf support
    ${SDK_ROOT}/external/fprintf
    
    # SoftDevice headers (required for SDK components)
    ${SDK_ROOT}/components/softdevice/s140/headers
    ${SDK_ROOT}/components/softdevice/s140/headers/nrf52
    ${SDK_ROOT}/components/softdevice/common
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
    BOARD_PCA10056
    BSP_DEFINES_ONLY
    CONFIG_GPIO_AS_PINRESET
    FLOAT_ABI_HARD
    NRF52840_XXAA
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
    -T${CMAKE_CURRENT_SOURCE_DIR}/../armgcc/blinky_gcc_nrf52.ld
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

add_custom_target(package_dfu
    COMMAND mkdir -p ${CMAKE_CURRENT_SOURCE_DIR}/../../../tmp/dfu
    COMMAND nrfutil_6 pkg generate   --application  ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}.hex  --hw-version 52   --application-version 1   --sd-req 0x0100   --key-file ${CMAKE_CURRENT_SOURCE_DIR}/../../../examples/dfu/secure_bootloader/pca10056_s140_ble/armgcc/private_key.pem  ${CMAKE_CURRENT_SOURCE_DIR}/../../../tmp/dfu/${PROJECT_NAME}.zip
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