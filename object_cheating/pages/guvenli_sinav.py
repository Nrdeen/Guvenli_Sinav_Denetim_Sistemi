import reflex as rx
import subprocess
import os

class GuvenliSinavState(rx.State):
    """State for Güvenli Sınav system."""
    is_running: bool = False
    status_message: str = "Sistem çalışmıyor"
    
    def start_system(self):
        """Start the Güvenli Sınav system and redirect to dashboard."""
        try:
            # Path to the system
            system_path = os.path.join(os.getcwd(), "Güvenli Sınav Denetim Sistemi")
            
            # Check if START.bat exists
            start_bat = os.path.join(system_path, "START.bat")
            
            if os.path.exists(start_bat):
                # Run the system in background
                subprocess.Popen([start_bat], cwd=system_path, shell=True)
                self.is_running = True
                # Redirect to dashboard
                return rx.redirect("/dashboard")
            else:
                self.status_message = "Hata: START.bat dosyası bulunamadı"
        except Exception as e:
            self.status_message = f"Başlatma hatası: {str(e)}"

def guvenli_sinav_page() -> rx.Component:
    return rx.box(
        rx.vstack(
            # Header
            rx.el.div(
                rx.link(
                    rx.button(
                        "← Ana Sayfaya Dön",
                        class_name="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg"
                    ),
                    href="/"
                ),
                class_name="w-full mb-4"
            ),
            
            rx.el.h1(
                "Güvenli Sınav Denetim Sistemi",
                class_name="text-3xl font-bold text-blue-900 mb-8 text-center"
            ),
            
            # Instructions Card
            rx.el.div(
                rx.el.h2(
                    "Nasıl Kullanılır:",
                    class_name="text-2xl font-bold mb-4 text-blue-900"
                ),
                rx.el.ol(
                    rx.el.li("Aşağıdaki 'Sistemi Başlat' düğmesine tıklayın", class_name="mb-3 text-gray-700"),
                    rx.el.li("Güvenli sınav sistemi için yeni bir pencere açılacak", class_name="mb-3 text-gray-700"),
                    rx.el.li("Yeni penceredeki talimatları izleyin", class_name="mb-3 text-gray-700"),
                    rx.el.li("Raporlar otomatik olarak 'reports' klasörüne kaydedilecek", class_name="mb-3 text-gray-700"),
                    class_name="list-decimal list-inside"
                ),
                class_name="bg-blue-50 p-6 rounded-lg mb-8 max-w-2xl border border-blue-200"
            ),
            
            # Features Card
            rx.el.div(
                rx.el.h3(
                    "Özellikler:",
                    class_name="text-xl font-bold mb-4 text-blue-900"
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.span("👤 ", class_name="text-2xl"),
                        rx.el.span("Yüz ve göz tespiti", class_name="text-gray-700"),
                        class_name="mb-3"
                    ),
                    rx.el.div(
                        rx.el.span("👁️ ", class_name="text-2xl"),
                        rx.el.span("Göz hareketi takibi", class_name="text-gray-700"),
                        class_name="mb-3"
                    ),
                    rx.el.div(
                        rx.el.span("🖥️ ", class_name="text-2xl"),
                        rx.el.span("Ekran kaydı", class_name="text-gray-700"),
                        class_name="mb-3"
                    ),
                    rx.el.div(
                        rx.el.span("🎤 ", class_name="text-2xl"),
                        rx.el.span("Ses tespiti", class_name="text-gray-700"),
                        class_name="mb-3"
                    ),
                    rx.el.div(
                        rx.el.span("📱 ", class_name="text-2xl"),
                        rx.el.span("Yasak nesne tespiti", class_name="text-gray-700"),
                        class_name="mb-3"
                    ),
                    rx.el.div(
                        rx.el.span("📊 ", class_name="text-2xl"),
                        rx.el.span("Detaylı PDF/HTML raporları", class_name="text-gray-700"),
                        class_name="mb-3"
                    ),
                    class_name="grid grid-cols-2 gap-4"
                ),
                class_name="bg-blue-50 p-6 rounded-lg mb-8 max-w-2xl border border-blue-200"
            ),
            
            # Start Button
            rx.button(
                "🚀 Güvenli Sınavı Başlat",
                on_click=GuvenliSinavState.start_system,
                class_name="bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 px-12 rounded-lg shadow-xl text-xl mb-4"
            ),
            
            # Status Message
            rx.cond(
                GuvenliSinavState.status_message != "",
                rx.el.div(
                    rx.text(GuvenliSinavState.status_message),
                    class_name="bg-blue-100 border-l-4 border-blue-500 text-blue-700 p-4 rounded mt-4 max-w-2xl"
                ),
            ),
            
            # Note
            rx.el.div(
                rx.el.p(
                    "💡 Not: 'Güvenli Sınav Denetim Sistemi' klasöründeki tüm gereksinimlerin yüklü olduğundan emin olun",
                    class_name="text-gray-600 text-sm"
                ),
                class_name="mt-8 text-center"
            ),
            
            spacing="4",
            align="center",
            class_name="min-h-screen py-12"
        ),
        class_name="min-h-screen bg-gradient-to-br from-blue-50 to-white"
    )
