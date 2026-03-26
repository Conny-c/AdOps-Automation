@echo off
REM ==================================================
REM 一键清理 Python bytecode 并提交到 GitHub
REM ==================================================

REM 进入项目目录
cd /d F:\AdOps-Automation

echo ===== Updating .gitignore =====
REM 添加忽略规则，如果没有已经写入的，就写入
findstr /C:"__pycache__/" .gitignore >nul
if errorlevel 1 (
    echo # Python bytecode >> .gitignore
    echo __pycache__/ >> .gitignore
    echo *.pyc >> .gitignore
    echo ".gitignore updated with __pycache__ and *.pyc"
) else (
    echo ".gitignore already has __pycache__ rules"
)
echo.

echo ===== Removing cached pyc files =====
git rm -r --cached ads_ops/__pycache__ 2>nul
git rm -r --cached content_engines/aigc_engine/__pycache__ 2>nul
git rm -r --cached content_engines/content_remix/__pycache__ 2>nul
echo "Cached pyc files removed from Git"
echo.

echo ===== Adding all changes =====
git add .
echo.

REM 自动生成提交信息
set COMMIT_MSG=Clean pyc files + update .gitignore

git commit -m "%COMMIT_MSG%" 2>nul
if %errorlevel% == 0 (
    echo "Committed successfully: %COMMIT_MSG%"
) else (
    echo "Nothing to commit"
)
echo.

echo ===== Pushing to origin main =====
git push origin main
echo.
echo ===== Done! =====
pause