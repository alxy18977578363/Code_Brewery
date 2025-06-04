from diffusers import StableDiffusionPipeline
import torch

model_id = "stable-diffusion-v1-5/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
pipe = pipe.to("cuda")

prompt = "请你以水墨画的形式来画下面这个一个诗句‘日往菲薇，月来扶疏。’"
image = pipe(prompt).images[0]  

image.save("astronaut_rides_horse.png")