@echo off
chcp 65001 >nul
cd /d "%~dp0"
title AI 情报站 · 上线前自检

set PY=C:\Users\22198\.workbuddy\binaries\python\versions\3.13.12\python.exe
set NODE=C:\Users\22198\.workbuddy\binaries\node\versions\22.22.2-3\node.exe

echo.
echo ============================================================
echo   AI 情报站 · 上线前自检
echo ------------------------------------------------------------
echo   改完任何东西，双击这个 bat 跑一遍。
echo   必须全部通过，才允许说"已上线"。
echo ============================================================
echo.

echo [1/3] 重新构建 ...
"%PY%" _build.py
if errorlevel 1 goto FAILED_BUILD

echo.
echo [2/3] 内容与链接自检 ...
"%NODE%" _selfcheck.js
if errorlevel 1 goto FAILED_CHECK

echo.
echo [3/3] 上线前总检 ...
"%PY%" _preship.py --skip-remote
if errorlevel 1 goto FAILED_SHIP

echo.
echo ------------------------------------------------------------
echo   自检通过。可以推送了。
echo   推送命令：  git push
echo   想确认线上页面真是新的，再跑一次（会真访问线上比对）：
echo       python _preship.py
echo ------------------------------------------------------------
pause
exit /b 0

:FAILED_BUILD
echo.
echo !!!!!! 构建失败 !!!!!
echo 改的源码有问题，先修 index.src.html 或数据文件，再双击本 bat。
pause
exit /b 1

:FAILED_CHECK
echo.
echo !!!!!! 自检没过，不许上线 !!!!!
echo 看上面红色 FAIL 那行，按它下面的中文提示修。
pause
exit /b 1

:FAILED_SHIP
echo.
echo !!!!!! 上线前总检没过，不许宣布"已上线" !!!!!
echo 常见三种：
echo   1. 改了源文件但构建没成功   -- 看第 1 步报错
echo   2. git 还有提交没推上去     -- 手动执行  git push  再跑一次
echo   3. 线上内容和本地不一致     -- 推完等 1 分钟再跑一次
pause
exit /b 1
