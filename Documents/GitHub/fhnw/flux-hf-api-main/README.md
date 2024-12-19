# Image generator using HuggingFace API and Flux model. Hosted on RunPod.

## Configuration Parameters

1. Open `config.js` and change following parameters:
    - `access_token`: The HuggingFace API token to access private models.
    - `trigger_word`: The keyword to use for the image generation.
    - `space_name`: The name of the LoRA model to use for the image generation.
    - `img_size`: The size of the image to generate. 1024 is recommended for better quality.
    - `num_steps`: The number of steps to use for the image generation. Keep at 2 for faster generation, at 4 for better quality.
  
## Usage

1. Open `index.html` in your browser using Live Server extension.
2. Enter a prompt and click **Generate** button.
3. Download the image with rigth mouse click.
4. Previous generated images will be shown under the **Generate** button (until you close/reload page).
