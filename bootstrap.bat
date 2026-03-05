@echo off
echo ==========================================
echo  FREAK Self-Hosted Compiler Bootstrap
echo ==========================================
echo.

echo [Step 1] Compiling self-hosted compiler (main.fk) with Python freakc...
python -m freakc build self_hosted/main.fk -o self_hosted/freakc_self.exe --keep-c
if errorlevel 1 (
    echo FAILED: Could not compile main.fk
    exit /b 1
)
echo.

echo [Step 2] Using self-hosted compiler to compile tests/hello.fk...
self_hosted\freakc_self.exe
if errorlevel 1 (
    echo FAILED: Self-hosted compiler crashed
    exit /b 1
)
echo.

echo [Step 3] Compiling generated C with clang...
clang -o tests/hello_self.exe tests/hello_self.c freakc/runtime/freak_runtime.c -Ifreakc/runtime -w
if errorlevel 1 (
    echo FAILED: Could not compile hello_self.c
    exit /b 1
)
echo.

echo [Step 4] Running hello_self.exe...
echo ------------------------------------------
tests\hello_self.exe
echo ------------------------------------------
echo.
echo Bootstrap complete! M15 achieved.
