import itertools
from PIL import Image

def hstack(lr, space=0):
    lr = list(lr)
    widths, heights = zip(*(i.size for i in lr))
    total_width = sum(widths)
    total_width += (len(lr) - 1) * space
    max_height = max(heights)
    im = Image.new('RGBA', (total_width, max_height))
    x_offset = 0
    for i in lr:
        im.paste(i, (x_offset, (max_height-i.size[1])//2), i)
        x_offset += i.size[0] + space
    return im

def vstack(tb, space=0, align="left"):
    tb = list(tb)
    widths, heights = zip(*(i.size for i in tb))
    max_width = max(widths)
    total_height = sum(heights)
    total_height += (len(tb) - 1) * space
    im = Image.new('RGBA', (max_width, total_height))
    y_offset = 0
    for i in tb:
        if align == "center":
            x = (max_width-i.size[0])//2
        elif align == "left":
            x = 0
        im.paste(i, (x, y_offset), i)
        y_offset += i.size[1] + space
    return im

claw = Image.open("dino_print.png")
#claw = claw.resize((8, 10))

radicals = [claw.rotate(d, expand=True) for d in [0, 90, 180, 270]]

def question_mark():
    horiz = hstack([claw.rotate(90), claw.rotate(270)], space=10)
    vert = vstack([claw, claw.rotate(180)], space=10)
    im = Image.new('RGBA', (horiz.size[0], vert.size[1]))
    x_offset = 0
    im.paste(horiz, (0, (vert.size[1]-horiz.size[1])//2), horiz)
    im.paste(vert, ((horiz.size[0]-vert.size[0])//2, 0), vert)
    return im

from PIL import ImageOps, ImageDraw
def period():
    size = (20, 20)
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask) 
    draw.ellipse((0, 0) + size, fill=255)
    output = ImageOps.fit(claw, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)
    return output

glyphs = "abcdefghijklmnopqrstuvwxyz0123456789?."
def generate():
    combos = list(itertools.product(radicals, radicals))
    for r in radicals:
        yield r
    for c in combos:
        yield vstack(reversed(c), space=-4, align="center")
    for c in combos:
        yield hstack(c, space=-5)
    yield question_mark()
    yield period()

alphabet = dict(zip(glyphs, generate()))


def word(letters):
    return hstack([alphabet[l] for l in letters], space=10)

def flow(words, linewidth=2000, minspace=80):
    lines = []
    l = []
    total = 0
    for w in [word(w) for w in words]:
        if total + w.size[0] > linewidth:
            wordswidth = sum(w.size[0] for w in l)
            #space = (linewidth - wordswidth) // (len(l)-1)
            space = minspace
            lines.append(hstack(l, space=space))
            l = []
            total = 0
        total += w.size[0] + minspace
        l.append(w)
    wordswidth = sum(w.size[0] for w in l)
    #space = (linewidth - wordswidth) // (len(l)-1)
    space = minspace
    lines.append(hstack(l, space=space))
    return vstack(lines, space=100)  # TODO make all lines same height and width!

def break_paras(text):
    paras = []
    para = ""
    for line in text.splitlines():
        if not len(line):
            if para: paras.append(flow(para.split()))
            para = ""
        else:
            para += " " + line
    if para: paras.append(flow(para.split()))
    return vstack(paras, space=200)

def encode(text, width_inches=7, height_inches=9, dpi=96):
    text = "".join(c for c in text.lower() if c in alphabet or c.isspace())
    rgba = break_paras(text)
    result = Image.new('RGB', rgba.size, (255, 255, 255))
    result.paste(rgba, mask=rgba.split()[3])  # 3 is the alpha channel
    result.thumbnail([width_inches * dpi, height_inches * dpi])
    return result
