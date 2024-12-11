@echo on

REM Open TouchDesigner with a specific file
start "" "C:\Program Files\Derivative\TouchDesigner\bin\TouchDesigner.exe" "C:\Users\hydra-PC\Documents\GitHub\hydra_rgbproject\touchDesigner\Hydra_v1.toe"

REM Wait for 5 seconds
timeout /t 5 /nobreak >nul

REM Open Ableton with a specific file
start "" "C:\ProgramData\Ableton\Live 10 Suite\Program\Ableton Live 10 Suite.exe" "C:\Users\hydra-PC\Desktop\Global_Layer_ABELTON\Global_layer_abelton_v2 Project\Global_layer_abelton_v2.als"

