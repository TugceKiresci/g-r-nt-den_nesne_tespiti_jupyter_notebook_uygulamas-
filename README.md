API İLE İLGİLİ BİLGİLER

Klasör Yapısı:
api/
└── api_project/
└── camera/ # API kodlarının bulunduğu klasör

Kurulum Adımları:
1) Klasöre Gir
	cd Desktop/yeni_api
2)Sanal Ortamı Oluştur (ilk kez kurulum yapılıyorsa)
	python -m venv myenv (Sİstemine bağlı olarak python yerine python3 de kullanılabilir.)
	//Bu işlem sonun yeni_api klasöründe myenv adında bir klasör oluşur.
3) Sanal Ortamı Aktifleştir
	myenv\Scripts\activate

4) API'yi Çalıştırmak
	cd api_project (projenin çalıştırılacağı klasöre gidilir.)
	python manage.py runserver (API' yi çalıştıran komut. Bu komut sonucunda API linki gelmeli.)


KAMERA İLE İLE İLGİLİ UYGULAMALAR 

1) Robot Tespiti Uygulaması
2)Hareketli Nesne Yön Tahmini Uygulaması

Kurulum

Aşağıdaki Python paketlerinin yüklü olması gerekir:
pip install opencv-python ipywidgets matplotlib Pillow requests numpy ipympl

Jupyter Notebook’ta widget desteği için şu komut çalıştırılmalıdır:
jupyter nbextension enable --py widgetsnbextension --sys-prefix


Klasör Yapısı
.
├── Kamera_Uygulamaları.ipynb
├── dataset/                  # Görüntü dosyaları
├── dataset_videos/          # Video dosyaları (hareket analizi için)


1)Robot Tespiti Uygulaması

Özellikler
-Görüntü kaynağı olarak dataset, webcam, veya API seçilebilir.
-Üç farklı tespit algoritması sekmeler (tabs) halinde sunulmaktadır:
	Algoritma 1: Belirli filtreleme ve eşikleme
	Algoritma 2: Renk tabanlı maskeleme
	Algoritma 3: Gelişmiş eşikleme veya morfolojik işlemler
	(algoritmalar değiştirilebilir ve genişletilebilir yapıdadır)
-Her algoritma sekmesinde yalnızca o algoritmaya ait parametreler görünür.
-Dataset seçildiğinde tam orijinal görüntü, renk bozulmadan gösterilir.
-Webcam veya API kaynağı seçildiğinde sabit pencere içinde gerçek zamanlı video önizleme yapılır.
-“Görüntü İşle” butonuna basıldığında o anki görüntü yakalanır, işlenir ve gösterilir.

Kullanım Akışı

Dataset seçilirse:
-Dropdown menüden görüntü seçilir.
-Görüntü doğrudan gösterilir.

Webcam veya API seçilirse:
-Video önizleme canlı olarak gösterilir.
-“Görüntü İşle” butonuna tıklanınca önizleme durur, kare alınır ve işlenmiş hali gösterilir.

NOT:Dataset seçilince diğer kaynaklara ait bileşenler inaktif hale gelir (tersi de geçerlidir).

2)Hareketli Nesne Yön Tahmini Uygulaması

Özellikler

Görüntü kaynağı: dataset_videos, webcam, veya API

-Hareketli pikseller belirlenerek yön tespiti yapılır.
-Hareketli alanlar dikdörtgen içinde gösterilir.
-Görüntü sabit boyutlu pencere (640x480) içinde oynatılır.
-Webcam/API kaynaklarında canlı video önizleme yapılır.
-“Görüntü İşle” butonuna basıldığında video durur.
-O anki görüntü işlenerek yön bilgisi elde edilir ve işaretlenmiş olarak gösterilir.


