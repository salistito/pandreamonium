from PIL import Image

images_folder = "../images/"

def image_grid(imgs, rows, cols):
    assert len(imgs) == rows*cols

    w, h = imgs[0].size
    grid = Image.new('RGB', size=(cols*w, rows*h))
    grid_w, grid_h = grid.size
    
    for i, img in enumerate(imgs):
        grid.paste(img, box=(i%cols*w, i//cols*h))
    return grid

def save_image(image, prompt):
    image_name = prompt.replace(" ", "_").replace(",","").replace("\n","")
    #image.save(f"{images_folder}{image_name}.png")
    image.save(f"image.png")