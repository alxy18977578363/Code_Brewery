@echo off
echo ========================================
echo 快速构建并运行
echo ========================================
echo.

gradlew.bat build -x test && gradlew.bat run

pause
