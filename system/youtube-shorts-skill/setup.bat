@echo off
echo === YouTube Shorts Pipeline Setup ===
echo.
echo [1/4] Installing yt-dlp...
pip install yt-dlp

echo [2/4] Installing Kinocut...
pip install kinocut

echo [3/4] Creating folders...
mkdir "D:\youtube system\output\4k video" 2>nul
mkdir "D:\youtube system\output\4k video\en" 2>nul
mkdir "D:\youtube system\output\4k video\hi" 2>nul
mkdir "D:\youtube system\output\transcript" 2>nul
mkdir "D:\youtube system\output\transcript\en" 2>nul
mkdir "D:\youtube system\output\transcript\hi" 2>nul
mkdir "D:\youtube system\output\face_track" 2>nul
mkdir "D:\youtube system\output\face_track\en" 2>nul
mkdir "D:\youtube system\output\face_track\hi" 2>nul
mkdir "D:\youtube system\output\final clips" 2>nul
mkdir "D:\youtube system\output" 2>nul

echo [4/4] Done.
echo.
echo Now configure your MCP servers in your agent:
echo.
echo   kinocut:     python -m kinocut
echo   youtube:     python "D:\youtube system\system\youtube-mcp-server\server.py"
echo   youtube-seo: python "D:\youtube system\system\youtube-mcp-seo\server.py"
echo.
echo Then tell your agent: "youtube system"
pause
