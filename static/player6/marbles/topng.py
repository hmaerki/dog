import PIL
import PIL.Image
import PIL.ImageDraw
import pathlib

DIRECTORY_OF_THIS_FILE = pathlib.Path(__file__).parent.absolute()
for filename in DIRECTORY_OF_THIS_FILE.glob('*.jpg'):
  print(filename)
  
  # img = PIL.Image.new('RGBA', size = (100, 100), color = (128, 128, 128, 255))
  img = PIL.Image.open(filename)
  mask= PIL.Image.new("L", img.size, 0)
  draw = PIL.ImageDraw.Draw(mask)
  draw.ellipse((0, 0, img.size[0], img.size[1]), fill=255)
  del draw

  # Now I draw the circle:
  # p_x, p_y = 50, 50
  # canvas.ellipse((p_x - 5, p_y - 5, p_x + 5, p_y + 5), fill=(255, 128, 10, 50))
  img.putalpha(mask)


  # now save and close

  img.save(filename.with_suffix('.png'), 'PNG')