# Template for writing objc/xcode-powered code in VSCode with clangd

## What is this?

If you are developing for macOS/\*OS you probably want Xcode's build system.

You may not want to use Xcode itself though.

Editing pbxproj files by hand is hard, and you might want to use CMakeLists.txt instead.

This template attempts to solve both of these problems.

By using the provided CMakeLists.txt file you can create .app bundles, and generate a compilation database using `./generate_xcode_compilation_database.py` for use with clangd.

Using clangd, you can effectively move basic development to your favorite editor, like Vim or VSCode.

## How can I use this?

### Use cmake instead of Xcode

cmake can use the Xcode build system if you specify `-GXcode`. using this, it is possible to create Xcode projects.

You can specify any Xcode settings you want using the construct `set(CMAKE_XCODE_ATTRIBUTE_<your_xcode_setting> <value>)`.
Just append a line like this to the CMakeLists.txt.

For a list of xcode settings, see <https://developer.apple.com/documentation/xcode/build-settings-reference>.

If you don't want to use the Xcode generator e.g. Make, that's also entirely possible, though you might need to add a lot of extra options to your configs to get it to work.

### Generate compile_commands.json

You can normally specify `-DCMAKE_EXPORT_COMPILE_COMMANDS=ON` in the command line when you want to generate a compilation database.
The Xcode generator doesn't support this.

Clang on the other hand supports outputting the cli invocation along with other compilation database metadata as a json to a user-specified directory during any compilation steps using the `-gen-cdb-fragment-path DIR` option. This project exploits this support by adding this option to all invocations if the Xcode generator is used and `CMAKE_EXPORT_COMPILE_COMMANDS` is set to `ON` by setting `CMAKE_XCODE_ATTRIBUTE_OTHER_CFLAGS` to include this option.

Then you can use `./generate_xcode_compilation_database.py` to put all these invocation log files together.

One problem with this approach is that the fragments are created during compile time, not generation time.

Due to this, you will be able to run `./generate_xcode_compilation_database.py` only after the first compile in Xcode projects.

As a corollary, since Xcode only compiles files that changed, these fragments will not be created for builds that set the `-gen-cdb-fragment-path DIR` option affter the first build unless files are changed. `./generate_xcode_compilation_database.py` supports this workflow where you can create the cdb after the first build (so after the build system is generated) so if you want it to work, you should first clean the build directory using `xcodebuild clean`.

After this clangd will be at your service and it should be close to Xcode if you use Apple clangd. Even apple's public fork of clangd has some bugs (the one I encountered was `@import module` constructs were not properly supported).

Hopefully all the bugfixes get pushed upstream some day and everyone can use clangd on objc files properly. (or maybe public clangd already has these bugfixes and they must be enabled via configs?)

## Enough jibberjabber, show me how you use this

```shell
cmake -B build -G "Unix Makefiles" -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build build # not needed for Make if you just want to create compilation database.
```

or

```shell
cmake -B build -G "Xcode" -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build build

./generate_xcode_compilation_database.py build
```

or

```shell
cmake -B build -G "Xcode" -DCMAKE_EXPORT_COMPILE_COMMANDS=OFF # default

./generate_xcode_compilation_database.py build --build-with "xcodebuild --flags --what-have-you"
```

or

```shell
cmake -B build -G "Xcode" -DCMAKE_EXPORT_COMPILE_COMMANDS=OFF # default
cmake build # after first build the cdb fragments can become out of sync because
            # they will only be regenerated for changed files/changed compile flags.
# ...

cmake --build buildX --target clean # clean build so fragments are in sync again.
./generate_xcode_compilation_database.py build --build-with "xcodebuild --flags --what-have-you"
```
