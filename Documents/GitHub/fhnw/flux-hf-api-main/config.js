export const access_token = ""  // your huggingface access token

// trigger word "BRUNN"and space_name "moritz-brunnmatt" --> Moritz
// trigger word "STUUEHL" and space_name "fhnw-flux-lora" --> Mia
// trigger word "BOODLE" and space_name "luisa-doodle" --> Luisa
// trigger word "YOMICS" and space_name "fhnw-flux-lora" --> Yoana
// trigger word "ATILE" and space_name "aiste-tiles" --> Aiste
export const trigger_word = "ATILE" 
export const space_name = "aiste-tiles" 
export const img_size = 1024 // keep at 1024 for better quality, 512 to speed up generation
export const num_steps = 2 // keep at 2 for faster generation, change to 4 for better quality
