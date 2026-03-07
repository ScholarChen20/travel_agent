@echo off
REM Travel Agent - 快速启动脚本（Windows版本）

echo ========================================
echo   Travel Agent - 快速启动
echo ========================================
echo.

REM 检查Docker是否安装
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] Docker未安装
    echo 请先安装Docker Desktop: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM 检查Docker Compose是否安装
where docker-compose >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] Docker Compose未安装
    echo 请先安装Docker Compose: https://docs.docker.com/compose/install/
    pause
    exit /b 1
)

echo [成功] Docker环境检查通过
echo.

REM 检查.env文件
if not exist .env (
    echo [警告] .env文件不存在
    echo 正在从.env.example创建.env文件...
    if exist .env.example (
        copy .env.example .env
        echo [成功] .env文件已创建
    ) else (
        echo [错误] .env.example文件不存在
        pause
        exit /b 1
    )
)

REM 检查ngrok配置文件
if not exist backend\scripts\ngrok.yml (
    echo [错误] ngrok配置文件不存在
    echo 请确保 backend\scripts\ngrok.yml 文件存在
    pause
    exit /b 1
)

REM 提示输入ngrok authtoken
echo.
echo ========================================
echo   Ngrok 配置
echo ========================================
echo.
echo 请输入你的Ngrok Authtoken
echo 获取地址: https://dashboard.ngrok.com/get-started/your-authtoken
echo.
set /p NGROK_TOKEN="Ngrok Authtoken: "

if "%NGROK_TOKEN%"=="" (
    echo [错误] Authtoken不能为空
    pause
    exit /b 1
)

REM 更新.env文件
findstr /C:"NGROK_AUTHTOKEN=" .env >nul
if %errorlevel% equ 0 (
    powershell -Command "(Get-Content .env) -replace '^NGROK_AUTHTOKEN=.*', 'NGROK_AUTHTOKEN=%NGROK_TOKEN%' | Set-Content .env"
) else (
    echo NGROK_AUTHTOKEN=%NGROK_TOKEN% >> .env
)
echo [成功] Ngrok Authtoken已配置
echo.

REM 停止现有服务
echo 停止现有服务...
docker-compose down 2>nul

REM 构建并启动服务
echo.
echo ========================================
echo   启动服务
echo ========================================
echo.
echo 正在构建并启动所有服务（包括ngrok）...
docker-compose up -d --build

echo.
echo ========================================
echo   服务启动完成
echo ========================================
echo.

REM 等待服务启动
echo 等待服务启动...
timeout /t 15 /nobreak >nul

REM 检查服务状态
echo 检查服务状态...
docker-compose ps

echo.
echo ========================================
echo   获取Ngrok公网地址
echo ========================================
echo.

echo 正在获取ngrok公网地址...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo   访问信息
echo ========================================
echo.
echo 请手动查看ngrok日志获取公网地址:
echo   docker-compose logs -f ngrok
echo.
echo 或访问ngrok Web UI:
echo   http://localhost:4040
echo.
echo ========================================
echo   管理命令
echo ========================================
echo.
echo 查看所有服务状态:
echo   docker-compose ps
echo.
echo 查看ngrok日志:
echo   docker-compose logs -f ngrok
echo.
echo 查看所有服务日志:
echo   docker-compose logs -f
echo.
echo 停止所有服务:
echo   docker-compose down
echo.
echo 重启所有服务:
echo   docker-compose restart
echo.
echo ========================================
echo   重要提示
echo ========================================
echo.
echo 1. 免费版ngrok的域名可能会变化，这是正常现象
echo 2. 如需固定域名，请升级ngrok付费计划
echo 3. 生产环境建议使用固定域名或自建frp
echo 4. 可以通过以下命令查看ngrok日志:
echo    docker-compose logs -f ngrok
echo.
echo ========================================
echo   部署完成！
echo ========================================
echo.
pause
