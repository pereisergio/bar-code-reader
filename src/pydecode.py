from pyzbar import pyzbar
from PIL import Image

class DecodeBar:
    def __init__(self, path) -> None:
        self.image = Image.open(path)

    def decoded_bar(self):
        return pyzbar.decode(self.image)
    
if __name__ == '__main__':
    code = DecodeBar('C:/temp/capture/bar_capture.png').decoded_bar()