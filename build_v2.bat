@echo off
setlocal enabledelayedexpansion

echo [Stage 1] Concatenating source files into build\freakc_v2.fk...
if not exist build mkdir build
if exist build\freakc_v2.fk del build\freakc_v2.fk

type src\compiler\ast.fk >> build\freakc_v2.fk
type src\compiler\lexer.fk >> build\freakc_v2.fk
type src\compiler\parser.fk >> build\freakc_v2.fk
type src\compiler\checker.fk >> build\freakc_v2.fk
type src\compiler\emitter.fk >> build\freakc_v2.fk
type src\compiler\backend\llvm.fk >> build\freakc_v2.fk
type src\compiler\main.fk >> build\freakc_v2.fk

echo [Stage 2] Compiling build\freakc_v2.fk with freakc_self.exe...
freakc_self.exe build\freakc_v2.fk

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] freakc_self.exe failed to compile freakc_v2.fk
    exit /b %ERRORLEVEL%
)

echo [Stage 3] Building freakc_v2.exe natively with Clang...
clang -o build\freakc_v2.exe build\freakc_v2.fk.c freakc\runtime\freak_runtime.c -Ifreakc\runtime -g -std=c11 -Wall

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Clang failed to compile freakc_v2.c
    exit /b %ERRORLEVEL%
)

echo .
echo Bootstrap Level 3 complete! The v2 compiler is ready at build\freakc_v2.exe
echo .
