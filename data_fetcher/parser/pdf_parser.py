import os
import pdfplumber
from pathlib import Path
from data_platform.config import ConfigManager

current_path = Path(os.path.join(os.getcwd(), "../.."))
data_path = current_path / 'data'
xml_path = data_path / 'unprocessed_articles_xml'
pdf_path = data_path / 'pdf_files'
config = ConfigManager({
    "init": {
        "location": xml_path,
        "pdf": pdf_path
    }
})

X_TOLERANCE = 1
Y_TOLERANCE = 1


def parse(config, filename):

    text = ""
    with pdfplumber.open(Path(config.check_get(["init", "pdf"])) / filename) as pdf:
        for page in pdf.pages:
            left = page.within_bbox((float(page.width)*0.06, float(page.height)*0.07, float(page.width)*0.5, float(page.height)*(1-0.05)))
            right = page.within_bbox((float(page.width)*0.5, float(page.height)*0.07, float(page.width)*(1-0.06), float(page.height)*(1-0.05)))
            text += extract_text(left.chars)
            text += extract_text(right.chars)
            # text += ''.join([item['text'] for item in left.chars])
            # text += ''.join([item['text'] for item in right.chars])
    # print(text)
    paragraphs = text.split('\n')
    output = list()
    cur_paragraph = ""
    for p in paragraphs:
        # 接续当前段
        cur_paragraph += p
        if p.strip().endswith('.') or p.strip().endswith('!') or p.strip().endswith('?'):
            # 遇到段尾，存储当前段
            output.append(cur_paragraph)
            cur_paragraph = ""

    for p in output:
        print(p)


def extract_text(chars, x_tolerance=X_TOLERANCE, y_tolerance=Y_TOLERANCE):

    if len(chars) <= 1:
        return ''.join(chars)
    cur_char = chars[0]
    text = ""
    for raw_char in chars[1:]:
        char = raw_char['text'].strip()
        # if cur_char['text'] == 'l' and raw_char['text'] == 'w':
        #     print(cur_char['top'], cur_char['bottom'], cur_char['height'], raw_char['top'], raw_char['bottom'], raw_char['height'])
        if raw_char['top'] >= cur_char['bottom']-raw_char['height']/10:
            if cur_char['text'].isalnum():
                text += ' '
                text += '\n'
            elif cur_char['text'] == '-':
                text = text[:-1]
            else:
                text += '\n'
        elif raw_char['x0'] >= cur_char['x1'] + x_tolerance:
            text += ' '
        text += char
        cur_char = raw_char
    if not text.endswith('\n'):
        text += '\n'
    return text


if __name__ == "__main__":

    pdf_name = "Selling Virtual Currency in Digital Games Implications for Gameplay and Social Welfare.pdf"
    parse(config, pdf_name)
