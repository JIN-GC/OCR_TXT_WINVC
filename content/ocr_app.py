# OCR Ver.Win11.Home.Eclipse.20231006

import os
# import PIL
from PIL import Image
from PIL import ImageFilter
from PIL import ImageEnhance
from PIL.ImageDraw import ImageDraw
# from IPython.display import display # .google.colab用：display(pil_image)
import pyocr
# import cv2
# from cv2 import *
import time
import datetime
from pathlib import Path
from shutil import copytree

import re
import unicodedata


def main():
    # 処理時間計測開始
    proc_start = time.perf_counter()

    # メディア情報準備
    src_dir = 'content/src_dir/'    # 入力・読込用
    dst_dir = 'content/dst_dir/'    # 出力用
#    bak_dir = 'content/bak_dir/'    # バックアップ用

    # バックアップ
#    backup_media_proc(src_dir, bak_dir)
    # 画像ファイル名抽出
    # files_list = list()

    files_list = extract_media_proc(src_dir)
    # improve_image_test_proc(src_dir, files_list)
    # file_name = '郵送-通信費-532-37.JPG' # 入出力ファイル名
    # ocr_proc(file_name, src_dir, dst_dir)

##    improve_image_proc(src_dir, dst_dir, files_list)
    for file_name in files_list:
        ocr_proc(file_name, src_dir, dst_dir)

    # 処理時間表示
    show_proc_time('*** OCR PROCESS COMPLETED ***', time.perf_counter() - proc_start)





# タイムスタンプ
def time_stamp():
    return str(datetime.datetime.now().strftime('%Y%m%d%H%M%S%f'))

# 処理時間計測表示
def show_proc_time(subject, elapsed_time):
    time_h = int(elapsed_time / (60 * 60))
    time_m = int((elapsed_time % (60 * 60)) / 60)
    time_s = int(elapsed_time % 60)
    time_f = int(elapsed_time * 1000000)
    # if len(subject.encode()) > 36:
    #     print(f'{"*****" * 1} {time_h:02}:{time_m:02}:{time_s:02}.{time_f:08}{"*****" * 1} {subject:^2} {"*****" * 1}')
    # elif len(subject.encode()) > 18:
    # print(f'{"*****" * 1} {time_h:02}:{time_m:02}:{time_s:02}.{time_f:06} {"*****" * 1} {subject:^22} {"*****" * 1}')
    print(f'**{"*****" * 10} {time_h:02}:{time_m:02}:{time_s:02}.{time_f:06} {"*****" * 1}')
    # elif len(subject.encode()) > 9:
    #     print(f'{"*****" * 1} {time_h:02}:{time_m:02}:{time_s:02}.{time_f:08} {"*****" * 1} {subject:^16} {"*****" * 1}')

# バックアップ（画像ファイル名の抽出リスト参照）
def backup_media_proc(src_dir = 'content/src_dir/', bak_dir = 'content/bak_dir/'):
    copytree(src_dir, bak_dir + time_stamp())

# 画像ファイル名抽出    # Python/Pillow(PIL)サポートタイプ用 (pathlib ＆ glob)
def extract_media_proc(src_dir = 'content/src_dir/'):
    # 抽出対象拡張子
    extension = ['.bmp', '.dib', '.eps', '.gif', '.icns', '.ico', '.im', '.jpg', '.jpeg', '.jpeg2000', '.msp', '.pcx', '.png', '.ppm', '.sgi', '.spider', '.tga', '.tiff', '.webp', '.xmb', '.palm', '.pdf', '.xv', '.thumbnails']
    files_list = [ os.path.basename(i) for i in Path(src_dir).glob('**/*.*') if i.suffix.lower() in extension]
    # print(files_list)   # For Check
    return files_list

# 画質改善（画像ファイル名の抽出リスト参照）
def improve_image_proc(src_dir, dst_dir, files_list):
    for file_name in files_list:
        # 入力用ファイル準備
        source_image = Image.open(src_dir + file_name)

        # ガウス分布を使用して画像をぼかし(ガウシアン)  # Gaussianフィルタ：引数: 画像データ, カーネル(ぼかし)の縦幅・横幅, 横方向の標準偏差, 縦方向の標準偏差(省略時はsigmaX値)
        blurred_image = source_image.filter(ImageFilter.GaussianBlur(radius=10))

        # コントラスト調整(文字濃淡)
        enhancer = ImageEnhance.Contrast(source_image)
        enhanced_image = enhancer.enhance(2.0)  # 2.0は濃淡の強度

        # 画像サイズ調整
        width, height = source_image.size
        blurred_image = blurred_image.resize((width, height))
        enhanced_image = enhanced_image.resize((width, height))

        # アルファチャンネル(透明度)を含む画質形式に変換 RBG to RGBA(R:Red G:Green B:Blue A:Alpha:透明度)
        blurred_image_rgba = blurred_image.convert("RGBA")
        enhanced_image_rgba = enhanced_image.convert("RGBA")

        # 背景と文字の合成(前景RGBA×前景のアルファ ＋ 背景RGBA×(1-前景のアルファ) ＝　掛け合せ合成)
        merged_image = Image.alpha_composite(blurred_image_rgba, enhanced_image_rgba)
        # merged_image = merged_image.convert("RGB")
        merged_image = merged_image.convert("RGB")

        # 画像表示
        # genereted_image.show() # For Check
        merged_image.save(dst_dir + file_name)
        # ファイルクローズ
        # genereted_image.close() # close()はgifなどのmulti-frameメディア対策
        
# 画質改善（ファイル単体用）
def improve_image_test_proc(file_name, src_dir = 'content/src_dir/', dst_dir = 'content/dst_dir/'):
    img_file = Image.open(src_dir + file_name)
    # 輪郭強調(弱)
    # img_file.filter(ImageFilter.EDGE_ENHANCE).save(dst_dir + file_name)
    # 輪郭強調(強)
    img_file.filter(ImageFilter.EDGE_ENHANCE_MORE).save(dst_dir + file_name)
    # 高画質化(細かい部分を強調)
    # img_file.filter(ImageFilter.DETAIL).save(dst_dir + file_name)
    # シャープマスク(細かい部分を強調)
    # img_file.filter(ImageFilter.SHARPEN).save(dst_dir + file_name)
    # アンシャープマスク
    # img_file.filter(ImageFilter.UnsharpMask(radius=10, percent=200, threshold=5)).save(dst_dir + file_name)
    # # Pillow/PIL API
    # def __init__(self, radius=2, percent=150, threshold=3):
    # self.radius = radius
    # self.percent = percent
    # self.threshold = threshold

    return img_file

# 電話番号抽出
def extract_pnumbers_proc(ocr_txt):
    # 半角全角変換(全角英数字->半角英数字, 半角ｶﾅ->全角カナ, ①->1, ㈱-> (株),『か』+『゛』の結合文字->1文字の『が』)
    ocr_txt = unicodedata.normalize('NFKC', ocr_txt)

    # # 抽出処理方式Ａ
    # # 置換処理
    # ocr_txt = ocr_txt.replace("ｃ", "0").replace("Ｃ", "0").replace("d", "0").replace("D", "0").replace("ｄ", "0").replace("Ｄ", "0").replace("n", "0").replace("ｎ", "0").replace("o", "0").replace("O", "0").replace("ｏ", "0").replace("Ｏ", "0").replace("Ο", "0").replace("○", "0").replace("О", "0").replace("〇", "0").replace("u", "0").replace("U", "0").replace("ｕ", "0").replace("Ｕ", "0").replace("ц", "0").replace("∪", "0").replace("q", "9").replace("Q", "9").replace("ｑ", "0").replace("Ｑ", "0").replace("@", "0").replace("＠", "0").replace("i", "1").replace("I", "1").replace("ｉ", "1").replace("Ｉ", "1").replace("l", "1").replace("L", "1").replace("ｌ", "1").replace("Ｌ", "1").replace("!", "1").replace("！", "1").replace("「", "1").replace("」", "1").replace("『", "1").replace("』", "1").replace("|", "1").replace("｜", "1").replace("¦", "1").replace("¦", "1").replace("⋮", "1").replace("❘", "1").replace("Ι", "1").replace("Ⅰ", "1").replace("ⅱ", "11").replace("Ⅱ", "11").replace("ⅲ", "111").replace("Ⅲ", "111").replace("z", "2").replace("Z", "2").replace("ｚ", "2").replace("Ｚ", "2").replace("Ζ", "2").replace("b", "6").replace("ｂ", "6").replace("G", "6").replace("Ｇ", "6").replace("/", "7").replace("／", "7").replace("B", "8").replace("Ｂ", "8").replace("в", "8").replace("g", "9").replace("ｇ", "9").replace("q", "9").replace("ｑ", "9")
    # ocr_txt = ocr_txt.replace(".", "").replace("．", "").replace("。", "").replace(",", "").replace("，", "").replace("、", "").replace("・", "").replace(":", "").replace("：", "").replace(";", "").replace("；", "").replace(" ", "").replace("　", "").replace("\t", "").replace("\n", "").replace("(", "").replace("（", "").replace("[", "").replace("［", "").replace("〔", "").replace("{", "").replace("｛", "").replace("<", "").replace("＜", "").replace("〈", "").replace("〉", "-").replace("《", "").replace("≪", "")
    # ocr_txt = ocr_txt.replace("T", "-").replace("Ｔ", "-").replace(")", "-").replace("）", "-").replace("]", "-").replace("］", "-").replace("〕", "-").replace("}", "-").replace(">", "-").replace("＞", "-").replace("｝", "-").replace("》", "-").replace("≫", "-").replace("_", "-").replace("__", "-").replace("___", "-").replace("=", "-").replace("==", "-").replace("===", "-").replace("＝", "-").replace("＝＝", "-").replace("＝＝＝", "-").replace("＿", "-").replace("＿＿", "-").replace("＿＿＿", "-").replace("ー", "-").replace("ーー", "-").replace("ーーー", "-").replace("一", "-").replace("一一", "-").replace("一一一", "-").replace("一", "-").replace("一一", "-").replace("一一一", "-").replace("--", "-").replace("---", "-")
    # # 正規表現パターン
    # pattern = r'0[1-9]\d{8}|0[1-9]\d{2}[-]\d{6}|0[1-9]\d{2}[-]\d{3}[-]\d{3}|0[1-9][-]\d{8}|0[1-9][-]\d{4}[-]\d{4}|0[1-9][0-9][-]\d{7}|0[1-9][0-9][-]\d{4}[-]\d{3}|0[1-9][0-9][-]\d{3}[-]\d{4}|0[1-9]\d{2}[-]\d{6}|0[1-9]\d{2}[-]\d{3}[-]\d{3}'
    #  # 電話番号抽出
    # found_phone_numbers = re.findall(pattern, ocr_txt)


    # 抽出処理方式Ｂ
    # 電話番号を抽出する正規表現パターン(unicodedata.normalize関数で変換しているが念の為該当文字含め抽出)
    # pattern = r'0[1-9]\d{0,3}[-－ー一_＿ ()（）〔〕 　 \s\t]*\d{2,4}[-－ー一_＿ ()（） 　 \s\t]*\d{2,4}[-－ー一_＿ ()（） 　 \s\t]*\d{2,4}'
    # pattern = r'[0０oOcCDQ][0-9０-９dDcCqQlL1][0-9０-９oOcCdDqQlZzL1 -_＿ー一()（） 　\s\t]{3,9}[0-9０-９oOcCdDqQlZzL1 　\s\t\n]+[ 　\s\t\n]'
    pattern = r'[0０〇cCｃＣdDｄＤGＧnｎoOｏＯuUｕＵＱοΟО@＠][1-9１-９iIｉＩlLｌＬ」］ⅰⅠⅱⅡⅲⅢzZｚＺbｂбBＢВgｇqｑ"/／"][0-9０-９ -_＿ー一()（） 　 \s\t]{3,9}[0-9０-９oO０〇cCｃＣdDｄＤGＧnｎoOｏＯuUｕＵＱοΟО@＠iIｉＩlLｌＬⅰⅠ」］ⅱⅡⅲⅢzZｚＺbｂбBＢВgｇqｑ"/／" 　 \s\t\n]+[ 　 \s\t\n]'
    #pattern = r'(?:[0０〇cCｃＣdDｄＤGＧnｎoOｏＯTＴuUUｕＵＱοΟО@＠".。,，、・"][1-9１-９iIｉＩlLｌＬ」］ⅰⅠⅱⅡⅲⅢ!！zZｚＺbｂбBＢВgｇqｑTＴ"=＝|｜/／.。,，、・"][0-9０-９ -_＿ー一()（）oO０〇cCｃＣdDｄＤGＧnｎoOｏＯTＴuUｕＵＱοΟО@＠iIｉＩlLｌＬ」］ⅰⅠⅱⅡⅲⅢ!！zZｚＺbｂбBＢВgｇqｑ"=＝|｜/／.。,，、・" 　 \s\t]{3,9}[0-9０-９oO０〇cCｃＣdDｄＤGＧnｎoOｏＯTＴuUｕＵＱοΟО@＠iIｉＩlLｌＬ」］ⅰⅠⅱⅡⅲⅢ!！zZｚＺbｂбBＢВgｇqｑ"=＝|｜/／.。,，、・" 　 \s\t\n]+)[0-9０-９oO０〇cCｃＣdDｄＤGＧnｎoOｏＯTＴuUｕＵＱοΟО@＠iIｉＩlLｌＬ」］ⅰⅠⅱⅡⅲⅢ!！zZｚＺbｂбBＢВgｇqｑ"=＝|｜/／.。,，、・" 　 \s\t\n]?'
    # pattern = r'[0０oOｏＯcCｃＣdDｄＤuUｕＵqQｑＱ＠][0-9０-９oOｏＯcCｃＣdDｄＤuUｕＵqQｑＱ＠iIｉＩlLｌＬzZｚＺbｂ／][0-9０-９oOｏＯcCｃＣdDｄＤuUｕＵqQｑＱ＠iIｉＩlLｌＬzZｚＺbｂ／ 　-_＿ー一()（）\s\t]{3,9}[0-9０-９oOｏＯcCｃＣdDｄＤuUｕＵqQｑＱ＠iIｉＩlLｌＬzZｚＺbｂ/／ 　-_＿ー一\s\t\n]+[ 　\s\t\n]'
    # pattern = r'[0０oOｏＯcCｃＣdDｄＤuUｕＵqQｑＱ][0-9０-９oOｏＯcCｃＣdDｄＤuUｕＵqQｑＱiIｉＩlLｌＬzZｚＺbｂ][0-9０-９oOｏＯcCｃＣdDｄＤuUｕＵqQｑＱiIｉＩlLｌＬzZｚＺbｂ 　 -_＿ー一()（）\s\t]{3,9}[0-9０-９oOｏＯcCｃＣdDｄＤuUｕＵqQｑＱiIｉＩlLｌＬzZｚＺbｂ 　 -_＿ー一\s\t\n]+[ 　(（\s\t\n]'

    # 正規表現を使用して電話番号を抽出
    phone_numbers = re.findall(pattern, ocr_txt)

    # 表記揺れ修正
    # rp_phone_numbers = [phone.replace("\n", "").replace("_", "-").replace("＿", "-").replace("ー", "-").replace("一", "-").replace("(", "").replace(")", "-").replace("（", "").replace("）", "-").replace("O", "0").replace("c", "0").replace("C", "0").replace("d", "0").replace("D", "0").replace("q", "9").replace("Q", "9").replace("l", "1").replace("L", "1") for phone in phone_numbers]
    # rp_phone_numbers = [phone.replace("\n", "").replace("_", "-").replace("＿", "-").replace("ー", "-").replace("一", "-").replace("(", "").replace(")", "-").replace("（", "").replace("）", "-").replace("O", "0").replace("c", "0").replace("C", "0").replace("d", "0").replace("D", "0").replace("U", "0").replace("u", "0").replace("q", "9").replace("Q", "9").replace("l", "1").replace("L", "1").replace("/", "7") for phone in phone_numbers]
    rp_phone_numbers = [phone.replace(".", "").replace("．", "").replace("。", "").replace(",", "").replace("，", "").replace("、", "").replace(":", "").replace("：", "").replace(";", "").replace("；", "").replace(" ", "").replace("　", "").replace(" ", "").replace("\n", "").replace("(", "").replace("（", "").replace(")", "-").replace("）", "-").replace("[", "").replace("［", "").replace("]", "-").replace("］", "-").replace("〔", "").replace("〕", "-").replace("{", "").replace("｛", "").replace("}", "-").replace("｝", "-").replace("<", "").replace("＜", "").replace(">", "-").replace("＞", "-").replace("〈", "").replace("〉", "-").replace("《", "").replace("》", "-").replace("≪", "").replace("≫", "-").replace("_", "-").replace("__", "-").replace("＿", "-").replace("＿＿", "-").replace("ー", "-").replace("ーー", "-").replace("一", "-").replace("一一", "-").replace("一", "-").replace("一一", "-").replace("--", "-").replace("=", "-").replace("＝", "-").replace("T", "-").replace("T", "-").replace("c", "0").replace("C", "0").replace("ｃ", "0").replace("Ｃ", "0").replace("d", "0").replace("D", "0").replace("ｄ", "0").replace("Ｄ", "0").replace("n", "0").replace("ｎ", "0").replace("o", "0").replace("O", "0").replace("ｏ", "0").replace("Ｏ", "0").replace("Ο", "0").replace("○", "0").replace("О", "0").replace("〇", "0").replace("u", "0").replace("U", "0").replace("ｕ", "0").replace("Ｕ", "0").replace("ц", "0").replace("∪", "0").replace("q", "9").replace("Q", "9").replace("ｑ", "0").replace("Ｑ", "0").replace("@", "0").replace("＠", "0").replace("i", "1").replace("I", "1").replace("ｉ", "1").replace("Ｉ", "1").replace("l", "1").replace("L", "1").replace("ｌ", "1").replace("Ｌ", "1").replace("!", "1").replace("！", "1").replace("「", "1").replace("」", "1").replace("|", "1").replace("｜", "1").replace("¦", "1").replace("¦", "1").replace("⋮", "1").replace("❘", "1").replace("Ι", "1").replace("Ⅰ", "1").replace("ⅱ", "11").replace("Ⅱ", "11").replace("ⅲ", "111").replace("Ⅲ", "111").replace("z", "2").replace("Z", "2").replace("ｚ", "2").replace("Ｚ", "2").replace("Ζ", "2").replace("b", "6").replace("ｂ", "6").replace("G", "6").replace("Ｇ", "6").replace("/", "7").replace("／", "7").replace("B", "8").replace("Ｂ", "8").replace("в", "8").replace("g", "9").replace("ｇ", "9").replace("q", "9").replace("ｑ", "9") for phone in phone_numbers]
    rp_phone_numbers = [phone.replace(".", "").replace("．", "").replace("。", "").replace(",", "").replace("，", "").replace("、", "").replace(":", "").replace("：", "").replace(";", "").replace("；", "").replace(" ", "").replace("　", "").replace(" ", "").replace("\n", "").replace("(", "").replace("（", "").replace(")", "-").replace("）", "-").replace("[", "").replace("［", "").replace("]", "-").replace("］", "-").replace("〔", "").replace("〕", "-").replace("{", "").replace("｛", "").replace("}", "-").replace("｝", "-").replace("<", "").replace("＜", "").replace(">", "-").replace("＞", "-").replace("〈", "").replace("〉", "-").replace("《", "").replace("》", "-").replace("≪", "").replace("≫", "-").replace("_", "-").replace("__", "-").replace("＿", "-").replace("＿＿", "-").replace("ー", "-").replace("ーー", "-").replace("一", "-").replace("一一", "-").replace("一", "-").replace("一一", "-").replace("--", "-").replace("=", "-").replace("＝", "-").replace("T", "-").replace("T", "-").replace("c", "0").replace("C", "0").replace("ｃ", "0").replace("Ｃ", "0").replace("d", "0").replace("D", "0").replace("ｄ", "0").replace("Ｄ", "0").replace("n", "0").replace("ｎ", "0").replace("o", "0").replace("O", "0").replace("ｏ", "0").replace("Ｏ", "0").replace("Ο", "0").replace("○", "0").replace("О", "0").replace("〇", "0").replace("u", "0").replace("U", "0").replace("ｕ", "0").replace("Ｕ", "0").replace("ц", "0").replace("∪", "0").replace("q", "9").replace("Q", "9").replace("ｑ", "0").replace("Ｑ", "0").replace("@", "0").replace("＠", "0").replace("i", "1").replace("I", "1").replace("ｉ", "1").replace("Ｉ", "1").replace("l", "1").replace("L", "1").replace("ｌ", "1").replace("Ｌ", "1").replace("!", "1").replace("！", "1").replace("「", "1").replace("」", "1").replace("|", "1").replace("｜", "1").replace("¦", "1").replace("¦", "1").replace("⋮", "1").replace("❘", "1").replace("Ι", "1").replace("Ⅰ", "1").replace("ⅱ", "11").replace("Ⅱ", "11").replace("ⅲ", "111").replace("Ⅲ", "111").replace("z", "2").replace("Z", "2").replace("ｚ", "2").replace("Ｚ", "2").replace("Ζ", "2").replace("b", "6").replace("ｂ", "6").replace("G", "6").replace("Ｇ", "6").replace("/", "7").replace("／", "7").replace("B", "8").replace("Ｂ", "8").replace("в", "8").replace("g", "9").replace("ｇ", "9").replace("q", "9").replace("ｑ", "9") for phone in rp_phone_numbers]
    # rp_phone_numbers = [phone.replace("ｃ", "0").replace("Ｃ", "0").replace("d", "0").replace("D", "0").replace("ｄ", "0").replace("Ｄ", "0").replace("n", "0").replace("ｎ", "0").replace("o", "0").replace("O", "0").replace("ｏ", "0").replace("Ｏ", "0").replace("Ο", "0").replace("○", "0").replace("О", "0").replace("〇", "0").replace("u", "0").replace("U", "0").replace("ｕ", "0").replace("Ｕ", "0").replace("ц", "0").replace("∪", "0").replace("q", "9").replace("Q", "9").replace("ｑ", "0").replace("Ｑ", "0").replace("@", "0").replace("＠", "0").replace("i", "1").replace("I", "1").replace("ｉ", "1").replace("Ｉ", "1").replace("l", "1").replace("L", "1").replace("ｌ", "1").replace("Ｌ", "1").replace("!", "1").replace("！", "1").replace("「", "1").replace("」", "1").replace("『", "1").replace("』", "1").replace("|", "1").replace("｜", "1").replace("¦", "1").replace("¦", "1").replace("⋮", "1").replace("❘", "1").replace("Ι", "1").replace("Ⅰ", "1").replace("ⅱ", "11").replace("Ⅱ", "11").replace("ⅲ", "111").replace("Ⅲ", "111").replace("z", "2").replace("Z", "2").replace("ｚ", "2").replace("Ｚ", "2").replace("Ζ", "2").replace("b", "6").replace("ｂ", "6").replace("G", "6").replace("Ｇ", "6").replace("/", "7").replace("／", "7").replace("B", "8").replace("Ｂ", "8").replace("в", "8").replace("g", "9").replace("ｇ", "9").replace("q", "9").replace("ｑ", "9") for phone in phone_numbers]
    # rp_phone_numbers = [phone.replace(".", "").replace("．", "").replace("。", "").replace(",", "").replace("，", "").replace("、", "").replace("・", "").replace(":", "").replace("：", "").replace(";", "").replace("；", "").replace(" ", "").replace("　", "").replace("\t", "").replace("\n", "").replace("(", "").replace("（", "").replace("[", "").replace("［", "").replace("〔", "").replace("{", "").replace("｛", "").replace("<", "").replace("＜", "").replace("〈", "").replace("〉", "-").replace("《", "").replace("≪", "") for phone in rp_phone_numbers]
    # rp_phone_numbers = [phone.replace("T", "-").replace("Ｔ", "-").replace(")", "-").replace("）", "-").replace("]", "-").replace("］", "-").replace("〕", "-").replace("}", "-").replace(">", "-").replace("＞", "-").replace("｝", "-").replace("》", "-").replace("≫", "-").replace("_", "-").replace("__", "-").replace("___", "-").replace("=", "-").replace("==", "-").replace("===", "-").replace("＝", "-").replace("＝＝", "-").replace("＿", "-").replace("＿＿", "-").replace("ー", "-").replace("ーー", "-").replace("一", "-").replace("一一", "-").replace("一", "-").replace("一一", "-").replace("--", "-") for phone in rp_phone_numbers]
    # rp_phone_numbers = [phone.replace("ｃ", "0").replace("Ｃ", "0").replace("d", "0").replace("D", "0").replace("ｄ", "0").replace("Ｄ", "0").replace("n", "0").replace("ｎ", "0").replace("o", "0").replace("O", "0").replace("ｏ", "0").replace("Ｏ", "0").replace("Ο", "0").replace("○", "0").replace("О", "0").replace("〇", "0").replace("u", "0").replace("U", "0").replace("ｕ", "0").replace("Ｕ", "0").replace("ц", "0").replace("∪", "0").replace("q", "9").replace("Q", "9").replace("ｑ", "0").replace("Ｑ", "0").replace("@", "0").replace("＠", "0").replace("i", "1").replace("I", "1").replace("ｉ", "1").replace("Ｉ", "1").replace("l", "1").replace("L", "1").replace("ｌ", "1").replace("Ｌ", "1").replace("!", "1").replace("！", "1").replace("「", "1").replace("」", "1").replace("『", "1").replace("』", "1").replace("|", "1").replace("｜", "1").replace("¦", "1").replace("¦", "1").replace("⋮", "1").replace("❘", "1").replace("Ι", "1").replace("Ⅰ", "1").replace("ⅱ", "11").replace("Ⅱ", "11").replace("ⅲ", "111").replace("Ⅲ", "111").replace("z", "2").replace("Z", "2").replace("ｚ", "2").replace("Ｚ", "2").replace("Ζ", "2").replace("b", "6").replace("ｂ", "6").replace("G", "6").replace("Ｇ", "6").replace("/", "7").replace("／", "7").replace("B", "8").replace("Ｂ", "8").replace("в", "8").replace("g", "9").replace("ｇ", "9").replace("q", "9").replace("ｑ", "9") for phone in rp_phone_numbers]
    # rp_phone_numbers = [phone.replace(".", "").replace("．", "").replace("。", "").replace(",", "").replace("，", "").replace("、", "").replace("・", "").replace(":", "").replace("：", "").replace(";", "").replace("；", "").replace(" ", "").replace("　", "").replace("\t", "").replace("\n", "").replace("(", "").replace("（", "").replace("[", "").replace("［", "").replace("〔", "").replace("{", "").replace("｛", "").replace("<", "").replace("＜", "").replace("〈", "").replace("〉", "-").replace("《", "").replace("≪", "") for phone in rp_phone_numbers]
    # rp_phone_numbers = [phone.replace("T", "-").replace("Ｔ", "-").replace(")", "-").replace("）", "-").replace("]", "-").replace("］", "-").replace("〕", "-").replace("}", "-").replace(">", "-").replace("＞", "-").replace("｝", "-").replace("》", "-").replace("≫", "-").replace("_", "-").replace("__", "-").replace("___", "-").replace("=", "-").replace("==", "-").replace("===", "-").replace("＝", "-").replace("＝＝", "-").replace("＿", "-").replace("＿＿", "-").replace("ー", "-").replace("ーー", "-").replace("一", "-").replace("一一", "-").replace("一", "-").replace("一一", "-").replace("--", "-") for phone in rp_phone_numbers]

    # 10桁以上および10桁以下の数字を含む文字列、00から始まる文字列、アルファベットを含む文字列を除外
    found_phone_numbers = [phone for phone in rp_phone_numbers if 10 <= len(re.sub(r'[-ー一_＿ ()（） 　\s\t]', '', phone)) <= 10 and not phone.startswith("00") and not any(char.isalpha() for char in phone) ]

    return found_phone_numbers


def ocr_proc(file_name, src_dir = 'content/src_dir/', dst_dir = 'content/dst_dir/'):
    # 処理時間計測開始
    ocr_proc_start = time.perf_counter()
    # メディア情報準備
    # src_dir = 'content/src_dir/'    # 入力用
    # dst_dir = 'content/dst_dir/'    # 出力用
    # file_name = '郵送-通信費-532-37.JPG' # 入出力ファイル名

    # メディアファイル読込準備
    img_file = Image.open(dst_dir + file_name)

    # OCR処理準備
    pyocr.tesseract.TESSERACT_CMD = r'C:/Users/j/AppData/Local/Programs/Tesseract-OCR/tesseract.exe'
    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        print('OCRアプリ検知エラー')
        os.sys.exit(1)
    tool = tools[0]

    # OCR情報
    # print("*****" * 15, '\n[OCR種別]: ', tool.get_name())    # For Check
    # print('[OCRモジュール設定情報]: ', tools)    # For Check
    print("*****" * 15)

    # RGBモードに画像変換
    # img_file = file_img.convert('RGB')    # ※　文字列検知品質改善用(影響なし)

    # 文字列の検知・抽出・認識
    ocr_txt = tool.image_to_string(
        img_file,
        lang='jpn',     # 日本語学習済みモデル ※　文字列検知品質改善用(改善)
        # lang='jpn+eng',      # 日本・英語学習済みモデル ※　文字列検知品質改善用(日本語レシート用としては逆効果)
        builder=pyocr.builders.TextBuilder(tesseract_layout=6)
    )
    
    # 電話番号文字列抽出
    tel_list = extract_pnumbers_proc(ocr_txt)
    
    # テキストファイル出力準備
    # txt_file = open(dst_dir + file_name + '.txt', 'w', encoding='UTF-8')
    txt_file = open(dst_dir + 'result.txt', 'a', encoding='UTF-8')

    # 認識文字列のコンソール表示＆テキストファイル出力 
    if (tel_list):
        print(f'{"*****" * 15}\n{file_name}\n{"*****" * 15}\n{"  ".join(tel_list)}\n{"*****" * 15}\n{ocr_txt}\n{"*****" * 15}')
        txt_file.write(f'{"*****" * 15}\n{file_name}\n{"*****" * 15}\n{"  ".join(tel_list)}\n{"*****" * 15}\n{ocr_txt}\n{"*****" * 15}\n')
    else:
        print(f'{"*****" * 15}\n{file_name}\n{"*****" * 15}\n{ocr_txt}\n{"*****" * 15}')
        txt_file.write(f'{"*****" * 15}\n{file_name}\n{"*****" * 15}\n{ocr_txt}\n{"*****" * 15}\n')

    # 文字列の検知・位置情報取得
    results = tool.image_to_string(
        img_file,
        lang='jpn',     # 日本語学習済みモデル ※　文字列検知品質改善用(改善)
        # lang='jpn+eng',      # 日本・英語学習済みモデル ※　文字列検知品質改善用(日本語レシート用としては逆効果)
        builder=pyocr.builders.WordBoxBuilder(tesseract_layout=6)
    )
    # 認識文字位置の表示
    # print(results, '\n', "*****" * 15)    # For Check

    # 矩形描画準備
    # draw_rectangle = cv2.imread(dst_dir + file_name)
    # for box in results:
    #     cv2.rectangle(draw_rectangle, box.position[0], box.position[1], (255, 0, 0), 3, cv2.LINE_4)
    # cv2.imwrite(dst_dir + file_name, draw_rectangle)
    # draw_rectangle = Image.open(dst_dir + file_name)
    # draw_rectangle.show()

    # 矩形描画準備
    draw = ImageDraw(img_file)

    # 矩形描画の開始・終了位置座標配列
    for box in results:
        # print(box.position)    # For Check
        draw.rectangle(     # 矩形描画
            [(box.position[0][0] - 7, box.position[0][1] - 7),  # 矩形の色(RGB)
            (box.position[1][0] + 7, box.position[1][1] + 7)],  # 矩形の色(RGB)
            outline = (0, 255, 255),  # 矩形の色(RGB)
            width = 5 # 線の太さ
        )

    # 画像表示
    img_file.show()
    # display(img_file) # .google.colab用：display(pil_image)
    # ファイル保存
    img_file.save(dst_dir + file_name)
    # ファイル処理終了
    img_file.close()

    show_proc_time(file_name, time.perf_counter() - ocr_proc_start)

main()
# 改善参考情報
# https://majisemi.com/topics/tool/2505/