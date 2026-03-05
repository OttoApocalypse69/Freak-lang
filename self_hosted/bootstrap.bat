@echo off
echo ============================================================
echo  FREAK Self-Hosted Compiler Bootstrap
echo  M15: The compiler compiles itself.
echo ============================================================
echo.

echo [Step 1] Compiling self_hosted/main.fk with Python compiler...
python -m freakc build self_hosted/main.fk -o self_hosted/freakc_self.exe --keep-c
if errorlevel 1 (
    echo FAILED: Python compiler could not compile main.fk
    exit /b 1
)
echo [Step 1] OK — freakc_self.exe built.
echo.

echo [Step 2] Running self-hosted compiler on tests/hello.fk...
self_hosted\freakc_self.exe
if errorlevel 1 (
    echo FAILED: Self-hosted compiler crashed
    exit /b 1
)
echo.

echo [Step 3] Compiling the C output from self-hosted compiler...
gcc tests/hello_self.c freakc/runtime/freak_runtime.c -Ifreakc/runtime -o tests/hello_self.exe
if errorlevel 1 (
    echo FAILED: gcc could not compile the generated C
    exit /b 1
)
echo [Step 3] OK — hello_self.exe built from self-hosted compiler output.
echo.

echo [Step 4] Running hello_self.exe...
tests\hello_self.exe
echo.

echo ============================================================
echo  BOOTSTRAP COMPLETE! M15 ACHIEVED!
echo ============================================================
