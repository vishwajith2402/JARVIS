@echo off
title T.I.T.A.N. // Desktop Tactical AI Core
cd /d "D:\Practice Projects\JARVIS"

:: Performance Optimizations for RTX 3050 & AMD Ryzen 5
set OLLAMA_FLASH_ATTENTION=1
set OLLAMA_NUM_PARALLEL=1
set OLLAMA_MAX_LOADED_MODELS=1
set OLLAMA_KEEP_ALIVE=-1

echo.
echo  ========================================================
echo   T.I.T.A.N.  Desktop Tactical AI  //  v1.3.0
echo   [ACCELERATION: RTX 3050 + FlashAttention + VRAM Pinned]
echo   Auto-launching AI Agent + Desktop HUD...
echo  ========================================================
echo.
python main.py
pause
