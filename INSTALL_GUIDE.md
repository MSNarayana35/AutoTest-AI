# Quick Install Guide for AutoTest AI

## Step 1: Install Node.js (CRITICAL)
Since npm and node aren't found, you need to install Node.js first!

1. Go to https://nodejs.org/
2. Download the **LTS** version (Long Term Support - recommended for stability)
3. Run the installer:
   - IMPORTANT: When the installer asks, **CHECK THE BOX** that says "Automatically install the necessary tools"
   - Also ensure "Add to PATH" is checked (it should be by default)
4. After installing, **CLOSE ALL OPEN TERMINALS** and reopen them to refresh PATH
5. Verify installation: Open a new terminal and run:
   ```bash
   node --version
   npm --version
   ```
   You should see version numbers!

## Step 2: Install Python (if not already done)
1. Go to https://www.python.org/downloads/
2. Download Python 3.10 or newer (3.13 is fine)
3. Run the installer:
   - **IMPORTANT: CHECK THE BOX "Add Python 3.x to PATH"** at the bottom!
4. Click "Install Now"
5. Verify: Open a new terminal and run:
   ```bash
   python --version
   ```

## Step 3: (Optional but Recommended) Install Ollama for AI Features
1. Download Ollama from https://ollama.com/
2. Install it
3. Open a terminal and run:
   ```bash
   ollama pull llama3
   ```

## Step 4: Run AutoTest AI
Now double-click `start.bat` again!
