import math
import sys

import sympy
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QApplication, QWidget, QFileDialog, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, \
    QLineEdit, QLabel


# Расширенный алгоритм Евклида для генерации приватного ключа: позволяет найти такие x и y, что ax + by = НОД(a, b)
def gcd_extended(num1, num2):
    if num1 == 0:
        return num2, 0, 1
    else:
        div, x, y = gcd_extended(num2 % num1, num1)
    return div, y - (num2 // num1) * x, x


# Генерация ключей
def generate_keys(digits):
    # Число знаков в простых числах
    aux_digits = digits / 2
    # Границы генерации простых чисел
    lower_bound = 10 ** (aux_digits - 1)
    higher_bound = (10 ** aux_digits) - 1
    # Генерируем простые числа до того момента, пока их произведение не будет длиной 28 цифр
    p = sympy.randprime(lower_bound, higher_bound)
    q = sympy.randprime(lower_bound, higher_bound)
    n = p * q

    while int(math.log10(n)) + 1 != digits:
        p = sympy.randprime(lower_bound, higher_bound)
        q = sympy.randprime(lower_bound, higher_bound)
        n = p * q
    # Значение функции Эйлера для полупростого модуля n
    phi = (p - 1) * (q - 1)
    # Ищем взаимно простое со значением функции Эйлера число, которое будет публичным ключом
    e = 3
    while e < phi:
        if math.gcd(e, phi) == 1:
            break
        else:
            e += 1
    # Генерация приватного ключа; приватный ключ - обратный к публичному в поле вычетов по модулю phi
    d = gcd_extended(e, phi)[1]
    # Берем публичный ключ по модулю phi, т.к. результатом работы алгоритма Евклида может быть отрицательное число
    d = d % phi
    return p, q, phi, e, d, n


def encode_number(msg, e, n):
    # Шифрование: зашифрованное = (сообщение ^ публичный ключ) mod модуль
    return pow(msg, e, n)


def decode_number(msg, d, n):
    # Дешифрование: исходное = (зашифрованное ^ приватный ключ) mod модуль
    return pow(msg, d, n)


# Графика
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Members
        self.f = str
        self.f_enc = str
        self.f_dec = str

        self.n = int
        self.p = int
        self.q = int
        self.phi = int
        self.e = int
        self.d = int

        # Layout settings
        self.setWindowTitle("RSA")

        self.button_generatekeys = QPushButton("Generate RSA keys")
        self.button_setkeys = QPushButton("Set RSA keys")
        self.button_savekeys = QPushButton("Save RSA keys as a file")
        self.button_loadkeys = QPushButton("Load RSA keys from a file")
        self.button_opentext = QPushButton("Open text file")
        self.button_encrypt = QPushButton("Encrypt file")
        self.button_decrypt = QPushButton("Decrypt file")

        self.button_encrypt.setEnabled(False)
        self.button_decrypt.setEnabled(False)

        layout = QVBoxLayout(self)

        keys_layout = QHBoxLayout(self)

        self.n_label = QLabel("n: ")
        self.n_lineedit = QLineEdit()
        self.e_label = QLabel("e: ")
        self.e_lineedit = QLineEdit()
        self.d_label = QLabel("d: ")
        self.d_lineedit = QLineEdit()

        keys_layout.addWidget(self.n_label)
        keys_layout.addWidget(self.n_lineedit)
        keys_layout.addWidget(self.e_label)
        keys_layout.addWidget(self.e_lineedit)
        keys_layout.addWidget(self.d_label)
        keys_layout.addWidget(self.d_lineedit)

        ck_widget = QWidget(self)
        ck_widget.setLayout(keys_layout)

        layout.addWidget(ck_widget)
        layout.addWidget(self.button_generatekeys)
        layout.addWidget(self.button_setkeys)
        layout.addWidget(self.button_savekeys)
        layout.addWidget(self.button_loadkeys)
        layout.addWidget(self.button_opentext)
        layout.addWidget(self.button_encrypt)
        layout.addWidget(self.button_decrypt)

        c_widget = QWidget(self)
        c_widget.setLayout(layout)
        self.setCentralWidget(c_widget)

        self.button_opentext.clicked.connect(self.openFileSlot)
        self.button_generatekeys.clicked.connect(self.genKeysSlot)
        self.button_setkeys.clicked.connect(self.setKeysSlot)
        self.button_savekeys.clicked.connect(self.saveKeysSlot)
        self.button_loadkeys.clicked.connect(self.loadKeysSlot)
        self.button_encrypt.clicked.connect(self.e_file)
        self.button_decrypt.clicked.connect(self.d_file)

        self.setFixedSize(QSize(800, 300))

    def updateKeys(self):
        self.n_lineedit.setText(str(self.n))
        self.e_lineedit.setText(str(self.e))
        self.d_lineedit.setText(str(self.d))

    def openFileSlot(self):
        # noinspection PyTypeChecker
        self.f = QFileDialog.getOpenFileName(self, 'Open file', None, "Text files (*.txt)")[0]
        self.f_enc = self.f[0:-4] + "_enc.txt"
        self.f_dec = self.f[0:-4] + "_dec.txt"
        self.button_encrypt.setEnabled(True)
        self.button_decrypt.setEnabled(True)
        self.setWindowTitle(self.windowTitle() + ": " + self.f)

    def genKeysSlot(self):
        # Генерация ключей с длиной модуля = 28
        self.p, self.q, self.phi, self.e, self.d, self.n = generate_keys(28)
        self.updateKeys()

    def setKeysSlot(self):
        self.updateKeys()

    def saveKeysSlot(self):
        public = open("./.public.rsa", 'wb')
        private = open("./.private.rsa", 'wb')
        public.write(bytearray(str(self.n) + "\n" + str(self.e), "ascii"))
        private.write(bytearray(str(self.n) + "\n" + str(self.d), "ascii"))
        public.close()
        private.close()

    def loadKeysSlot(self):
        public = open("./.public.rsa", 'rb')
        private = open("./.private.rsa", 'rb')
        self.n = int(public.readline())
        self.e = int(public.readline())
        self.n = int(private.readline())
        self.d = int(private.readline())
        self.updateKeys()
        public.close()
        private.close()

    # noinspection PyTypeChecker
    def e_d_file(self, way):
        if way == 1:
            # Берем численное значение каждого символа из файла и применяем к нему функцию зашифровки, получившиеся
            # числа записываем через пробел
            write_e_file = open(self.f_enc, 'wt')
            toEncFile = open(self.f, 'rt')
            for token in toEncFile.read():
                write_e_file.write(str(encode_number(ord(token), self.e, self.n)) + " ")
            write_e_file.close()
            toEncFile.close()
        else:
            # Парсим файл по пробелам, получившиеся токены кастуем в инт и дешифруем, записываем в файл символы из
            # таблицы ASCII с соответсвующими номерами
            write_d_file = open(self.f_dec, 'wt')
            toDecFile = open(self.f, 'rt')
            # Пустые токены нужно удалить
            parsed = filter(None, toDecFile.read().split(" "))
            for token in parsed:
                inttoken = int(token, 10)
                dec = decode_number(inttoken, self.d, self.n)
                write_d_file.write(chr(dec))
            write_d_file.close()
            toDecFile.close()

    def e_file(self):
        self.e_d_file(1)

    def d_file(self):
        self.e_d_file(0)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


# Нужно для корректной работы кода как и отдельной программой, так и модулем. Если имя файла main.py - запустить
# функцию main()
if __name__ == '__main__':
    main()
