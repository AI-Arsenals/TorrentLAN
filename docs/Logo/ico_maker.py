from PIL import Image

png_image = Image.open('./docs/Logo/Logo.png')
png_image.save('./docs/Logo/Logo.ico')

png_image = Image.open('./docs/Logo/Icon.png')
png_image.save('./docs/Logo/Icon.ico')