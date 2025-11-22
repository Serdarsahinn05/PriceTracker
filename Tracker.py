import requests  # html haline getirip veri çekiyo
from bs4 import BeautifulSoup  # html haline gelen veriyi işliyo
import json
import webbrowser  # tarayıcı açmak
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QListWidget, QListWidgetItem, QMessageBox, QSystemTrayIcon,
    QFileDialog, QCheckBox, QInputDialog, QComboBox, QMainWindow, QDialog,
    QListView, QDialogButtonBox, QMenu, QSlider, QLayout
)
from PySide6.QtGui import QIcon, QPixmap, QAction
from PySide6.QtCore import Qt,QSize


"""
1) Kullanıcı uygulamaya istediği ürünün linkini atar(epey kullancaz mecbur ya da cimri ya da tek site trendyol falan)
1.1) Veyahut arayüz yaparız oradan ürünün adını aratır epeyden falan buldurturuz
2) Bir fiyat yazar o fiyata gelince bildirim atar.
3) Ürünün satıldığı sitenin adresini de seçebilir

"""

# ------------Ayarlar-------------
CHECK_INTERVAL_DEFAULT = 30
SAVEFILE = "products.json"


#En sondaki sayılar ID siymiş onu kullan sonrakilerde
# ------------Ürün Bilgisi Çekme Fonksiyonu-------------
def get_url(url):
    response = requests.get(url)
    return response.text


# ------------Ürün Bilgisi İşleme Fonksiyonu-------------
def get_item_info(url):
    page_content = get_url(url)
    soup = BeautifulSoup(page_content, 'html.parser')
    if "trendyol.com" in url:
        product_name = soup.find("h1", class_="product-title").get_text(strip=True)
        product_price = soup.find("div", class_="price-wrapper").get_text(strip=True).split("TL")
        product_url = url
        split_url = url.split("-")
        product_id = split_url[-1]
        product_image = soup.find("div", class_="product-image-gallery-wrapper").find("img")["src"]

        return {
            "name": product_name,
            "price": product_price,
            "url": product_url,
            "image": product_image,
            "id": product_id
        }
    else:
        return None


"""
1)isim
2)fiyat
3)link
4)istenen fiyat
5)son kontrol zamanı
6)kontrol aralığı
7)aktif/pasif
8)bildirim türü (sesli/görsel)
9) Stok durumu (var/yok)

"""


# ------------ürün Listeleme Arayüzü-------------
class productWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ürün Takipçisi")
        self.setMinimumSize(QSize(500, 800))






        self.init_ui()

    def value_changed(self, value):
        print(value)

    def slider_position(self, position):
        print("position", position)

    def slider_pressed(self):
        print("Pressed!")

    def slider_released(self):
        print("Released")

    def init_ui(self):
        textLayout = QVBoxLayout()

        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Ürün Linkini Girin")

        textLayout.addWidget(self.url_input)
        textLayout.setAlignment(Qt.AlignTop)



        self.setLayout(textLayout)


    def item_info(self, product_info):


        chartBtn = QPushButton("Sepeti Görüntüle")
        chartBtn.clicked.connect(self.open_chart)
        self.layout().addWidget(chartBtn)
        addBtn = QPushButton(
            icon=QIcon("./icons/add_icons.png"),
            iconSize=QSize(24, 24),
            toolTip="Ürünü Sepete Ekle"
        )

        addBtn.clicked.connect(self.add_button_clicked)

        productLayout = QVBoxLayout()
        imageLayout = QHBoxLayout()
        self.id_label = QLabel(product_info['id'])
        self.name_label = QLabel(product_info['name'])
        self.price_label = QLabel(f"Fiyat: {product_info['price']} TL")
        self.image_label = QLabel()
        self.url_label = QLabel(product_info['url'])



        pixmap = QPixmap()
        pixmap.loadFromData(requests.get(product_info['image']).content)
        self.image_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))


        imageLayout.addWidget(self.image_label)

        productLayout.addWidget(self.id_label)
        productLayout.addWidget(self.url_label)
        productLayout.addWidget(self.name_label)
        productLayout.addWidget(self.price_label)



        imageLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        productLayout.setAlignment(Qt.AlignTop)

        imageLayout.addLayout(productLayout)
        imageLayout.addWidget(addBtn)
        self.layout().addLayout(imageLayout)



    def add_button_clicked(self):
        arr = self.load_info_from_json()
        print(arr)


        product_info = {
            'id': self.id_label.text(),
            'name': self.name_label.text(),
            'price': self.price_label.text().replace("Fiyat: ", "").replace(" TL", ""),
            'url': self.url_label.text()

        }

        arr.append(product_info)
        print(arr)
        if product_info:
            try:
                with open(SAVEFILE, 'w', encoding="utf-8") as f:
                    json.dump(arr, f, ensure_ascii=False, indent=2)
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Ürün kaydedilemedi: {str(e)}")
                return



            QMessageBox.information(self, "Başarılı", "Ürün sepete eklendi.")
        else:
            QMessageBox.warning(self, "Hata", "Ürün bilgisi alınamadı.")




    def load_info_from_json(self):
        try:
            with open(SAVEFILE, 'r', encoding="utf-8") as f:
                data = json.load(f)
                return data
        except FileNotFoundError:
            return []
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Hata", f"JSON dosyası okunamadı: {str(e)}")
            return []

    def open_chart(self):
        self.chart_window = chartWidget()
        self.chart_window.show()




    def keyPressEvent(self, event):

        try:
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                print(self.url_input.text())
                product_info = get_item_info(self.url_input.text())
                if product_info:
                    self.item_info(product_info)
                    self.url_input.setText("")
                else:
                    QMessageBox.warning(self, "Hata", "Ürün bilgisi alınamadı.")
            return None
        except Exception as e:
            QMessageBox.critical(self, "Hata: URL Geçersiz", str(e))






# ------------Sepet Arayüzü-------------
class chartWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sepetim")
        self.setMinimumSize(QSize(400, 600))
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        products = self.load_info_from_json()

        for product in products:
            product_label = QLabel(
                f"ID: {product['id']} \n"
                f"Name: {product['name']} \n" 
                f"Price: {product['price']} TL \n"
                f"Url: {product['url']} \n"
            )
            layout.addWidget(product_label)
    def load_info_from_json(self):
        try:
            with open(SAVEFILE, 'r', encoding="utf-8") as f:
                data = json.load(f)
                return data
        except FileNotFoundError:
            return []
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Hata", f"JSON dosyası okunamadı: {str(e)}")
            return []











def __main__():
    tracker_app = QApplication(sys.argv)
    tracker_window = productWidget()
    tracker_window.show()

    sys.exit(tracker_app.exec())


if __name__ == "__main__":
    __main__()
