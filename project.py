from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QSlider
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QLineEdit, QLabel, QInputDialog, QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5 import uic
from PIL import Image, ImageDraw
from random import randint as rad
from math import sqrt
import sys


def gcd(a, b):
    while b:
        a %= b
        a, b, = b, a
    return a


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('project.ui', self)
        self.lastContrast = 1
        self.lastBright = 1
        self.lastSize = 1
        self.size_x = 1
        self.size_y = 1

        self.nameStartImage = None
        self.startImage = None
        self.timeImage = self.startImage
        self.cur_pixmap = None
        self.cur_image = None
        self.selectImage.clicked.connect(self.openImage)
        self.generate.clicked.connect(self.generateDef)
        self.generate_mirror.clicked.connect(self.generateMirrorDef)
        self.gener_anagliph.clicked.connect(self.generateAnagliph)
        self.anagliph_slider.valueChanged.connect(self.displayAnagliph)
        self.contrast_slider.setValue(100)
        self.contrast_slider.valueChanged.connect(self.displayContrast)
        self.gener_contr.clicked.connect(self.changeContrast)
        self.bright_slider.setValue(100)
        self.bright_slider.valueChanged.connect(self.displayBright)
        self.gener_bright.clicked.connect(self.changeBright)
        self.size_slider.valueChanged.connect(self.displaySize)
        self.saveButton.clicked.connect(self.SaveImage)

    def displaySize(self):
        k = self.size_slider.value()
        self.lcd_size.display(k / 100)

    def displayAnagliph(self):
        k = self.anagliph_slider.value()
        self.lcd_anagliph.display(k)

    def generateAnagliph(self):
        k = self.anagliph_slider.value()
        self.displayAnagliph()
        self.timeImage = self.makeAnagliph(self.timeImage, k)
        self.showImage()

    def generateMirrorDef(self):
        self.vertical.setChecked(False)
        self.horizontal.setChecked(False)
        if self.vertical.isChecked():
            self.timeImage = self.mirrorVertical(self.timeImage)
        elif self.horizontal.isChecked():
            self.timeImage = self.mirrorHorizontal(self.timeImage)
        self.showImage()

    def generateDef(self):
        self.negative.setChecked(False)
        self.blackwhite.setChecked(False)
        self.sepia.setChecked(False)
        if self.negative.isChecked():
            self.timeImage = self.makeNeg(self.timeImage)
        elif self.blackwhite.isChecked():
            self.timeImage = self.makeBW(self.timeImage)
        elif self.sepia.isChecked():
            self.timeImage = self.makeSep(self.timeImage)
        self.showImage()

    def resizeImageM(self, k, im):  # только для k <= 1
        pixels = im.load()
        x, y = im.size
        tx = int(x * k)
        ty = int(y * k)
        # tx, ty - размер получаемого изображеия
        imn = Image.new("RGB", (tx, ty), (0, 0, 0))
        pixelsn = imn.load()
        for i in range(tx):
            for j in range(ty):
                s_r = s_g = s_b = cnt = 0
                for qx in range(x // tx):
                    for qy in range(y // ty):
                        px, py = x * i // tx, y * j // ty
                        r, g, b = pixels[px, py]
                        s_r += r
                        s_g += g
                        s_b += b
                        cnt += 1
                # подсчет среднего в блоке
                pixelsn[i, j] = (s_r // cnt), \
                                (s_g // cnt), \
                                (s_b // cnt)
                # Создание картинки
        return imn

    def resizeImage(self, k, im):  # для всех k
        if k > 1:
            k1 = 0
            if type(k) == float:
                k = int(k * 100) / 100
                for i in range(2, int(sqrt(k * 100) + 2)):
                    if k * 100 % i == 0:
                        break
                k1 = int(k * 100 / i) / 100
                k = int(i)
                g = gcd(k, k1)
                if g > 1:
                    k /= g
                    k = int(k)
                    k1 /= g
            # выполяется алгоритм для целых k затем для k1 <= 1,
            # таких что k * k1 == начальному k
            pixels = im.load()
            x, y = im.size
            tx = int(x * k)
            ty = int(y * k)
            # tx, ty - размер получаемого изображеия
            imn = Image.new("RGB", (tx, ty), (0, 0, 0))
            pixelsn = imn.load()
            for i in range(x):
                for j in range(y):
                    for px in range(k):
                        for py in range(k):
                            pixelsn[(i * k) + px, (j * k) + py] = pixels[i, j]
            if k1 != 0:
                return self.resizeImageM(k1, imn)
            else:
                return imn
        else:
            return self.resizeImageM(k, im)

    def displayContrast(self):
        k = self.contrast_slider.value()
        self.lcd_contr.display(k / 100)

    def changeContrast(self):
        k = self.contrast_slider.value()
        self.timeImage = self.contrast(self.timeImage, (k / 100) / self.lastContrast)
        self.lastContrast = k / 100
        self.showImage()

    def displayBright(self):
        k = self.bright_slider.value()
        self.lcd_bright.display(k / 100)

    def changeBright(self):
        k = self.bright_slider.value()
        self.timeImage = self.bright(self.timeImage, (k / 100) / self.lastBright)
        self.lastBright = k / 100
        self.showImage()

    def mirrorVertical(self, im):
        x, y = im.size
        pixels = im.load()
        red, gre, blu = 0, 0, 0
        for i in range(x // 2):
            for j in range(y):
                pixels[x - i - 1, j], pixels[i, j] = pixels[i, j], pixels[x - i - 1, j]
        return im

    def mirrorHorizontal(self, im):
        x, y = im.size
        pixels = im.load()
        red, gre, blu = 0, 0, 0
        for i in range(y // 2):
            for j in range(x):
                pixels[j, y - i - 1], pixels[j, i] = pixels[j, i], pixels[j, y - i - 1]
        return im

    def makeBW(self, im):
        pixels = im.load()
        x, y = im.size
        for i in range(x):
            for j in range(y):
                r, g, b = pixels[i, j]
                r = g = b = round((r + g + b) / 3)
                pixels[i, j] = (r, g, b)
        return im

    def makeSep(self, im):
        pixels = im.load()
        x, y = im.size
        for i in range(x):
            for j in range(y):
                r, g, b = pixels[i, j]
                r1 = int(r * 0.393 + g * 0.769 + b * 0.189)
                g1 = int(r * 0.349 + g * 0.686 + b * 0.168)
                b1 = int(r * 0.272 + g * 0.534 + b * 0.131)
                pixels[i, j] = (r1, g1, b1)
        return im

    def makeNeg(self, im):
        pixels = im.load()
        x, y = im.size
        for i in range(x):
            for j in range(y):
                r, g, b = pixels[i, j]
                pixels[i, j] = (255 - r, 255 - g, 255 - b)
        return im

    def makeAnagliph(self, im, delta):
        pixels = im.load()
        x, y = im.size
        imn = Image.new("RGB", (x, y), (255, 255, 255))
        pixelsn = imn.load()
        for n in range(delta):
            for i in range(n, x, delta):
                for j in range(y):
                    r, g, b = pixels[i, j]
                    if 0 <= i + delta < x:
                        rn, gn, bn = pixels[i + delta, j]
                        pixelsn[i + delta, j] = r, gn, bn
                    r, g, b = pixels[n, j]
                    pixelsn[n, j] = 0, g, b
        return imn

    def contrast(self, im, k):
        pixels = im.load()
        x, y = im.size
        sr = 0
        for i in range(x):
            for j in range(y):
                r, g, b = pixels[i, j]
                sr += r * 0.299 + g * 0.587 + b * 0.114
        sr /= x * y
        new_val = [min(255, max(0, int(sr + k * (i - sr)))) for i in range(256)]
        for i in range(x):
            for j in range(y):
                r, g, b = pixels[i, j]
                pixels[i, j] = (new_val[r], new_val[g], new_val[b])
        return im

    def bright(self, im, k):
        pixels = im.load()
        x, y = im.size
        for i in range(x):
            for j in range(y):
                r, g, b = pixels[i, j]
                r = min(255, max(0, int(r * k)))
                g = min(255, max(0, int(g * k)))
                b = min(255, max(0, int(b * k)))
                pixels[i, j] = (r, g, b)
        return im

    def showImage(self):
        x, y = self.timeImage.size
        new_im = self.resizeImage(850 / x, self.timeImage)
        new_im.save("newim.jpg")
        x, y = new_im.size
        self.timeImage = new_im
        self.cur_pixmap = QPixmap('newim.jpg')
        self.cur_image = QLabel(self)
        self.cur_image.move(80, 100)
        self.cur_image.resize(x, y)
        self.cur_image.setPixmap(self.cur_pixmap)
        self.cur_image.show()

    def openImage(self):
        name_ = QFileDialog.getOpenFileName(self, 'Выбрать картинку',
                                                          '', "Картинка(*.jpg)")[0]
        if len(name_) > 0:
            self.contrast_slider.setValue(100)
            self.bright_slider.setValue(100)
            self.size_slider.setValue(100)
            self.anagliph_slider.setValue(0)
            self.vertical.setChecked(False)
            self.horizontal.setChecked(False)
            self.negative.setChecked(False)
            self.blackwhite.setChecked(False)
            self.sepia.setChecked(False)
            self.nameStartImage = name_
            self.startImage = Image.open(self.nameStartImage)
            self.timeImage = self.startImage
            self.size_x, self.size_y = self.timeImage.size
            self.showImage()

    def SaveImage(self):
        file = QFileDialog.getSaveFileName(self, "Select Directory", '', "Картинка(*.jpg)")[0]
        if len(file) > 0:
            x, y = self.timeImage
            k = self.size_slider.value() / 100
            x *= k
            self.timeImage = self.resizeImage(self.size_x / x, self.timeImage)
            self.timeImage.save(file)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())

