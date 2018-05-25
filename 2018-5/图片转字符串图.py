from PIL import Image, ImageDraw, ImageFont
import os
import time


class IMG_STR:
    def __init__(self, img_name):
        self.img_name = img_name

    def save(self, img, file_name):
        if os.path.isfile(file_name):
            file_name=file_name.split('.')
            self.save(img, file_name[0] + 'o.' + file_name[1])
        else:
            img.save(file_name, 'JPEG')

    def main(self):
        f_size = 16
        f_num_x = 100
        font_map = [' ', '.', 'i', 'I', 'J', 'C', 'D', 'O', 'S', 'Q', 'G', 'F', 'E', '#', '&', '@']
        im = Image.open(self.img_name).convert('L')
        im = im.resize((f_num_x, int(f_num_x * im.size[1] / im.size[0])))
        level = im.getextrema()[-1] / (len(font_map) - 1)
        im = im.point(lambda i: int(i / level))
        imn = Image.new('L', (im.size[0] * f_size, im.size[1] * f_size))

        f = ImageFont.truetype('arial.ttf', f_size)
        d = ImageDraw.Draw(imn)

        for y in range(0, im.size[1]):
            for x in range(0, im.size[0]):
                pp = im.getpixel((x, y))
                d.text((x * f_size, y * f_size), font_map[len(font_map) - pp - 1], fill=255, font=f)

        self.save(imn, self.img_name)

if __name__ == '__main__':
    img = IMG_STR('a.jpg')
    img.main()
