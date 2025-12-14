#!/usr/bin/env python3
"""
Basit sinav kopya tespit sisteminin sade surumu
"""

import cv2
import numpy as np
from datetime import datetime

def simple_face_detection():
    """Sadece OpenCV kullanarak yuz tespiti"""
    # Yuz tespit modeli yukleniyor
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Kamera aciliyor
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Hata: Kameraya erisilemiyor")
        return
    
    print("✅ Kopya tespit sistemi calisiyor!")
    print("📹 Cikmak icin 'q' tusuna basin")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Hata: Kare okunamadi")
            break
        
        # Tespit icin gri tona cevir
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Yuzleri tespit et
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        # Durum bilgisini hazirla
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_color = (0, 255, 0)  # Varsayilan yesil
        status_text = "✅ Durum normal"
        
        # Sonuclari analiz et
        if len(faces) == 0:
            status_color = (0, 0, 255)  # Kirmizi
            status_text = "⚠️ Hic yuz bulunamadi!"
            print(f"🚨 Uyari: Yuz kayboldu - {timestamp}")
        elif len(faces) > 1:
            status_color = (0, 165, 255)  # Turuncu
            status_text = f"⚠️ {len(faces)} yuz bulundu!"
            print(f"🚨 Uyari: Birden fazla yuz - {timestamp}")
        else:
            status_text = "✅ Tek bir yuz bulundu"
        
        # Yuzlerin etrafina kutu ciz
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), status_color, 2)
            cv2.putText(frame, f"Face {len(faces)}", (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        
        # Durum bilgilerini ekle
        cv2.putText(frame, status_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
        cv2.putText(frame, timestamp, (10, frame.shape[0] - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Pencereyi goster
        cv2.imshow('Sinav gozlem sistemi - Basit surum', frame)
        
        # q tusuna basilirsa cik
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Kaynaklari serbest birak
    cap.release()
    cv2.destroyAllWindows()
    print("🔚 Izleme sonlandirildi")

if __name__ == "__main__":
    simple_face_detection()