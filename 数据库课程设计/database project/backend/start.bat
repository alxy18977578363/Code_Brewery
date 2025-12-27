@echo off
setlocal

echo ========================================
echo 海洋数据库管理系统 - 后端服务启动
echo ========================================
echo.

REM 检查Java
echo [1/4] 检查Java环境...
java -version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Java环境，请先安装Java 11或更高版本
    echo 下载地址: https://adoptium.net/
    pause
    exit /b 1
)
java -version
echo.

REM 检查数据库配置
echo [2/4] 检查数据库配置...
if not exist "config\database.properties" (
    echo [警告] 未找到数据库配置文件
    echo 将使用默认配置: localhost:3306/ocean_database
    echo 如需修改，请编辑 config\database.properties
)
echo.

REM 构建项目
echo [3/4] 构建项目...
call gradlew.bat build -x test
if errorlevel 1 (
    echo [错误] 构建失败
    pause
    exit /b 1
)
echo.

REM 启动服务
echo [4/4] 启动服务...
echo ========================================
call gradlew.bat run

endlocal
