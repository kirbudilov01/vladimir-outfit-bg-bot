from PIL import Image

from app.processor import BackgroundComposer


def test_trim_alpha_keeps_nontransparent_area():
    image = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    for x in range(3, 7):
        for y in range(2, 6):
            image.putpixel((x, y), (255, 255, 255, 255))

    trimmed = BackgroundComposer._trim_alpha(image)
    assert trimmed.size == (4, 4)
