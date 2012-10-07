# EVE Map library

from PIL import Image, ImageDraw

class EveMapDraw(object):
    def __init__(self, im, bounding_box, offset=None,
                 xoffset=None, yoffset=None):
        self.im = im
        self.draw = ImageDraw.Draw(im)
        (xmin, xmax, ymin, ymax) = bounding_box
        if offset is not None:
            xoffset = yoffset = offset
        (image_width, image_height) = im.size
        if xoffset is None:
            xoffset = image_width * 0.05
        if yoffset is None:
            yoffset = image_height * 0.05
        xscale = float(image_width + -1 + -2*xoffset) / abs(xmax - xmin)
        yscale = float(image_height + -1 + -2*yoffset) / abs(ymax - ymin)
        self.xscale = lambda x: ((x - xmin) * xscale) + xoffset
        self.yscale = lambda y: ((y - ymin) * yscale) + yoffset

    def text(self, coords, text, **kwargs):
        (x, y) = coords
        x = self.xscale(x)
        y = self.yscale(y)
        self.draw.text((x, y), text, **kwargs)
