@echo off
chcp 65001 >nul

REM 提示用户输入 saleropenid, start_date 和 end_date
set /p SALEROPENID=请输入置业顾问ID（saleropenid）:
set /p START_DATE=请输入开始日期（YYYY-MM-DD）:
set /p END_DATE=请输入结束日期（YYYY-MM-DD）:

REM 发送带有输入参数的 POST 请求
curl -X POST http://127.0.0.1:45104/analysis ^
     -H "Content-Type: application/json" ^
     -d "{\"saleropenid\": \"%SALEROPENID%\", \"start_date\": \"%START_DATE%\", \"end_date\": \"%END_DATE%\"}"
