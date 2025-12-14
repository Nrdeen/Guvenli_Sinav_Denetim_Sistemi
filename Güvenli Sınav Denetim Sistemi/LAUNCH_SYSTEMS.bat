@echo off
chcp 65001 >nul
title Sınav Sistemleri - Unified Launcher

cls
echo.
echo ═══════════════════════════════════════════════════════════════
echo   🎓 SINAV GÜVENLİK SİSTEMLERİ - Unified Launcher
echo ═══════════════════════════════════════════════════════════════
echo.
echo   Starting unified launcher...
echo.
echo   Bu launcher iki sistemi yönetir:
echo     • Online Sınav (Port 5000)
echo     • Sınıf İçi Sınav (Port 3000)
echo.
echo   Launcher URL: http://localhost:8080
echo.
echo ═══════════════════════════════════════════════════════════════
echo.

python unified_launcher.py

pause
