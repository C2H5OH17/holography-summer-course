from PIL import Image, ImageDraw, ImageFont


def create_character_image(character, output_path, width=1920, height=1080, font_size=900):
# def create_character_image(character, output_path, width=1080, height=1920, font_size=900):
    """
    生成一个指定文字居中显示的1080p图片

    参数:
    character (str): 要显示的字符
    output_path (str): 图片保存路径
    width (int): 图片宽度，默认为1920 (1080p)
    height (int): 图片高度，默认为1080 (1080p)
    font_size (int): 字体大小，默认为900
    """
    # 创建白色背景的图像 (24位真彩色)
    image = Image.new('RGB', (width, height), (255, 255, 255))
    # image = Image.new('RGB', (width, height), (0,0,0))
    draw = ImageDraw.Draw(image)

    # 尝试加载中文字体
    font_path = None
    # 检查常见系统字体路径
    possible_fonts = [
        "simhei.ttf",  # Windows
        "/System/Library/Fonts/PingFang.ttc",  # macOS
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # Linux
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"  # Linux/BSD
    ]

    for font in possible_fonts:
        try:
            ImageFont.truetype(font, 10)  # 测试字体是否存在
            font_path = font
            break
        except IOError:
            continue

    if font_path:
        font = ImageFont.truetype(font_path, font_size)
    else:
        # 如果都失败，使用PIL默认字体，但可能无法正确显示中文
        print("警告: 未找到中文字体，使用默认字体，可能无法正确显示中文")
        font = ImageFont.load_default()

    # 计算文本尺寸
    text_bbox = draw.textbbox((0, 0), character, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # 计算居中位置
    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # 在图像上绘制文字
    draw.text((x, y), character, font=font, fill=(0, 0, 0))
    # draw.text((x, y), character, font=font, fill=(255, 255, 255))

    # 保存为BMP格式
    image.save(output_path, "BMP")
    print(f"图像已保存为: {output_path}")
    print(f"分辨率: {width}x{height}")
    print(f"字体大小: {font_size}")


if __name__ == "__main__":
    # 指定输出路径和文件名
    output_path = "light_1080p.png"
    # output_path = "../holography_test/xin_1080p.png"
    create_character_image("光", output_path)