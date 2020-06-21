import PIL
import PIL.Image
import PIL.ImageDraw
import pathlib

'''
Take a jpg image, make everything outside the marble transparent and save it as a png.
'''
DIRECTORY_OF_THIS_FILE = pathlib.Path(__file__).parent.absolute()
for filename in DIRECTORY_OF_THIS_FILE.glob('*.jpg'):
  print(filename)
  
  # img = PIL.Image.new('RGBA', size = (100, 100), color = (128, 128, 128, 255))
  img = PIL.Image.open(filename)
  mask= PIL.Image.new("L", img.size, 0)
  draw = PIL.ImageDraw.Draw(mask)
  draw.ellipse((0, 0, img.size[0], img.size[1]), fill=255)
  del draw
  img.putalpha(mask)
  img.save(filename.with_suffix('.png'), 'PNG')
