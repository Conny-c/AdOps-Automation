@echo off
REM 一键提交 & 推送脚本 - push_all.bat

REM 进入项目目录
cd /d F:\AdOps-Automation

REM 显示 Git 状态
echo ===== Git Status =====
git status
echo.

REM 添加所有修改文件
echo ===== Adding all files =====
git add .
echo.

REM 提交
set /p COMMIT_MSG=请输入本次提交说明：
git commit -m "%COMMIT_MSG%"
echo.

REM 推送到远程 main 分支
echo ===== Pushing to origin main =====
git push origin main
echo.
echo ===== Push Complete =====
pause