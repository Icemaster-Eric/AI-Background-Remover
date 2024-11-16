from nicegui import run, ui
import model
from PIL import Image
import torch
import os
from io import BytesIO
import requests
import urllib.parse


device = torch.device("cuda")

model = model.BEN_Base().to(device).eval()
model.loadcheckpoints("./BEN_Base.pth")


@ui.page("/")
def main():
    def remove_background(image):
        return model.inference(image)[1]

    async def upload_image(e):
        ui.notify(f"Processing {e.name}")

        image = Image.open(e.content)

        result = await run.io_bound(remove_background, image)

        image_buffer = BytesIO()
        result.save(image_buffer, format="PNG")
        image_buffer.seek(0)

        files = {"file": (urllib.parse.quote(e.name), image_buffer, "image/png")}

        response = await run.io_bound(requests.post, "https://cdn.pyro.hackclub.app/upload", files=files)
        url = response.json().get("url")

        if url:
            ui.image(f"https://cdn.pyro.hackclub.app{url}")
        else:
            ui.notify(f"Failed to process {e.name}")

    # actual code here
    with ui.row().classes("mx-auto"):
        ui.label("AI Background Remover").tailwind.font_size("4xl").font_weight("bold")

    with ui.row().classes("mx-auto"):
        ui.label("Upload any image and remove its background using the current state-of-the-art model!").tailwind.font_size("lg")

    with ui.row().classes("mx-auto"):
        ui.upload(label="Upload Image", auto_upload=True, max_files=5, max_file_size=1024 * 1024 * 10, on_upload=upload_image).classes("max-w-full")


ui.run(title="AI Background Remover", dark=True, reload=False, on_air=os.environ["NICEGUI_ON_AIR"])
