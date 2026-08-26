import os
from PIL import Image, ImageDraw, ImageFont

os.makedirs('logos', exist_ok=True)

def create_channels_tv_logo(path):
    size = (512, 512)
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Background rounded rectangle
    draw.rounded_rectangle([16, 16, 496, 496], radius=64, fill=(10, 30, 80, 255), outline=(0, 160, 255, 255), width=8)
    
    # Inner circular emblem
    draw.ellipse([70, 60, 442, 432], fill=(15, 65, 160, 255), outline=(255, 255, 255, 200), width=6)
    
    # Red accent arc / banner
    draw.chord([90, 80, 422, 412], start=160, end=380, fill=(220, 20, 40, 255))
    
    # Text
    try:
        font_large = ImageFont.truetype("arialbd.ttf", 64)
        font_small = ImageFont.truetype("arialbd.ttf", 36)
        font_badge = ImageFont.truetype("arialbd.ttf", 28)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_badge = ImageFont.load_default()
        
    draw.text((256, 210), "CHANNELS", fill=(255, 255, 255, 255), font=font_large, anchor="mm")
    draw.text((256, 280), "TELEVISION", fill=(255, 215, 0, 255), font=font_small, anchor="mm")
    
    # HD Badge
    draw.rounded_rectangle([206, 330, 306, 375], radius=10, fill=(220, 20, 40, 255), outline=(255, 255, 255, 255), width=3)
    draw.text((256, 352), "HD", fill=(255, 255, 255, 255), font=font_badge, anchor="mm")
    
    img.save(path, "PNG")
    print(f"Generated {path}")

def create_tvc_news_logo(path):
    size = (512, 512)
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Rounded badge background
    draw.rounded_rectangle([16, 16, 496, 496], radius=64, fill=(180, 20, 20, 255), outline=(255, 140, 0, 255), width=8)
    
    # Golden / Orange angled banner
    draw.polygon([(16, 280), (496, 180), (496, 360), (16, 460)], fill=(230, 90, 0, 255))
    
    try:
        font_huge = ImageFont.truetype("arialbd.ttf", 110)
        font_news = ImageFont.truetype("arialbd.ttf", 52)
        font_sub = ImageFont.truetype("arialbd.ttf", 32)
    except:
        font_huge = ImageFont.load_default()
        font_news = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        
    draw.text((256, 160), "TVC", fill=(255, 255, 255, 255), font=font_huge, anchor="mm")
    draw.text((256, 275), "NEWS", fill=(255, 240, 200, 255), font=font_news, anchor="mm")
    draw.text((256, 370), "NIGERIA", fill=(255, 255, 255, 255), font=font_sub, anchor="mm")
    
    img.save(path, "PNG")
    print(f"Generated {path}")

def create_arise_news_logo(path):
    size = (512, 512)
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Bold black & red rounded box
    draw.rounded_rectangle([16, 16, 496, 496], radius=64, fill=(15, 15, 15, 255), outline=(230, 0, 0, 255), width=10)
    
    # Ruby red center banner
    draw.rounded_rectangle([40, 130, 472, 380], radius=24, fill=(215, 15, 30, 255))
    
    try:
        font_arise = ImageFont.truetype("arialbd.ttf", 96)
        font_news = ImageFont.truetype("arialbd.ttf", 54)
        font_live = ImageFont.truetype("arialbd.ttf", 26)
    except:
        font_arise = ImageFont.load_default()
        font_news = ImageFont.load_default()
        font_live = ImageFont.load_default()
        
    draw.text((256, 215), "ARISE", fill=(255, 255, 255, 255), font=font_arise, anchor="mm")
    draw.text((256, 310), "NEWS", fill=(255, 255, 255, 255), font=font_news, anchor="mm")
    
    # Live indicator dot + text
    draw.ellipse([180, 420, 204, 444], fill=(0, 230, 50, 255))
    draw.text((260, 432), "GLOBAL HD", fill=(200, 200, 200, 255), font=font_live, anchor="mm")
    
    img.save(path, "PNG")
    print(f"Generated {path}")

def create_nolly_africa_logo(path):
    size = (512, 512)
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Emerald & Gold African TV theme
    draw.rounded_rectangle([16, 16, 496, 496], radius=64, fill=(5, 45, 25, 255), outline=(235, 180, 20, 255), width=8)
    draw.rounded_rectangle([45, 45, 467, 467], radius=48, fill=(10, 70, 40, 255), outline=(255, 255, 255, 100), width=4)
    
    try:
        font_top = ImageFont.truetype("arialbd.ttf", 74)
        font_mid = ImageFont.truetype("arialbd.ttf", 64)
        font_hd = ImageFont.truetype("arialbd.ttf", 36)
    except:
        font_top = ImageFont.load_default()
        font_mid = ImageFont.load_default()
        font_hd = ImageFont.load_default()
        
    draw.text((256, 170), "NOLLY", fill=(255, 215, 0, 255), font=font_top, anchor="mm")
    draw.text((256, 265), "AFRICA", fill=(255, 255, 255, 255), font=font_mid, anchor="mm")
    
    # Golden HD pill badge
    draw.rounded_rectangle([196, 335, 316, 395], radius=16, fill=(235, 180, 20, 255))
    draw.text((256, 365), "HD", fill=(10, 45, 25, 255), font=font_hd, anchor="mm")
    
    img.save(path, "PNG")
    print(f"Generated {path}")

if __name__ == "__main__":
    create_channels_tv_logo("logos/channels_tv.png")
    create_tvc_news_logo("logos/tvc_news.png")
    create_arise_news_logo("logos/arise_news.png")
    create_nolly_africa_logo("logos/nolly_africa.png")
    print("All logos generated successfully!")
