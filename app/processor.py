from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageFilter, ImageOps
from rembg import remove

from .config import Settings


class BackgroundComposer:
    def __init__(self, settings: Settings):
        self.settings = settings

    def compose(self, source_path: Path, output_path: Path) -> None:
        background_path = Path(self.settings.background_path)
        if not background_path.exists():
            raise FileNotFoundError("Background is not configured. Admin must send /set_background first.")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        background = Image.open(background_path).convert("RGBA")
        source = Image.open(source_path).convert("RGBA")
        cutout = remove(source)
        cutout = self._trim_alpha(cutout)

        max_w = int(background.width * self.settings.placement_width_ratio)
        max_h = int(background.height * self.settings.placement_height_ratio)
        cutout.thumbnail((max_w, max_h), Image.LANCZOS)

        x = (background.width - cutout.width) // 2
        bottom_margin = int(background.height * self.settings.placement_bottom_margin_ratio)
        y = background.height - cutout.height - bottom_margin
        y = max(0, y)

        result = background.copy()
        shadow = Image.new("RGBA", result.size, (0, 0, 0, 0))
        shadow_alpha = cutout.getchannel("A").filter(ImageFilter.GaussianBlur(14))
        shadow_layer = Image.new("RGBA", cutout.size, (0, 0, 0, 92))
        shadow_layer.putalpha(shadow_alpha)
        shadow.alpha_composite(shadow_layer, (x + 8, min(result.height - cutout.height, y + 10)))
        result = Image.alpha_composite(result, shadow)
        result.alpha_composite(cutout, (x, y))
        result.convert("RGB").save(output_path, quality=95)

    @staticmethod
    def _trim_alpha(image: Image.Image) -> Image.Image:
        alpha = image.getchannel("A")
        bbox = alpha.getbbox()
        if bbox is None:
            return image
        return image.crop(bbox)
