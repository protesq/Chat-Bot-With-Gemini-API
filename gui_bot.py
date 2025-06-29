#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import os
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from google import genai

class ChatWorker(QThread):
    """Bot yanıtını ayrı thread'de çalıştırmak için"""
    response_ready = pyqtSignal(str)
    
    def __init__(self, client, model, message, history):
        super().__init__()
        self.client = client
        self.model = model
        self.message = message
        self.history = history
    
    def run(self):
        try:
            # Geçmişle birlikte mesaj oluştur
            if self.history:
                tam_gecmis = "\n".join([
                    f"Kullanıcı: {item['kullanici']}\nBot: {item['bot']}" 
                    for item in self.history[-5:]  # Son 5 mesajı al
                ])
                tam_mesaj = f"Önceki konuşma:\n{tam_gecmis}\n\nYeni mesaj:\nKullanıcı: {self.message}"
            else:
                tam_mesaj = self.message
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=tam_mesaj
            )
            
            self.response_ready.emit(response.text)
            
        except Exception as e:
            self.response_ready.emit(f"❌ Hata: {str(e)}")

class GeminiChatGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api_key = "YOUR_API_KEY"
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.5-flash"
        self.gecmis = []
        self.worker = None
        
        self.init_ui()
        self.load_history()
        
    def init_ui(self):
        """Arayüzü oluşturur"""
        self.setWindowTitle("🤖 Gemini AI Chat Bot")
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
                         QTextEdit {
                 background-color: #2d2d2d;
                 color: #ffffff;
                 border: 1px solid #3d3d3d;
                 border-radius: 8px;
                 padding: 8px;
                 font-family: 'Segoe UI', Arial, sans-serif;
                 font-size: 14px;
             }
            QLineEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 20px;
                padding: 8px 15px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 20px;
                padding: 8px 20px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QMenuBar {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background-color: #4CAF50;
                border-radius: 5px;
            }
            QMenu {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
            }
            QMenu::item:selected {
                background-color: #4CAF50;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title = QLabel("🤖 Gemini AI Chat Bot")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 10px;
            }
        """)
        main_layout.addWidget(title)
        
        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMinimumHeight(400)
        main_layout.addWidget(self.chat_display)
        
        # Input layout
        input_layout = QHBoxLayout()
        
        # Message input
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Mesajınızı buraya yazın...")
        self.message_input.returnPressed.connect(self.send_message)
        
        # Send button
        self.send_button = QPushButton("Gönder")
        self.send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.message_input, 4)
        input_layout.addWidget(self.send_button, 1)
        
        main_layout.addLayout(input_layout)
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #2d2d2d;
                color: #ffffff;
                border-top: 1px solid #3d3d3d;
            }
        """)
        self.status_bar.showMessage("Hazır ✅")
        
        # Menu bar
        self.create_menu()
        
        # Welcome message
        self.add_message("🤖 Bot", "Merhaba! Ben Gemini AI. Size nasıl yardımcı olabilirim?", is_bot=True)
    
    def create_menu(self):
        """Menü çubuğunu oluşturur"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('📁 Dosya')
        
        save_action = QAction('💾 Geçmişi Kaydet', self)
        save_action.triggered.connect(self.save_history)
        file_menu.addAction(save_action)
        
        load_action = QAction('📂 Geçmişi Yükle', self)
        load_action.triggered.connect(self.load_history)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        clear_action = QAction('🧹 Geçmişi Temizle', self)
        clear_action.triggered.connect(self.clear_chat)
        file_menu.addAction(clear_action)
        
        # Help menu
        help_menu = menubar.addMenu('❓ Yardım')
        
        about_action = QAction('ℹ️ Hakkında', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def add_message(self, sender, message, is_bot=False):
        """Chat'e mesaj ekler"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if is_bot:
            color = "#4CAF50"  # Yeşil
            icon = "🤖"
        else:
            color = "#2196F3"  # Mavi
            icon = "👤"
        
        html_message = f"""
        <div style="margin: 10px 0; padding: 10px; background-color: #3d3d3d; border-radius: 10px; border-left: 4px solid {color};">
            <div style="color: {color}; font-weight: bold; margin-bottom: 5px; font-size: 14px;">
                {icon} {sender} <span style="color: #888; font-size: 12px; font-weight: normal;">[{timestamp}]</span>
            </div>
            <div style="color: #ffffff; line-height: 1.4; font-size: 14px;">
                {message.replace('\n', '<br>')}
            </div>
        </div>
        """
        
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertHtml(html_message)
        
        # Auto scroll
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def send_message(self):
        """Mesaj gönderir"""
        message = self.message_input.text().strip()
        if not message:
            return
        
        # Kullanıcı mesajını ekle
        self.add_message("Sen", message)
        self.message_input.clear()
        
        # Geçmişe ekle
        self.gecmis.append({
            'kullanici': message,
            'bot': '',  # Bot yanıtı gelince doldurulacak
            'zaman': datetime.now().isoformat()
        })
        
        # Bot düşünüyor mesajı
        self.status_bar.showMessage("🤖 Bot düşünüyor...")
        self.send_button.setEnabled(False)
        self.message_input.setEnabled(False)
        
        # Worker thread'i başlat
        self.worker = ChatWorker(self.client, self.model, message, self.gecmis[:-1])
        self.worker.response_ready.connect(self.handle_bot_response)
        self.worker.start()
    
    def handle_bot_response(self, response):
        """Bot yanıtını işler"""
        # Bot mesajını ekle
        self.add_message("Gemini", response, is_bot=True)
        
        # Geçmişi güncelle
        if self.gecmis:
            self.gecmis[-1]['bot'] = response
        
        # UI'yi etkinleştir
        self.status_bar.showMessage("Hazır ✅")
        self.send_button.setEnabled(True)
        self.message_input.setEnabled(True)
        self.message_input.setFocus()
        
        # Worker'ı temizle
        if self.worker:
            self.worker.deleteLater()
            self.worker = None
    
    def clear_chat(self):
        """Chat'i temizler"""
        reply = QMessageBox.question(self, 'Temizle', 
                                   'Sohbet geçmişini temizlemek istediğinizden emin misiniz?',
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.chat_display.clear()
            self.gecmis = []
            self.add_message("🤖 Bot", "Geçmiş temizlendi. Yeni bir sohbete başlayalım!", is_bot=True)
    
    def save_history(self):
        """Geçmişi dosyaya kaydeder"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, 'Geçmişi Kaydet', 'sohbet_gecmisi.json', 
                'JSON files (*.json)'
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.gecmis, f, ensure_ascii=False, indent=2)
                
                QMessageBox.information(self, 'Başarılı', f'Geçmiş başarıyla kaydedildi:\n{filename}')
                
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'Kaydetme hatası:\n{str(e)}')
    
    def load_history(self):
        """Geçmişi dosyadan yükler"""
        # Varsayılan dosyayı otomatik yükle
        default_file = "sohbet_gecmisi.json"
        if os.path.exists(default_file):
            try:
                with open(default_file, 'r', encoding='utf-8') as f:
                    loaded_history = json.load(f)
                
                self.chat_display.clear()
                self.gecmis = loaded_history
                
                # Geçmişi ekranda göster
                for item in self.gecmis:
                    if item.get('kullanici'):
                        self.add_message("Sen", item['kullanici'])
                    if item.get('bot'):
                        self.add_message("Gemini", item['bot'], is_bot=True)
                
                if not self.gecmis:
                    self.add_message("🤖 Bot", "Merhaba! Ben Gemini AI. Size nasıl yardımcı olabilirim?", is_bot=True)
                
            except Exception as e:
                print(f"Yükleme hatası: {e}")
                self.add_message("🤖 Bot", "Merhaba! Ben Gemini AI. Size nasıl yardımcı olabilirim?", is_bot=True)
        else:
            self.add_message("🤖 Bot", "Merhaba! Ben Gemini AI. Size nasıl yardımcı olabilirim?", is_bot=True)
    
    def show_about(self):
        """Hakkında dialogunu gösterir"""
        QMessageBox.about(self, 'Hakkında', 
                         '🤖 Gemini AI Chat Bot\n\n'
                         'Google Gemini API kullanılarak yapılmış\n'
                         'modern bir sohbet uygulaması.\n\n'
                         '✨ Özellikler:\n'
                         '• Gerçek zamanlı AI sohbeti\n'
                         '• Sohbet geçmişi\n'
                         '• Modern dark tema\n'
                         '• Geçmiş kaydetme/yükleme\n\n'
                         'PyQt5 ile geliştirilmiştir.')
    
    def closeEvent(self, event):
        """Uygulama kapatılırken"""
        reply = QMessageBox.question(self, 'Çıkış', 
                                   'Çıkmadan önce sohbet geçmişini kaydetmek ister misiniz?',
                                   QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        
        if reply == QMessageBox.Yes:
            # Otomatik kaydet
            try:
                with open("sohbet_gecmisi.json", 'w', encoding='utf-8') as f:
                    json.dump(self.gecmis, f, ensure_ascii=False, indent=2)
                QMessageBox.information(self, 'Kaydedildi', 'Geçmiş otomatik kaydedildi!')
            except:
                pass
            event.accept()
        elif reply == QMessageBox.No:
            event.accept()
        else:
            event.ignore()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Gemini Chat Bot")
    
    # Uygulama ikonunu ayarla (varsa)
    try:
        app.setWindowIcon(QIcon('bot_icon.png'))
    except:
        pass
    
    window = GeminiChatGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 