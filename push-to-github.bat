@echo off
echo ================================================
echo   Push AutoTest AI to GitHub
echo ================================================
echo.
echo STEP 1: Create GitHub Repository First!
echo.
echo   1. Go to: https://github.com/new
echo   2. Repository name: autotest-ai
echo   3. Make it PUBLIC
echo   4. Don't initialize with anything
echo   5. Click "Create repository"
echo.
pause
echo.
echo STEP 2: Enter Your Repository URL
echo.
echo Example: https://github.com/MSNarayana35/autotest-ai.git
echo.
set /p REPO_URL="Paste your repository URL here: "
echo.
echo Updating git remote...
git remote remove origin 2>nul
git remote add origin %REPO_URL%
echo.
echo Pushing code to GitHub...
git push -u origin main
echo.
if %errorlevel% equ 0 (
    echo ================================================
    echo   SUCCESS! Code pushed to GitHub!
    echo ================================================
    echo.
    echo Your repository is now at:
    echo %REPO_URL%
    echo.
    echo Next steps:
    echo   1. Visit your repository on GitHub
    echo   2. Deploy to Railway: https://railway.app
    echo   3. Or deploy to Render: https://render.com
    echo.
) else (
    echo ================================================
    echo   ERROR: Push failed!
    echo ================================================
    echo.
    echo Common issues:
    echo   1. Repository doesn't exist yet
    echo   2. Wrong URL
    echo   3. Authentication failed
    echo.
    echo Solutions:
    echo   - Make sure you created the repository on GitHub
    echo   - Check the URL is correct
    echo   - Try again with correct credentials
    echo.
)
pause
