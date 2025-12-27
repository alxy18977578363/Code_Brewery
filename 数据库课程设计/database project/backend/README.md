# 海洋数据库管理系统 - 后端服务

基于 Java + Gradle + Netty 实现的 REST API 后端服务

## 技术栈

- **Java 11+**
- **Gradle 8.5** - 构建工具
- **Netty** - 高性能HTTP服务器
- **MySQL** - 数据库
- **HikariCP** - 数据库连接池
- **Gson** - JSON序列化

## 项目结构

```
backend/
├── build.gradle                 # Gradle构建配置
├── settings.gradle              # Gradle项目设置
├── gradle.properties            # Gradle属性配置
├── config/
│   └── database.properties      # 数据库配置文件
├── src/
│   └── main/
│       └── java/
│           └── com/ocean/database/
│               ├── Application.java              # 应用入口
│               ├── config/
│               │   └── DatabaseConfig.java      # 数据库配置
│               ├── server/
│               │   └── HttpServer.java          # HTTP服务器
│               ├── handler/
│               │   ├── CorsHandler.java         # CORS处理
│               │   └── ApiRouter.java           # API路由
│               └── service/
│                   ├── BaseService.java         # Service基类
│                   ├── StatsService.java        # 统计服务
│                   ├── UserService.java         # 用户服务
│                   ├── SampleService.java       # 样本服务
│                   ├── MeasurementService.java  # 测量服务
│                   ├── LocationService.java     # 地点服务
│                   └── NuclideService.java      # 核素服务
└── gradlew.bat                  # Gradle包装器(Windows)
```

## 快速开始

### 1. 环境要求

- Java 11 或更高版本
- MySQL 5.7 或更高版本
- Gradle 8.5+ (或使用项目自带的gradlew)

### 2. 配置数据库

编辑 `config/database.properties` 文件，配置你的数据库连接：

```properties
db.url=jdbc:mysql://localhost:3306/ocean_database?useSSL=false&serverTimezone=UTC
db.user=root
db.password=your_password
```

### 3. 初始化Gradle包装器

首次使用需要生成Gradle包装器：

```bash
cd backend
gradle wrapper
```

### 4. 构建项目

```bash
# Windows
gradlew.bat build

# Linux/Mac
./gradlew build
```

### 5. 运行服务

```bash
# Windows
gradlew.bat run

# Linux/Mac
./gradlew run
```

服务将启动在 `http://localhost:3000`

### 6. 使用Fat JAR运行

构建可执行的Fat JAR：

```bash
gradlew.bat jar
```

运行JAR包：

```bash
java -jar build/libs/ocean-database-backend-1.0.0.jar
```

## API接口文档

### 基础URL
```
http://localhost:3000/api
```

### 统计API

#### 获取系统统计数据
```
GET /api/stats
```

响应示例：
```json
{
  "users": 156,
  "samples": 2847,
  "measurements": 5632,
  "locations": 89
}
```

### 用户API

- `GET /api/users` - 获取所有用户
- `GET /api/users/:id` - 获取指定用户
- `POST /api/users` - 创建用户
- `PUT /api/users/:id` - 更新用户
- `DELETE /api/users/:id` - 删除用户

### 样本API

- `GET /api/samples` - 获取所有样本
- `GET /api/samples/:id` - 获取指定样本
- `POST /api/samples` - 创建样本
- `PUT /api/samples/:id` - 更新样本
- `DELETE /api/samples/:id` - 删除样本

### 测量记录API

- `GET /api/measurements` - 获取所有测量记录
- `GET /api/measurements/:id` - 获取指定测量记录
- `POST /api/measurements` - 创建测量记录
- `PUT /api/measurements/:id` - 更新测量记录
- `DELETE /api/measurements/:id` - 删除测量记录

### 地点API

- `GET /api/locations` - 获取所有地点
- `GET /api/locations/:id` - 获取指定地点
- `POST /api/locations` - 创建地点
- `PUT /api/locations/:id` - 更新地点
- `DELETE /api/locations/:id` - 删除地点

### 核素API

- `GET /api/nuclides` - 获取所有核素
- `GET /api/nuclides/:id` - 获取指定核素
- `POST /api/nuclides` - 创建核素
- `PUT /api/nuclides/:id` - 更新核素
- `DELETE /api/nuclides/:id` - 删除核素

## 开发指南

### 添加新的API端点

1. 在 `service/` 目录下创建新的Service类，继承 `BaseService`
2. 在 `ApiRouter.java` 中添加路由映射

### 数据库表对应

Service类与数据库表的对应关系：
- UserService → User表
- SampleService → Sample表
- MeasurementService → Measurement表
- LocationService → Location表
- NuclideService → Nuclide表

### 日志

使用SLF4J日志框架，日志会输出到控制台。

## 故障排除

### 端口被占用
如果3000端口被占用，在 `Application.java` 中修改端口号：
```java
int port = 3001; // 修改为其他端口
```

### 数据库连接失败
1. 检查MySQL服务是否启动
2. 验证 `config/database.properties` 中的配置
3. 确认数据库名称、用户名、密码正确
4. 检查MySQL是否允许远程连接

### Gradle构建失败
1. 确保Java版本为11或更高：`java -version`
2. 清理构建缓存：`gradlew.bat clean`
3. 重新构建：`gradlew.bat build --refresh-dependencies`

## 性能优化

- 使用HikariCP连接池，最大连接数为10
- 统计API使用单次查询获取所有计数（避免多次查询）
- Netty NIO模型，支持高并发

## 注意事项

1. 本项目使用Netty实现HTTP服务器，而不是传统的Flink流处理
2. 如果需要使用Flink的流处理功能，可以扩展项目添加Flink作业
3. 生产环境建议配置HTTPS和认证机制
4. 建议使用环境变量管理敏感配置信息

## License

MIT License
