@echo off
chcp 65001
setlocal enabledelayedexpansion
set "OPENCC=C:\Users\yzren\AppData\Local\Programs\Python\Python310\Lib\site-packages\opencc\clib\bin\opencc.exe"
set "CONFIG=C:\Users\yzren\AppData\Local\Programs\Python\Python310\Lib\site-packages\opencc\clib\share\opencc\t2s.json"

echo 正在转换含 needT2S 的繁体文本文件为简体...

for %%f in (*needT2S*.txt) do (
    set "src=%%f"
    
    rem 替换 needT2S 为 alreadyT2S 作为输出文件名
    set "dst=%%~nxf"
    set "dst=!dst:needT2S=alreadyT2S!"

    if exist "!dst!" (
        echo [已存在] 跳过: !dst!
    ) else (
        echo [处理中] !src! → !dst!
        %OPENCC% -i "!src!" -o "!dst!" -c "!CONFIG!"
    )
)

echo 所有文件处理完成。
pause
