import { Client } from "https://cdn.jsdelivr.net/npm/@gradio/client/dist/index.min.js";
import { access_token, space_name, trigger_word, img_size, num_steps} from './config.js';
let image_counter = 0;

//Initialize the client and the UI
async function init() {
    const client = await Client.connect(`kratadata/${space_name}`, { hf_token: access_token });
    const genInfo = document.getElementById('info')
    let result;
    document.getElementById('generate').addEventListener('click', async () => {
        const prompt = document.getElementById('prompt').value;
        genInfo.innerText = "Generating image, please wait...";
        
        try {
            result = await client.predict("/infer", { 		
                prompt: prompt + " in the style of " + trigger_word, 		
                seed: 0, 		
                randomize_seed: true, 		
                width: img_size, 		
                height: img_size, 		
                num_inference_steps: num_steps, 
            });
            
        } catch (error) {
            console.error("Error occurred during prediction:", error);
            genInfo.innerText = `Error occurred: ${error.message}`;
            return; 
        }

        if (result.error) {
            console.error("Error in result:", result.error);
            genInfo.innerText = `Error in result: ${result.error}`;
            return; 
        }
        console.log(result); 

        const imageUrl = result.data[0].url; 
        if (typeof imageUrl === 'string') {
            const img = document.createElement('img');
            img.src = imageUrl; 
            document.getElementById('result').innerHTML = ''; 
            document.getElementById('result').appendChild(img);
            genInfo.innerText = "Image generated successfully!";
            addToGalery(imageUrl);
        } else {
            console.error("Expected a string URL but got:", imageUrl);
            genInfo.innerText = "Error: Invalid image URL."; 
        }

        
    });
}


//Display all generated images
function addToGalery(imageUrl) {
    const galleryItem = document.createElement('div');
    galleryItem.className = 'gallery-item';
    const galleryImg = document.createElement('img');
    galleryImg.src = imageUrl;
    galleryItem.appendChild(galleryImg);
    document.getElementById('gallery').appendChild(galleryItem);
}

init(); 