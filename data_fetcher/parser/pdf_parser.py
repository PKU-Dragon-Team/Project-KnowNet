import pdfplumber


class PDFFormat:
    # columns: pdf栏数，只考虑1和2的情况，小于1会被截取为1，大于2会被截取为2
    # bbox: pdf四边缘站总长/宽的比例，四元素依次为左、上、右、下
    DEFAULT = {"columns": 2, "bbox": (0.05, 0.08, 0.95, 0.9)}
    IEEE = {"columns": 2, "bbox": (0.05, 0.08, 0.95, 0.9)}


class PDFParser:
    X_TOLERANCE = 1
    Y_TOLERANCE = 1

    def parse(self, filename: str, pdf_format: dict = PDFFormat.DEFAULT) -> str:
        """
            将给定路径的pdf转化为str
            filename: pdf路径;
            pdf_format: PDF的格式，具体参数见本包内PDFFormat类
        """
        text = ""
        if "columns" not in pdf_format or "bbox" not in pdf_format:
            pdf_format = PDFFormat.DEFAULT
            print("The pdf format is illegal and automatically assigned to DEFAULT format!")
        with pdfplumber.open(filename) as pdf:
            columns = pdf_format["columns"]
            bbox = pdf_format["bbox"]
            # 单栏
            if columns <= 1:
                for page in pdf.pages:
                    box = page.within_bbox((float(page.width) * bbox[0],
                                            float(page.height) * bbox[1],
                                            float(page.width) * bbox[2],
                                            float(page.height) * bbox[3]))
                    text += self._extract_text(box.chars)
            # 双栏
            else:
                for page in pdf.pages:
                    left = page.within_bbox((float(page.width) * bbox[0],
                                             float(page.height) * bbox[1],
                                             float(page.width) * 0.5,
                                             float(page.height) * bbox[3]))
                    right = page.within_bbox((float(page.width) * 0.5,
                                              float(page.height) * bbox[1],
                                              float(page.width) * bbox[2],
                                              float(page.height) * bbox[3]))
                    text += self._extract_text(left.chars)
                    text += self._extract_text(right.chars)
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
        # for p in output:
        #     print(p)
        return '\n'.join(output)

    def _extract_text(self, chars, x_tolerance=X_TOLERANCE, y_tolerance=Y_TOLERANCE):

        if len(chars) <= 1:
            return ''.join(chars)
        cur_char = chars[0]
        text = ""
        for raw_char in chars[1:]:
            char = raw_char['text'].strip()
            # if cur_char['text'] == 'l' and raw_char['text'] == 'w':
            #     print(cur_char['top'], cur_char['bottom'], cur_char['height'],
            #     raw_char['top'], raw_char['bottom'], raw_char['height'])
            if raw_char['top'] >= cur_char['bottom'] - raw_char['height'] / 10:
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

    parser = PDFParser()
    pdf_name = '../data/pdf_files/8588673.pdf'
    parser.parse(pdf_name)
