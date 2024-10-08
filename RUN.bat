@echo off

cd %~dp0

REM Check if the conda environment "hydra" exists
conda env list | findstr "hydra" >nul
if %errorlevel% neq 0 (
    REM Create the conda environment "hydra"
    conda create -n hydra python=3.11 -y
)

REM Activate the conda environment "hydra"
call conda activate hydra

REM Install the requirements from requirements.txt
if exist requirements.txt (
    pip install -r requirements.txt
) else (
    echo requirements.txt not found.
)

