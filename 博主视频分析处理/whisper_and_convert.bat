@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
rem === 获取当前 BAT 文件所在目录 ===
set "BASEDIR=%~dp0"
echo 当前工作目录: %BASEDIR%
rem === 新增：先把文件名中的空格改成下划线 ===
for %%f in (*" "*) do (
    set "old=%%f"
    set "new=!old: =_!"
    if not "!old!"=="!new!" (
        echo 重命名: "!old!" → "!new!"
        ren "!old!" "!new!"
    )
)

set "OPENCC=C:\Users\yzren\AppData\Local\Programs\Python\Python310\Lib\site-packages\opencc\clib\bin\opencc.exe"
set "CONFIG=C:\Users\yzren\AppData\Local\Programs\Python\Python310\Lib\site-packages\opencc\clib\share\opencc\t2s.json"
:: 设置源文件夹和目标文件夹
set "source=D:\tools\AI信息收集转化整理工具链\TikTokDownloader_V5.6_Windows_X64\_internal\Download"
set "target=D:\tools\AI信息收集转化整理工具链\博主视频分析处理"

:: 检查源文件夹是否存在
if not exist "%source%" (
    echo 错误：源文件夹不存在！
    pause
    exit /b 1
)

:: 检查目标文件夹是否存在，如果不存在则创建
if not exist "%target%" (
    echo 目标文件夹不存在，正在创建...
    mkdir "%target%"
)

:: 移动文件
echo 正在移动文件...
for %%F in ("%source%\*.*") do (
    echo 移动: %%~nxF
    move "%%F" "%target%\" >nul
)

echo 文件移动完成！

rem 创建目标文件夹（如果不存在）
rem === 创建分类文件夹 ===
if not exist "%target%\中文文本" mkdir "%target%\中文文本"
if not exist "%target%\视频" mkdir "%target%\视频"
if not exist "%target%\其他文件" mkdir "%target%\其他文件"

echo ==========================
echo 开始批量转写视频文件...
echo ==========================

cd /d "%target%"

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

        if exist "%%~nf.txt" (
            ren "%%~nf.txt" "%%~nf_needT2S.txt"
        )

        set /a duration=!endSec! - !startSec!
        echo [转写完成] %%f，耗时 !duration! 秒
    )
)

echo ==========================
echo 开始转换繁体文本为简体...
echo ==========================

for %%f in (*needT2S*.txt) do (
    set "src=%%f"
    set "dst=%%~nxf"
    set "dst=!dst:needT2S=alreadyT2S!"

    if exist "!dst!" (
        echo [已存在] 跳过: !dst!
    ) else (
        echo [文本转换完成] !src! → !dst!
        "%OPENCC%" -i "!src!" -o "!dst!" -c "%CONFIG%"
    )
)

echo ==========================
echo 文件分类整理中...
echo ==========================



rem 移动视频文件
for %%f in (*.mp4 *.mkv) do (
   
    move "%%f" "视频\"
)

rem 移动其他非Excel非bat文件
for %%f in (*) do (
    set "ext=%%~xf"
    set "file=%%~nxf"

    if /I not "!ext!"==".xls" if /I not "!ext!"==".xlsx" if /I not "!ext!"==".bat" (
        if not exist "中文文本\!file!" (
            if not exist "视频\!file!" (
            
                move "%%f" "其他文件\"
            )
        )
    )
)

rem 移动 alreadyT2S 文本文件
for %%f in (*alreadyT2S*.txt) do (
    echo [移动到中文文本] %%f
    move "%%f" "中文文本\"
)


echo ==========================
echo 所有文件处理与分类完成！翻译后的文本放在中文问二八年目录下，视频放到视频目录下，其他文件放在其他文件下
echo ==========================
echo  请将文本交给ai，根据作者,日期,总结,观点,新闻内容摘要五个总结内容，总结是内容的一句话总结。并按照excel文本格式输出，作者和日期都在文件名称中,将今天的内容一起输出，最后复制到[2-生活记录-经济新闻]新闻观点内容整理.xls
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
