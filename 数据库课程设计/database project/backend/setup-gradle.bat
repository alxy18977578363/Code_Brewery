@echo off
echo 正在生成Gradle包装器...
echo.

REM 如果已安装gradle，使用本地gradle生成wrapper
where gradle >nul 2>&1
if %errorlevel% == 0 (
    echo 使用本地Gradle生成包装器...
    gradle wrapper --gradle-version 8.5
) else (
    echo 未检测到本地Gradle安装
    echo 请先安装Gradle或手动下载gradle-wrapper.jar
    echo.
    echo 安装Gradle方法：
    echo 1. 访问 https://gradle.org/install/
    echo 2. 下载并解压Gradle
    echo 3. 配置PATH环境变量
    echo.
    echo 或者手动配置Gradle Wrapper：
    echo 1. 创建 gradle/wrapper 目录
    echo 2. 下载 gradle-wrapper.jar 到该目录
    echo 3. 创建 gradle-wrapper.properties 配置文件
)

pause
