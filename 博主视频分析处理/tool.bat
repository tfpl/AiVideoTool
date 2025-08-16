@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ==========================
echo 开始批量转写视频文件...
echo ==========================

rem 支持 mp4 和 mkv
for %%f in (*.mp4 *.mkv) do (
    set "video=%%~nf"
    set "ext=%%~xf"
    set "outputFile=%%~nf_needT2S.txt"

    if exist "!outputFile!" (
        echo [已存在] 跳过: %%f
    ) else (
        echo --------------------------
        echo 正在处理: %%f

        call :getStartTime
        whisper "%%f" --language zh --task transcribe --model medium --device cuda
        call :getEndTime

        rem 如果 whisper 默认输出了 %%~nf.txt，就改名为加 needT2S 后缀
        if exist "%%~nf.txt" (
            ren "%%~nf.txt" "%%~nf_needT2S.txt"
        )

        set /a duration=!endSec! - !startSec!
        echo 已完成: %%f，耗时 !duration! 秒
    )
)

echo ==========================
echo 所有文件处理完成！
pause
exit /b

:getStartTime
for /f "tokens=1-3 delims=:." %%a in ("%TIME%") do (
    set /a startSec=%%a*3600 + %%b*60 + %%c
)
goto :eof

:getEndTime
for /f "tokens=1-3 delims=:." %%a in ("%TIME%") do (
    set /a endSec=%%a*3600 + %%b*60 + %%c
)
goto :eof
