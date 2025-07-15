# Toolchain file for ARM Cortex-M4 using arm-none-eabi-gcc

set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR arm)

# Toolchain paths (adjust as needed for your system)
find_program(CMAKE_C_COMPILER arm-none-eabi-gcc)
find_program(CMAKE_CXX_COMPILER arm-none-eabi-g++)
find_program(CMAKE_ASM_COMPILER arm-none-eabi-gcc)
find_program(CMAKE_AR arm-none-eabi-ar)
find_program(CMAKE_OBJCOPY arm-none-eabi-objcopy)
find_program(CMAKE_OBJDUMP arm-none-eabi-objdump)
find_program(CMAKE_SIZE arm-none-eabi-size)

# Check if toolchain is available
if(NOT CMAKE_C_COMPILER)
    message(FATAL_ERROR "arm-none-eabi-gcc not found. Please install ARM GCC toolchain.")
endif()

# Configure CMake to not check for working C/CXX compiler (cross-compilation)
set(CMAKE_C_COMPILER_WORKS 1)
set(CMAKE_CXX_COMPILER_WORKS 1)

# Don't search for programs in the build host directories
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)

# Search for libraries and headers in the target environment
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)

# Set common flags for ARM Cortex-M4
set(COMMON_FLAGS "-mcpu=cortex-m4 -mthumb -mabi=aapcs -mfloat-abi=hard -mfpu=fpv4-sp-d16")

# C flags
set(CMAKE_C_FLAGS_INIT "${COMMON_FLAGS} -Wall -Werror -ffunction-sections -fdata-sections -fno-strict-aliasing -fno-builtin -fshort-enums")
set(CMAKE_C_FLAGS_DEBUG_INIT "-O0 -g3")
set(CMAKE_C_FLAGS_RELEASE_INIT "-Os -DNDEBUG")
set(CMAKE_C_FLAGS_RELWITHDEBINFO_INIT "-Os -g3 -DNDEBUG")
set(CMAKE_C_FLAGS_MINSIZEREL_INIT "-Os -DNDEBUG")

# CXX flags
set(CMAKE_CXX_FLAGS_INIT "${COMMON_FLAGS} -Wall -Werror -ffunction-sections -fdata-sections -fno-strict-aliasing -fno-builtin")
set(CMAKE_CXX_FLAGS_DEBUG_INIT "-O0 -g3")
set(CMAKE_CXX_FLAGS_RELEASE_INIT "-Os -DNDEBUG")
set(CMAKE_CXX_FLAGS_RELWITHDEBINFO_INIT "-Os -g3 -DNDEBUG")
set(CMAKE_CXX_FLAGS_MINSIZEREL_INIT "-Os -DNDEBUG")

# ASM flags
set(CMAKE_ASM_FLAGS_INIT "${COMMON_FLAGS}")

# Linker flags
set(CMAKE_EXE_LINKER_FLAGS_INIT "${COMMON_FLAGS} -Wl,--gc-sections --specs=nano.specs")

# Set default build type if not specified
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Choose the type of build" FORCE)
endif()

# Set file extensions
set(CMAKE_EXECUTABLE_SUFFIX_C ".elf")
set(CMAKE_EXECUTABLE_SUFFIX_CXX ".elf")

# Tell CMake to use response files for linking (helps with long command lines)
set(CMAKE_C_USE_RESPONSE_FILE_FOR_LIBRARIES ON)
set(CMAKE_CXX_USE_RESPONSE_FILE_FOR_LIBRARIES ON)
set(CMAKE_C_USE_RESPONSE_FILE_FOR_OBJECTS ON)
set(CMAKE_CXX_USE_RESPONSE_FILE_FOR_OBJECTS ON)
set(CMAKE_C_USE_RESPONSE_FILE_FOR_INCLUDES ON)
set(CMAKE_CXX_USE_RESPONSE_FILE_FOR_INCLUDES ON) 