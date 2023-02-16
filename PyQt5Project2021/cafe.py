import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QVBoxLayout, QListWidget
from PyQt5.QtWidgets import QDialogButtonBox, QPushButton, QLabel, QInputDialog
import pymorphy2
from PyQt5.QtGui import QPixmap, QFont
import sqlite3
import shutil

# Когда я начинал писать проект, только я и Бог понимали, что я делаю. Теперь только Бог...
morph = pymorphy2.MorphAnalyzer()
COFFEE = {'Капучино': 3.00, 'Американо': 3.00, 'Латте': 3.00,
          'Эспрессо': 3.00, 'Макиато': 3.00}

TEA = {'Dragon Well Tea': 5.15, 'Iron Goddes': 5.00, 'Junshan Silver Needle': 5.00,
       'Keemun Black Tea': 5.25, 'White Hair of Pekoe Silver Needle': 6.00}

DESSERTS = {'Черничные маффины': 4.00, 'Чизкейк': 5.00, 'Булочки с малиной и корицей': 5.00,
            'Пончик с ванильной глазурью': 4.00, 'Тёмный шоколад ручной работы': 6.00}

SYRUPS = {'Без сиропа': 0.00, 'Миндальный сироп': 0.50, 'Лимонный сироп': 0.50,
          'Шоколадный сироп': 0.50, 'Карамельный сироп': 0.50, 'Ванильный сироп': 0.50}


class MyDialog(QDialog):
    def __init__(self, title, warn, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)

        btn = QDialogButtonBox.Ok

        self.buttonBox = QDialogButtonBox(btn)
        self.buttonBox.accepted.connect(self.accept)

        self.layout = QVBoxLayout()
        message = QLabel(warn)
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class ListForCoder(QDialog):
    def __init__(self, warn, file_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle('SECRET INFORMATION')

        btn = QDialogButtonBox.Ok

        self.buttonBox = QDialogButtonBox(btn)
        self.buttonBox.accepted.connect(self.accept)
        INP2 = open(file_name, mode='r', encoding='utf-8')
        self.layout = QVBoxLayout()
        s = float(INP2.readline().rstrip()) // 0.01 // 100
        inf_list = QLabel(warn + str(s))
        inf_list.setFont(QFont("Courier", 20))
        self.layout.addWidget(inf_list)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class Cafe(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('cafe.ui', self)
        self.order_coffee = []
        self.order_tea = dict()
        self.tea_in_order = {'Dragon Well Tea': '', 'Iron Goddes': '',
                             'Junshan Silver Needle': '',
                             'Keemun Black Tea': '',
                             'White Hair of Pekoe Silver Needle': ''}
        self.tea_dict = {'Dragon Well Tea': self.spinBox, 'Iron Goddes': self.spinBox_2,
                         'Junshan Silver Needle': self.spinBox_3,
                         'Keemun Black Tea': self.spinBox_4,
                         'White Hair of Pekoe Silver Needle': self.spinBox_5}
        self.tea_dict2 = {'Dragon Well Tea': self.label_19, 'Iron Goddes': self.label_20,
                          'Junshan Silver Needle': self.label_21,
                          'Keemun Black Tea': self.label_22,
                          'White Hair of Pekoe Silver Needle': self.label_24}
        self.coder_password = 'YanD3x21'
        self.dessert_dict = {'Черничные маффины': self.spinBox_6, 'Чизкейк': self.spinBox_7,
                             'Булочки с малиной и корицей': self.spinBox_8,
                             'Пончик с ванильной глазурью': self.spinBox_9,
                             'Тёмный шоколад ручной работы': self.spinBox_10}
        self.dessert_dict2 = {'Черничные маффины': self.label_27, 'Чизкейк': self.label_28,
                              'Булочки с малиной и корицей': self.label_29,
                              'Пончик с ванильной глазурью': self.label_30,
                              'Тёмный шоколад ручной работы': self.label_31}
        self.dessert_in_order = {'Черничные маффины': '', 'Чизкейк': '',
                                 'Булочки с малиной и корицей': '',
                                 'Пончик с ванильной глазурью': '',
                                 'Тёмный шоколад ручной работы': ''}
        self.order_dessert = dict()
        self.price = 0
        self.initUI()
        self.full_order = []

    def initUI(self):
        self.featureButton.clicked.connect(self.feature)
        self.featureButton.setStyleSheet("background-color: green")
        self.pushButton_5.clicked.connect(self.clear_order)
        for el in self.coffeeGroup.buttons():
            el.clicked.connect(self.default_syrup)
        for elem in self.syrupGroup.buttons():
            elem.toggled.connect(self.no_syrup)
            elem.clicked.connect(self.change_syrup)
        self.pushButton.clicked.connect(self.add_coffee)
        for tea in self.teaGroup.buttons():
            tea.clicked.connect(self.default_tea_amount)
        self.pushButton_2.clicked.connect(self.add_tea)
        self.spinBox.valueChanged.connect(self.tea_amount_changed)
        self.spinBox_2.valueChanged.connect(self.tea_amount_changed)
        self.spinBox_3.valueChanged.connect(self.tea_amount_changed)
        self.spinBox_4.valueChanged.connect(self.tea_amount_changed)
        self.spinBox_5.valueChanged.connect(self.tea_amount_changed)
        for dessert in self.dessertsGroup.buttons():
            dessert.clicked.connect(self.default_dessert_amount)
        self.spinBox_6.valueChanged.connect(self.dessert_amount_changed)
        self.spinBox_7.valueChanged.connect(self.dessert_amount_changed)
        self.spinBox_8.valueChanged.connect(self.dessert_amount_changed)
        self.spinBox_9.valueChanged.connect(self.dessert_amount_changed)
        self.spinBox_10.valueChanged.connect(self.dessert_amount_changed)
        self.pushButton_3.clicked.connect(self.add_dessert)
        self.pushButton_6.clicked.connect(self.delete_last_position)
        self.pushButton_4.clicked.connect(self.pay_and_add_order)
        self.pixmap = QPixmap('coffee_image.jpeg')
        self.pictureLabel.setPixmap(self.pixmap)
        self.coderButton.setStyleSheet("background-color: red")
        self.coderButton.clicked.connect(self.coder_info)

    def feature(self):
        my_dialog = MyDialog('Не баг, а фича', 'Каждый седьмой заказ имеет скидку 7%', self)
        my_dialog.exec_()

    def coder_info(self):
        con = sqlite3.connect('cafe_new.sqlite')
        cur = con.cursor()
        res = cur.execute("""SELECT price FROM orders""").fetchall()
        sm = 0
        for el in res:
            sm += el[0]
        INP = open('clients.txt', mode='w', encoding='utf-8')
        INP.write(str(sm))
        INP.close()
        shutil.copyfile('clients.txt', 'clients2.txt')
        password, ok_pressed = QInputDialog.getText(self, "Введите пароль",
                                                    "Тут сложная защита, юный программист!")
        if password == self.coder_password:
            my_dialog = ListForCoder('Вся прибыль на данный момент: {}'.format(sm), 'clients2.txt', self)
            my_dialog.exec_()

    def pay_and_add_order(self):
        if self.price > 0:
            num, ok_pressed = QInputDialog.getDouble(self, "Введите сумму (USD)",
                                                     "К оплате:")
            while num < self.price:
                num, ok_pressed = QInputDialog.getDouble(self, "Введите сумму (USD)",
                                                         "К оплате:")
            my_dialog = MyDialog('Спасибо за покупку!', 'Ваша сдача: {}'.format(num - self.price), self)
            my_dialog.exec_()
            order = []
            for coffee_ordered in self.order_coffee:
                order.append(coffee_ordered)
            for tea in self.tea_in_order.values():
                if tea != '':
                    order.append(tea)
            for value in self.dessert_in_order.values():
                if value != '':
                    order.append(value)
            order = ', '.join(order)
            con = sqlite3.connect('cafe_new.sqlite')
            cur = con.cursor()
            command = """INSERT INTO orders(meals,price) VALUES('{}',{})""".format(order, self.price)
            cur.execute(command)
            con.commit()
            cur.close()
            con = sqlite3.connect('cafe_new.sqlite')
            cur = con.cursor()
            command = """UPDATE orders
             SET price = price * 0.93
             WHERE id % 7 = 0"""
            cur.execute(command)
            con.commit()
            cur.close()
            self.clear_order()
        else:
            my_dialog = MyDialog('Ошибка!', 'Создайте заказ, а потом оплатите его', self)
            my_dialog.exec_()

    def default_syrup(self):
        self.checkBox.setChecked(True)
        for elem in self.syrupGroup.buttons()[1:]:
            elem.setChecked(False)

    def change_syrup(self):
        if self.sender().text() == 'Без сиропа':
            for elem in self.syrupGroup.buttons()[1:]:
                elem.setChecked(False)
        else:
            self.checkBox.setChecked(False)

    def no_syrup(self):
        x = True
        for el in self.syrupGroup.buttons():
            if el.isChecked():
                x = False
        if x:
            self.checkBox.setChecked(True)

    def clear_order(self):
        self.listWidget.clear()
        self.priceLabel.setText('')
        self.price = 0
        self.order_coffee = []
        self.order_tea = dict()
        self.tea_in_order = {'Dragon Well Tea': '', 'Iron Goddes': '',
                             'Junshan Silver Needle': '',
                             'Keemun Black Tea': '',
                             'White Hair of Pekoe Silver Needle': ''}
        self.dessert_in_order = {'Черничные маффины': '', 'Чизкейк': '',
                                 'Булочки с малиной и корицей': '',
                                 'Пончик с ванильной глазурью': '',
                                 'Тёмный шоколад ручной работы': ''}
        self.order_dessert = dict()
        for tea in self.teaGroup.buttons():
            tea.setChecked(False)
        for dessert in self.dessertsGroup.buttons():
            dessert.setChecked(False)
        for coffee in self.coffeeGroup.buttons():
            coffee.setDown(True)
        for syrup in self.syrupGroup.buttons():
            syrup.setChecked(False)
        for value in self.tea_dict.values():
            value.setValue(0)
        for value in self.dessert_dict.values():
            value.setValue(0)

    def delete_last_position(self):
        if len(self.full_order) > 0:
            deleted_item = self.full_order[-1]
            x = True
            for el in TEA.keys():
                if deleted_item in el:
                    x = False
                    self.price -= float(self.tea_in_order[el][self.tea_in_order[el].rfind(' '):])
                    self.priceLabel.setText(str(self.price))
                    self.tea_in_order[el] = ''
                    self.listWidget.clear()
                    del self.order_tea[el]
                    del self.full_order[-1]
                    for coffee_ordered in self.order_coffee:
                        self.listWidget.addItem(coffee_ordered)
                    for value in self.tea_in_order.values():
                        if value != '':
                            self.listWidget.addItem(value)
                    for dessert in self.dessert_in_order.values():
                        if dessert != '':
                            self.listWidget.addItem(dessert)
                    break
            if x:
                for el in DESSERTS.keys():
                    if deleted_item in el:
                        x = False
                        self.price -= float(self.dessert_in_order[el][self.dessert_in_order[el].rfind(' '):])
                        self.priceLabel.setText(str(self.price))
                        self.dessert_in_order[el] = ''
                        self.listWidget.clear()
                        del self.order_dessert[el]
                        del self.full_order[-1]
                        for coffee_ordered in self.order_coffee:
                            self.listWidget.addItem(coffee_ordered)
                        for value in self.tea_in_order.values():
                            if value != '':
                                self.listWidget.addItem(value)
                        for dessert in self.dessert_in_order.values():
                            if dessert != '':
                                self.listWidget.addItem(dessert)
                        break
            if x:
                for i in range(len(self.order_coffee)):
                    if self.order_coffee[i] == deleted_item:
                        self.price -= float(deleted_item[deleted_item.rfind(' '):])
                        self.priceLabel.setText(str(self.price))
                        del self.order_coffee[i]
                        del self.full_order[-1]
                        self.listWidget.clear()
                        for coffee_ordered in self.order_coffee:
                            self.listWidget.addItem(coffee_ordered)
                        for value in self.tea_in_order.values():
                            if value != '':
                                self.listWidget.addItem(value)
                        for dessert in self.dessert_in_order.values():
                            if dessert != '':
                                self.listWidget.addItem(dessert)

    def add_coffee(self):
        try:
            st = ''
            n_syrups = 0
            coffee_cost = 0
            for elem in self.coffeeGroup.buttons():
                if elem.isChecked():
                    coffee_name = elem.text()
                    break
            coffee_cost += COFFEE[coffee_name]
            for el in self.syrupGroup.buttons():
                if el.isChecked():
                    n_syrups += 1
            st += coffee_name
            if n_syrups > 1:
                coffee_cost += (n_syrups - 1) * 0.50
            if n_syrups > 1:
                st += ' с'
                syrups = []
                for el in self.syrupGroup.buttons()[1:]:
                    if el.isChecked():
                        text_syr1 = morph.parse(el.text().split()[0])[0]
                        syrups.append(text_syr1.inflect({'ablt'}).word)
                st += ' ' + ', '.join(syrups) + ' сиропами'
            elif self.checkBox.isChecked():
                st += ' без сиропа'
            else:
                st += ' с'
                for el in self.syrupGroup.buttons()[1:]:
                    if el.isChecked():
                        text_syr1 = morph.parse(el.text().split()[0])[0]
                        st += ' ' + text_syr1.inflect({'ablt'}).word + ' сиропом'
                        break
            st += ': ' + str(coffee_cost)
            self.order_coffee.append(st)
            self.full_order.append(st)
            self.listWidget.clear()
            for coffee_ordered in self.order_coffee:
                self.listWidget.addItem(coffee_ordered)
            for tea in self.tea_in_order.values():
                if tea != '':
                    self.listWidget.addItem(tea)
            for dessert in self.dessert_in_order.values():
                if dessert != '':
                    self.listWidget.addItem(dessert)
            self.price += coffee_cost
            self.priceLabel.setText(str(self.price))
        except UnboundLocalError:
            my_dialog = MyDialog('Ошибка!', 'Выберите кофе, прежде чем добавлять его в заказ', self)
            my_dialog.exec_()

    def default_tea_amount(self):
        tea = self.sender().text()
        if tea == 'Dragon Well Tea':
            self.spinBox.setValue(1)
        elif tea == 'Iron Goddes':
            self.spinBox_2.setValue(1)
        elif tea == 'Junshan Silver Needle':
            self.spinBox_3.setValue(1)
        elif tea == 'Keemun Black Tea':
            self.spinBox_4.setValue(1)
        elif tea == 'White Hair of Pekoe Silver Needle':
            self.spinBox_5.setValue(1)

    def tea_amount_changed(self):
        if self.sender().value() == 0:
            if self.checkBox_7.isChecked() and self.spinBox.value() == 0:
                self.checkBox_7.setChecked(False)
            elif self.checkBox_8.isChecked() and self.spinBox_2.value() == 0:
                self.checkBox_8.setChecked(False)
            elif self.checkBox_9.isChecked() and self.spinBox_3.value() == 0:
                self.checkBox_9.setChecked(False)
            elif self.checkBox_10.isChecked() and self.spinBox_4.value() == 0:
                self.checkBox_10.setChecked(False)
            elif self.checkBox_11.isChecked() and self.spinBox_5.value() == 0:
                self.checkBox_11.setChecked(False)
        else:
            if not self.checkBox_7.isChecked() and self.spinBox.value() != 0:
                self.checkBox_7.setChecked(True)
            elif not self.checkBox_8.isChecked() and self.spinBox_2.value() != 0:
                self.checkBox_8.setChecked(True)
            elif not self.checkBox_9.isChecked() and self.spinBox_3.value() != 0:
                self.checkBox_9.setChecked(True)
            elif not self.checkBox_10.isChecked() and self.spinBox_4.value() != 0:
                self.checkBox_10.setChecked(True)
            elif not self.checkBox_11.isChecked() and self.spinBox_5.value() != 0:
                self.checkBox_11.setChecked(True)

    def add_tea(self):
        x = True
        for el in self.teaGroup.buttons():
            if el.isChecked():
                st = ''
                x = False
                tea = el.text()
                amount = self.tea_dict[tea].value()
                if tea in self.order_tea:
                    if self.order_tea[tea] + amount > 99:
                        my_dialog = MyDialog('Ошибка!', 'Вы не можете заказать больше, чем 99 стаканов этого чая', self)
                        my_dialog.exec_()
                    else:
                        self.order_tea[tea] += amount
                        self.price += amount * float(float(self.tea_dict2[tea].text()))
                        st += (tea + ' x{}'.format(self.order_tea[tea])
                               + ': {}'.format(self.order_tea[tea] * float(float(self.tea_dict2[tea].text()))))
                        self.tea_in_order[tea] = st
                        self.listWidget.clear()
                        for coffee_ordered in self.order_coffee:
                            self.listWidget.addItem(coffee_ordered)
                        for value in self.tea_in_order.values():
                            if value != '':
                                self.listWidget.addItem(value)
                        for dessert in self.dessert_in_order.values():
                            if dessert != '':
                                self.listWidget.addItem(dessert)
                        self.priceLabel.setText(str(self.price))
                        if tea not in self.full_order:
                            self.full_order.append(tea)
                else:
                    self.order_tea[tea] = amount
                    self.price += amount * float(self.tea_dict2[tea].text())
                    st += (tea + ' x{}'.format(amount)
                           + ': {}'.format(amount * float(float(self.tea_dict2[tea].text()))))
                    self.tea_in_order[tea] = st
                    self.listWidget.clear()
                    if tea not in self.full_order:
                        self.full_order.append(tea)
                    for coffee_ordered in self.order_coffee:
                        self.listWidget.addItem(coffee_ordered)
                    for value in self.tea_in_order.values():
                        if value != '':
                            self.listWidget.addItem(value)
                    for dessert in self.dessert_in_order.values():
                        if dessert != '':
                            self.listWidget.addItem(dessert)
                    self.priceLabel.setText(str(self.price))
        if x:
            my_dialog = MyDialog('Ошибка!', 'Вы должны сначала выбрать чай, прежде чем добавлять его в заказ', self)
            my_dialog.exec_()

    def default_dessert_amount(self):
        dessert = self.sender().text()
        if dessert == 'Черничные маффины':
            self.spinBox_6.setValue(1)
        elif dessert == 'Чизкейк':
            self.spinBox_7.setValue(1)
        elif dessert == 'Булочки с малиной и корицей':
            self.spinBox_8.setValue(1)
        elif dessert == 'Пончик с ванильной глазурью':
            self.spinBox_9.setValue(1)
        elif dessert == 'Тёмный шоколад ручной работы':
            self.spinBox_10.setValue(1)

    def dessert_amount_changed(self):
        if self.sender().value() == 0:
            if self.checkBox_12.isChecked() and self.spinBox_6.value() == 0:
                self.checkBox_12.setChecked(False)
            elif self.checkBox_13.isChecked() and self.spinBox_7.value() == 0:
                self.checkBox_13.setChecked(False)
            elif self.checkBox_14.isChecked() and self.spinBox_8.value() == 0:
                self.checkBox_14.setChecked(False)
            elif self.checkBox_15.isChecked() and self.spinBox_9.value() == 0:
                self.checkBox_15.setChecked(False)
            elif self.checkBox_16.isChecked() and self.spinBox_10.value() == 0:
                self.checkBox_16.setChecked(False)
        else:
            if not self.checkBox_12.isChecked() and self.spinBox_6.value() != 0:
                self.checkBox_12.setChecked(True)
            elif not self.checkBox_13.isChecked() and self.spinBox_7.value() != 0:
                self.checkBox_13.setChecked(True)
            elif not self.checkBox_14.isChecked() and self.spinBox_8.value() != 0:
                self.checkBox_14.setChecked(True)
            elif not self.checkBox_15.isChecked() and self.spinBox_9.value() != 0:
                self.checkBox_15.setChecked(True)
            elif not self.checkBox_16.isChecked() and self.spinBox_10.value() != 0:
                self.checkBox_16.setChecked(True)

    def add_dessert(self):
        x = True
        for el in self.dessertsGroup.buttons():
            if el.isChecked():
                st = ''
                x = False
                dessert = el.text()
                amount = self.dessert_dict[dessert].value()
                if dessert in self.order_dessert:
                    if self.order_dessert[dessert] + amount > 99:
                        my_dialog = MyDialog('Ошибка!', 'Вы не можете заказать больше, чем 99 порций', self)
                        my_dialog.exec_()
                    else:
                        self.order_dessert[dessert] += amount
                        self.price += amount * float(float(self.dessert_dict2[dessert].text()))
                        st += (dessert + ' x{}'.format(self.order_dessert[dessert]) +
                               ': {}'.format(self.order_dessert[dessert]
                                             * float(float(self.dessert_dict2[dessert].text()))))
                        self.dessert_in_order[dessert] = st
                        self.listWidget.clear()
                        for coffee_ordered in self.order_coffee:
                            self.listWidget.addItem(coffee_ordered)
                        for tea in self.tea_in_order.values():
                            if tea != '':
                                self.listWidget.addItem(tea)
                        for value in self.dessert_in_order.values():
                            if value != '':
                                self.listWidget.addItem(value)
                        self.priceLabel.setText(str(self.price))
                else:
                    self.order_dessert[dessert] = amount
                    self.price += amount * float(self.dessert_dict2[dessert].text())
                    st += (dessert + ' x{}'.format(amount) +
                           ': {}'.format(amount * float(float(self.dessert_dict2[dessert].text()))))
                    self.dessert_in_order[dessert] = st
                    self.listWidget.clear()
                    if dessert not in self.full_order:
                        self.full_order.append(dessert)
                    for coffee_ordered in self.order_coffee:
                        self.listWidget.addItem(coffee_ordered)
                    for tea in self.tea_in_order.values():
                        if tea != '':
                            self.listWidget.addItem(tea)
                    for value in self.dessert_in_order.values():
                        if value != '':
                            self.listWidget.addItem(value)
                    self.priceLabel.setText(str(self.price))
        if x:
            my_dialog = MyDialog('Ошибка!', 'Вы должны сначала выбрать десерт, прежде чем добавлять его в заказ', self)
            my_dialog.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Cafe()
    ex.show()
    sys.exit(app.exec_())
