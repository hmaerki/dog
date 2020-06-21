import pathlib

DIRECTORY_OF_THIS_FILE = pathlib.Path(__file__).parent.absolute()
for i, filename in enumerate(sorted(DIRECTORY_OF_THIS_FILE.glob('*.jpg'))):
  print(i, filename)
  filename.rename(f'marble{i+10:02d}.jpg')