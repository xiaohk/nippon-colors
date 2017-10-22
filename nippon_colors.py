import colorsys
from json import load, dump
from xml.etree import ElementTree as ET 


def hex_to_rgb_hls(hex_str):
    """ Convert hex string to a rgb list in 255 scale, and a hsv list in
        float scale.
    """

    if len(hex_str) > 6:
        hex_str = hex_str[1:]

    # Convert to rgb
    rgb = []
    for i in range(0, 6, 2):
        rgb.append(int(hex_str[i:i+2], 16))

    # Convert to hsv
    hls = list(colorsys.rgb_to_hls(*[i / 255 for i in rgb]))
    
    return rgb, hls


def convert_json(in_fname, out_fname):
    """ Add more feature to the JSON, and sort dicts by hue value"""

    # Load JSON
    with open(in_fname, 'r') as fp:
        c1 = load(fp)
        kanji = [d['name'] for d in c1]
        color = [d['value'] for d in c1]
        romanji = [d['romanized'].lower() for d in c1]
        rgb, hls = [], []
        for h in color:
             rgb_and_hls = hex_to_rgb_hls(h)
             rgb.append(rgb_and_hls[0])
             hls.append(rgb_and_hls[1])
        
        # Build my list
        dict_list = []
        for i in range(len(color)):
            dict_list.append({
                'romanji': romanji[i],
                'kanji': kanji[i],
                'hex': color[i],
                'rgb': rgb[i],
                'hls': hls[i]
            })
        
        # Sort the color
        black_colors, white_colors, gray_colors, other_colors = [], [], [], []

        for i in dict_list:
            if i['hls'][1] < 0.2:
                black_colors.append(i)
            elif i['hls'][1] > 0.8:
                white_colors.append(i)
            elif i['hls'][2] < 0.25:
                gray_colors.append(i)
            else:
                other_colors.append(i)

        black_colors.sort(key=lambda dic: dic['hls'][1])
        white_colors.sort(key=lambda dic: dic['hls'][1])
        gray_colors.sort(key=lambda dic: dic['hls'][2])
        other_colors.sort(key=lambda dic: dic['hls'][0])

        sorted_list = other_colors + white_colors + gray_colors + black_colors

        # Dump JSON
        with open(out_fname, 'w') as fp2:
            dump(sorted_list, fp2, sort_keys=False, indent=4, ensure_ascii=False)


def generate_svg(color_dic):
    """Generate a svg image using the given color dictionary/"""
    image = ET.Element('svg', width='200', height='300', version='1.1',
                       xmlns='http://www.w3.org/2000/svg')
    # Draw a rectangle
    ET.SubElement(image, 'rect', x="0", y="0", width="200", height="300",
                 fill="rgb({},{},{})".format(*color_dic['rgb']))

    # Different Positions/size based on the length of kanji and romanji

    kanji_x, kanji_y, kanji_size = '100', '50', '45px'
    romanji_x, romanji_y, romanji_size = '100', '250', '30px'

    if len(color_dic['kanji']) == 3:
        kanji_size = '40px'
    elif len(color_dic['kanji']) == 4:
        kanji_y, kanji_size, romanji_y = '20', '40px', '270'
    elif len(color_dic['kanji']) > 4:
        kanji_y, kanji_size, romanji_y = '20', '35px', '275'

    if len(color_dic['romanji']) > 12:
        romanji_size = '25px'
    if len(color_dic['romanji']) > 16:
        romanji_size = '22px'

    # Add Kanji
    kanji = ET.Element('text', x=kanji_x, y=kanji_y, fill='white',
                       style='font-family: osaka, sans-serif;' +
                             'font-size: {};'.format(kanji_size) +
                             'writing-mode: tb')
    kanji.text = color_dic['kanji']
    image.append(kanji)

    # Add Romanji
    romanji = ET.Element('text', x=romanji_x, y=romanji_y, fill='white',
                       style='font-family: -apple-system, BlinkMacSystemFont,'+
                                          '"Helvetica Neue", sans-serif;' +
                             'font-size: {};'.format(romanji_size) +
                             'text-anchor: middle;' +
                             'dominant-baseline: top')
    romanji.text = color_dic['romanji']
    image.append(romanji)

    # Write header and dump xml
    with open('images/{}.svg'.format(color_dic['romanji']), 'w') as fp:
        fp.write('<?xml version=\"1.0\" standalone=\"no\"?>\n' +
                 '<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\"\n' +
                 '\"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">\n')
        fp.write(ET.tostring(image, encoding='unicode'))


def generate_markdown(out_fname):
    """ Generate README.MD while generating svg on the fly"""
    LINE = '[<img src="./images/{}.svg">](https://irocore.com/{}/)'
    with open('nippon_colors.json', 'r') as fp1:
        with open(out_fname, 'w') as fp2:
            color_list = load(fp1)
            for color in color_list:
                generate_svg(color)
                fp2.write(LINE.format(color['romanji'], color['romanji']))


generate_markdown("README.md")
#convert_json('colors.json', 'nippon_colors.json')
#with open('nippon_colors.json', 'r') as fp:
#    color_list = load(fp)
#    for color in color_list:
#        if len(color['romanji']) > 11:
#            generate_svg(color)
    #generate_svg(color_list[46])
