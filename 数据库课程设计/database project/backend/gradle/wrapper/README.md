# Gradle Wrapper文件说明

由于gradle-wrapper.jar是二进制文件，无法直接创建。

## 获取gradle-wrapper.jar的方法：

### 方法1：使用已安装的Gradle生成（推荐）
如果你已经安装了Gradle：
```bash
cd backend
gradle wrapper --gradle-version 8.5
```

### 方法2：从现有项目复制
从其他Gradle项目复制 `gradle/wrapper/gradle-wrapper.jar` 文件

### 方法3：手动下载
1. 访问：https://github.com/gradle/gradle/tree/master/gradle/wrapper
2. 下载 gradle-wrapper.jar
3. 放置到 `backend/gradle/wrapper/` 目录

### 方法4：使用setup脚本
运行 `setup-gradle.bat` 脚本自动生成

## 验证安装

成功后，可以使用以下命令：
```bash
gradlew.bat build
gradlew.bat run
```
