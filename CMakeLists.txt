cmake_minimum_required(VERSION 3.8)
project(HelloWorld)
set(NAME HelloWorld)

file(GLOB SOURCE_FILES "./src/*.m" "./src/*.c")
file(GLOB HEADER_FILES "./src/*.h")

add_executable(
    ${NAME}
    MACOSX_BUNDLE
    ${HEADER_FILES}
    ${SOURCE_FILES}
    ${XIB_FILE}
)

# add_definitions("-x objective-c")
# set(CMAKE_SHARED_LINKER_FLAGS "-rpath @executable_path/Frameworks -rpath @loader_path/Frameworks")
# For some reason CMAKE_BINARY_DIR is not set here but is still accessible?
# if(NOT DEFINED ENV{CMAKE_BINARY_DIR})
#     message( FATAL_ERROR "CMAKE_BINARY_DIR is not set. This should never happen, but you never know." )
# endif(NOT DEFINED ENV{CMAKE_BINARY_DIR})

# add_custom_command(
#     TARGET ${NAME}
#     PRE_BUILD
#     COMMAND rm -rf "${CMAKE_BINARY_DIR}/CompilationDatabase"
#     COMMENT "Removing compilation database before build"
# )

    

set(CMAKE_C_FLAGS "-fmodules") # For auto linking. Thanks <https://milen.me/writings/auto-linking-on-ios-and-macos/>!
# set(CMAKE_CXX_SCAN_FOR_MODULES YES)
# The below works for -GXcode. For other generators you need the full path.
# e.g. /Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS17.0.sdk
# You can find the path by running xcrun --sdk iphoneos --show-sdk-path
# set(CMAKE_OSX_SYSROOT iphoneos)
# set(CMAKE_OSX_SYSROOT /Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS17.0.sdk)

# set(XCODE_ATTRIBUTE_CODE_SIGN_IDENTITY "")
# set(XCODE_ATTRIBUTE_CODE_SIGNING_ALLOWED "")
# set_target_properties(${NAME} PROPERTIES
#     XCODE_ATTRIBUTE_CODE_SIGN_IDENTITY "" # Skip code signing, well not sure which of these precisely disables it.
# )

# target_link_libraries(${NAME} "-framework UIKit -framework IOKit")


# sadly only runs in compile time, not build system generation time.
# Idea from https://gist.github.com/T1T4N/f4d63a44476eb5c7046cc561cb8c7f77
if(CMAKE_GENERATOR STREQUAL "Xcode")
	if(CMAKE_EXPORT_COMPILE_COMMANDS)
		set(CMAKE_XCODE_ATTRIBUTE_OTHER_CFLAGS  "$(inherited) -gen-cdb-fragment-path ${CMAKE_BINARY_DIR}/CompilationDatabase")
		# The following three options come from <https://bugs.webkit.org/attachment.cgi?id=452685&action=prettypatch>.
        
        # Not enabled as this will affect all builds even when we don't want to change the cdb.
        # set(CMAKE_XCODE_ATTRIBUTE_GCC_PRECOMPILE_PREFIX_HEADER  "NO")
		# set(CMAKE_XCODE_ATTRIBUTE_CLANG_ENABLE_MODULE_DEBUGGING  "NO")
        
        # Enabled as we don't need this if we aren't using Xcode.
		set(CMAKE_XCODE_ATTRIBUTE_COMPILER_INDEX_STORE_ENABLE  "NO")
	endif()
endif()



