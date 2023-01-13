@echo off

call %~dp0telegram_bot\venv\Scripts\activate

cd %~dp0telegram_bot

set TOKEN=5714808685:AAFT9eV8HRMByKYUNOPkn0GTOUSJIHpHPb4

python bot.py

pause