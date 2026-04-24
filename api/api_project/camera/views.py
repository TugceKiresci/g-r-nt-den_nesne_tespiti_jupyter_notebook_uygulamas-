import os
import threading
import cv2
import csv
import json
import time
import numpy as np
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import SensorData
from .serializers import SensorDataSerializer
from .lidar_manager import start_lidar_thread, get_latest_scan
from rplidar import RPLidar
from io import BytesIO
import zipfile
from django.shortcuts import render
from django.shortcuts import redirect



# Ana Sayfa
def home(request):
    message = request.GET.get("message", "")
    html = f"""
        <html>
            <head>
                <title>🔧 API Kontrol Paneli</title>
                <style>
                    body {{
                        background-color: black;
                        color: white;
                        font-family: Arial, sans-serif;
                        text-align: center;
                        margin: 0;
                        padding: 20px;
                    }}
                    h1 {{
                        margin-bottom: 30px;
                    }}
                    .container {{
                        display: flex;
                        justify-content: center;
                        gap: 30px;
                        max-width: 1200px;
                        margin: 0 auto;
                    }}
                    .column {{
                        background-color: #1a1a1a;
                        border-radius: 10px;
                        padding: 20px;
                        width: 33%;
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
                    }}
                    .column h2 {{
                        margin: 0 0 20px;
                        font-size: 18px;
                    }}
                    .card {{
                        background-color: #2a2a2a;
                        border-radius: 8px;
                        padding: 10px;
                        margin-bottom: 15px;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                    }}
                    .card h3 {{
                        margin: 0 0 5px;
                        font-size: 14px;
                    }}
                    .card form {{
                        margin: 0;
                    }}
                    .card button {{
                        background-color: green;
                        color: white;
                        padding: 6px 12px;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        width: 100%;
                    }}
                    .card button:hover {{
                        background-color: #45a049;
                    }}
                    .card input {{
                        margin: 5px 0;
                        padding: 4px;
                        width: 90%;
                        border-radius: 4px;
                        border: 1px solid #333;
                        background-color: #3a3a2a;
                        color: white;
                    }}
                    #message {{
                        color: #00ff00;
                        margin-bottom: 20px;
                        font-size: 16px;
                    }}
                </style>
                <script>
                    function showAlert(message) {{
                        alert(message);
                    }}

                    document.addEventListener('DOMContentLoaded', function() {{
                        // Görüntü Veri Seti Oluştur
                        document.getElementById('image-dataset-form').addEventListener('submit', function(e) {{
                            e.preventDefault();
                            const numImages = this.querySelector('input[name="num_images"]').value;
                            fetch(this.action + '?num_images=' + numImages)
                                .then(response => response.text())
                                .then(data => showAlert('Başarıyla ' + numImages + ' görüntü kaydedildi'))
                                .catch(error => showAlert('Hata: ' + error));
                        }});

                        // Video Kaydet
                        document.getElementById('video-capture-form').addEventListener('submit', function(e) {{
                            e.preventDefault();
                            const duration = this.querySelector('input[name="duration"]').value;
                            fetch(this.action + '?duration=' + duration)
                                .then(response => response.text())
                                .then(data => showAlert('Başarıyla ' + duration + ' saniyelik video kaydedildi'))
                                .catch(error => showAlert('Hata: ' + error));
                        }});
                    }});
                </script>
            </head>
            <body>
                <h1>🔧 API Kontrol Paneli</h1>
                <div id="message">{message}</div>
                <div class="container">
                    <!-- Görüntü Sütunu -->
                    <div class="column">
                        <h2>📷 Görüntü</h2>
                        <div class="card">
                            <h3>Görüntü Akışını İzle</h3>
                            <form action="/video/" method="get">
                                <button type="submit">Görüntüyü Aç</button>
                            </form>
                        </div>
                        <div class="card">
                            <h3>Görüntü Veri Seti Oluştur</h3>
                            <form id="image-dataset-form" action="/api/create-image-dataset-stream/" method="get">
                                <input type="number" name="num_images" value="10" min="1" placeholder="Fotoğraf Sayısı">
                                <button type="submit">Oluştur</button>
                            </form>
                        </div>
                        <div class="card">
                            <h3>Görüntü Veri Setini İndir</h3>
                            <form action="/api/download-image-dataset/" method="get">
                                <button type="submit">İndir</button>
                            </form>
                        </div>
                    </div>

                    <!-- Video Sütunu -->
                    <div class="column">
                        <h2>🎥 Video</h2>
                        <div class="card">
                            <h3>Video Kaydet</h3>
                            <form id="video-capture-form" action="/api/video-capture/" method="get">
                                <input type="number" name="duration" value="10" min="1" placeholder="Süre (sn)">
                                <button type="submit">Kaydet</button>
                            </form>
                        </div>
                        <div class="card">
                            <h3>Video Veri Setini İndir</h3>
                            <form action="/api/download-video-dataset/" method="get">
                                <button type="submit">İndir</button>
                            </form>
                        </div>
                    </div>

                    <!-- LIDAR Sütunu -->
                    <div class="column">
                        <h2>📡 LIDAR</h2>
                        <div class="card">
                            <h3>LIDAR Verisi Akışı</h3>
                            <form action="/api/stream-lidar/" method="get">
                                <button type="submit">Akışı Başlat</button>
                            </form>
                        </div>
                        <div class="card">
                            <h3>LIDAR Veri Seti Kaydet</h3>
                            <form action="/api/record-lidar-dataset/" method="get">
                                <input type="number" name="rounds" value="10" min="1">
                                <input type="text" name="filename" value="dataset.csv" placeholder="Dosya Adı">
                                <button type="submit">Kaydet</button>
                            </form>
                        </div>
                        <div class="card">
                            <h3>LIDAR Veri Setini İndir</h3>
                            <form action="/api/list-lidar-datasets/" method="get">
                                <button type="submit">İndir</button>
                            </form>
                        </div>
                    </div>
                </div>
            </body>
        </html>
    """
    return HttpResponse(html)

# Görüntü Akışı Sayfası
def video(request):
    html = """
        <html>
            <head>
                <title>📷 Canlı Görüntü Akışı</title>
                <style>
                    body {
                        background-color: black;
                        color: white;
                        font-family: Arial, sans-serif;
                        text-align: center;
                        margin: 0;
                        padding: 20px;
                    }
                    #video-container {
                        max-width: 640px;
                        max-height: 480px;
                        margin: 20px auto;
                        border: 2px solid #333;
                    }
                    img {
                        width: 100%;
                        height: auto;
                    }
                </style>
            </head>
            <body>
                <h1>📷 Canlı Görüntü Akışı</h1>
                <div id="video-container">
                    <img src="/api/video-feed/" autoplay />
                </div>
                <a href="/">Ana Sayfaya Dön</a>
            </body>
        </html>
    """
    return HttpResponse(html)

# Kamera Verisi
class SensorDataViewSet(viewsets.ModelViewSet):
    queryset = SensorData.objects.all().order_by('-timestamp')
    serializer_class = SensorDataSerializer

# Video Kaydı
class VideoCaptureView(APIView):
    def get(self, request, *args, **kwargs):
        duration = int(request.GET.get("duration", 10))  # saniye cinsinden süre
        timestamp = time.strftime("%H%M%S_%d%m%Y")
        output_dir = os.path.join("media", "video_dataset", timestamp)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"video_{timestamp}.avi")

        def generate_video():
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                raise Exception("Kamera açılamadı.")
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(output_path, fourcc, 20.0, (640, 480))
            start_time = time.time()
            while int(time.time() - start_time) < duration:
                ret, frame = cap.read()
                if not ret:
                    cap.release()
                    out.release()
                    raise Exception("Video yakalanamadı")
                out.write(frame)
            cap.release()
            out.release()
            yield f"data: Video kaydedildi: {output_path}\n\n"

        try:
            return StreamingHttpResponse(generate_video(), content_type='text/event-stream')
        except Exception as e:
            return HttpResponse(f"Video kaydedilemedi: {str(e)}", status=500)

    @csrf_exempt
    def download_video(self, request, filename):
        file_path = os.path.join("media", "video_dataset", filename)
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)
        else:
            return HttpResponse("❌ Video bulunamadı", status=404)

# Görüntü Veri Seti Oluşturma
@csrf_exempt
def create_image_dataset_stream(request):
    try:
        num_images = int(request.GET.get("num_images", 10))
        timestamp = time.strftime("%H%M%S_%d%m%Y")
        output_dir = os.path.join("media", "image_dataset", timestamp)
        os.makedirs(output_dir, exist_ok=True)
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            cap.release()
            raise Exception("Kamera açılamadı.")

        count = 0
        while count < num_images:
            ret, frame = cap.read()
            if not ret:
                print(f"⚠️ Görüntü alınamadı.")
                break
            _, jpeg = cv2.imencode('.jpg', frame)
            filename = os.path.join(output_dir, f"image_{count}_{timestamp}.jpg")
            cv2.imwrite(filename, frame)
            print(f"✅ {filename} kaydedildi.")
            count += 1
            time.sleep(0.5)  # Her fotoğraf arasında 0.5 saniye bekle
        cap.release()
        return HttpResponse("OK")
    except Exception as e:
        return HttpResponse(f"Hata: {str(e)}", status=500)

# Sürekli Video Feed
from django.http import StreamingHttpResponse, HttpResponse
import cv2
import time
import logging

# Loglama ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def video_feed(request):
    if request.method != 'GET':
        logger.error(f"Yanlış istek yöntemi: {request.method}")
        return HttpResponse("Yalnızca GET istekleri destekleniyor.", status=405)

    def generate_frames():
        # DirectShow backend'ini kullan
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            logger.error("Kamera açılamadı: Cihaz bağlantısını, indeksini veya sürücüleri kontrol edin.")
            raise Exception("Kamera açılamadı.")
        
        try:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            logger.info("Kamera açıldı, akış başlatılıyor...")
            while True:
                ret, frame = cap.read()
                if not ret or frame is None or frame.size == 0:
                    logger.warning("Kare alınamadı, yeniden deneniyor...")
                    time.sleep(0.1)
                    continue
                ret, jpeg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
                if not ret:
                    logger.warning("JPEG kodlama hatası, atlanıyor...")
                    continue
                logger.info(f"Kare alındı, boyut: {frame.shape}, JPEG boyutu: {len(jpeg)}")
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
                time.sleep(0.033)  # ~30 FPS
        except Exception as e:
            logger.error(f"Akış sırasında hata: {str(e)}")
            raise
        finally:
            cap.release()
            logger.info("📷 Kamera serbest bırakıldı.")

    try:
        logger.info("Video akışı başlatılıyor...")
        return StreamingHttpResponse(
            generate_frames(),
            content_type='multipart/x-mixed-replace; boundary=frame'
        )
    except Exception as e:
        logger.error(f"Video akışı hatası: {str(e)}")
        return HttpResponse(f"Hata: {str(e)}", status=500)
# Resim ve Video Veri Seti İndirme
@csrf_exempt
def download_image_dataset(request):
    dataset_dir = os.path.join("media", "image_dataset")
    return _download_dataset(request, dataset_dir)

@csrf_exempt
def download_video_dataset(request):
    dataset_dir = os.path.join("media", "video_dataset")
    return _download_dataset(request, dataset_dir)

def _download_dataset(request, dataset_dir):
    try:
        if not os.path.exists(dataset_dir):
            return HttpResponse("❌ Veri seti klasörü bulunamadı", status=404)
        subdirs = [d for d in os.listdir(dataset_dir) if os.path.isdir(os.path.join(dataset_dir, d))]
        if not subdirs:
            return HttpResponse("❌ İndirilecek veri seti bulunamadı", status=404)
        latest_dir = max(subdirs, key=lambda x: os.path.getctime(os.path.join(dataset_dir, x)))
        timestamp = time.strftime("%H%M%S_%d%m%Y")
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for root, _, files in os.walk(os.path.join(dataset_dir, latest_dir)):
                for file in files:
                    file_path = os.path.join(root, file)
                    zip_file.write(file_path, file)
        zip_buffer.seek(0)
        dataset_type = "image" if "image_dataset" in dataset_dir else "video"
        return FileResponse(zip_buffer, as_attachment=True, filename=f"{dataset_type}_dataset_{timestamp}.zip")
    except Exception as e:
        return HttpResponse(f"❌ Hata: {str(e)}", status=500)
    
@csrf_exempt
def capture_image(request):
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return redirect('/?message=Kamera+açılamadı')

        ret, frame = cap.read()
        if not ret:
            cap.release()
            return redirect('/?message=Görüntü+alınamadı')

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        os.makedirs("captured_images", exist_ok=True)
        path = f"captured_images/image_{timestamp}.jpg"
        cv2.imwrite(path, frame)
        cap.release()

        # Anasayfaya başarılı mesajla dön
        return redirect('/?message=Fotoğraf+başarıyla+çekildi')

    except Exception as e:
        return redirect(f"/?message=Hata:+{str(e).replace(' ', '+')}")

# LIDAR Fonksiyonları
lock = threading.Lock()
latest_scan = []
lidar_thread = None
lidar = None
running = False
lidar_instance = None

def start_lidar_thread():
    global lidar_thread, running, lidar
    with lock:
        if not running:
            lidar = RPLidar('COM3')
            running = True
            lidar_thread = threading.Thread(target=read_lidar_data, daemon=True)
            lidar_thread.start()

def read_lidar_data():
    global latest_scan, running
    try:
        for scan in lidar.iter_scans():
            with lock:
                latest_scan = [(int(angle), int(dist)) for (_, angle, dist) in scan if dist > 0]
            time.sleep(0.05)
            if not running:
                break
    except:
        pass

def get_latest_scan():
    with lock:
        return list(latest_scan)

def stop_lidar():
    global running, lidar
    with lock:
        running = False
        if lidar:
            try:
                lidar.stop()
                lidar.disconnect()
            except:
                pass
            lidar = None

def get_lidar():
    global lidar_instance
    if lidar_instance is None:
        try:
            lidar_instance = RPLidar('COM3')
        except Exception as e:
            print("❌ LIDAR bağlanamadı:", e)
            raise e
    return lidar_instance

@csrf_exempt
def stream_lidar(request):
    start_lidar_thread()
    def event_stream():
        while True:
            scan = get_latest_scan()
            yield f"data: {json.dumps({'scan': scan})}\n\n"
            time.sleep(0.1)
    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')

class CaptureLidarStreamView(APIView):
    def get(self, request, *args, **kwargs):
        lidar = get_lidar()
        def lidar_stream():
            try:
                for scan in lidar.iter_scans():
                    scan_data = [(int(angle), int(dist)) for (_, angle, dist) in scan if dist > 0]
                    if not scan_data:
                        continue
                    data = json.dumps({"scan": scan_data})
                    yield f"data: {data}\n\n"
                    time.sleep(0.1)
            except Exception as e:
                yield f"event: error\ndata: {str(e)}\n\n"
        return StreamingHttpResponse(lidar_stream(), content_type='text/event-stream')

@csrf_exempt
def record_lidar_dataset(request):
    try:
        rounds = int(request.GET.get("rounds", 10))
        filename = request.GET.get("filename", "dataset.csv")

        if not filename.endswith(".csv"):
            filename += ".csv"

        start_lidar_thread()
        scan_interval = 0.1
        collected_scans = []

        current_round = 0
        while current_round < rounds:
            scan = get_latest_scan()
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            for angle, dist in scan:
                collected_scans.append([timestamp, angle, dist])
            current_round += 1
            time.sleep(scan_interval)

        os.makedirs("scans", exist_ok=True)
        csv_path = os.path.join("scans", filename)

        with open(csv_path, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "angle", "distance"])
            writer.writerows(collected_scans)

        return JsonResponse({
            "status": "success",
            "total_points": len(collected_scans),
            "rounds": rounds,
            "file": csv_path
        })

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})

@csrf_exempt
def list_lidar_datasets(request):
    files = []
    scans_dir = "scans"
    if os.path.exists(scans_dir):
        for fname in os.listdir(scans_dir):
            if fname.endswith(".csv"):
                files.append(fname)
    return render(request, "dataset_list.html", {"files": files})

@csrf_exempt
def download_lidar_file(request, filename):
    file_path = os.path.join("scans", filename)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)
    else:
        return HttpResponse("❌ Dosya bulunamadı", status=404)