import reflex as rx

class DashboardState(rx.State):
    """State for Dashboard."""
    # Stats
    total_students: int = 0
    active_sessions: int = 0
    total_violations: int = 0
    
    # System Status
    camera_status: str = "Hazır"
    ai_detection_status: str = "Hazır"
    recording_status: str = "Hazır"
    
    # Detection Metrics
    face_detection_count: int = 0
    eye_movement_count: int = 0
    mouth_movement_count: int = 0
    multi_face_count: int = 0
    object_detection_count: int = 0
    audio_detection_count: int = 0

def dashboard_page() -> rx.Component:
    """Dashboard page for Güvenli Sınav system - EduView Style."""
    return rx.box(
        # Header
        rx.el.div(
            rx.link(
                rx.button(
                    "← Ana Sayfaya Dön",
                    class_name="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg mb-4"
                ),
                href="/"
            ),
            rx.el.h1(
                "Güvenli Sınav İzleme Paneli",
                class_name="text-3xl font-bold text-blue-900 mb-8 text-center"
            ),
            class_name="max-w-7xl mx-auto px-4 py-8"
        ),
        
        # Main Content
        rx.el.div(
            # Left Section - Main Dashboard
            rx.el.div(
                # Live Monitoring Card
                rx.el.div(
                    rx.el.h3("Canlı İzleme", class_name="text-lg font-semibold mb-4 text-blue-900"),
                    rx.el.div(
                        rx.el.div(
                            "Kamera Görünümü",
                            class_name="w-full h-64 bg-gray-800 rounded-lg flex items-center justify-center text-gray-400 text-xl"
                        ),
                        class_name="mb-4"
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.span("📊 FPS: ", class_name="font-medium text-gray-700"),
                            rx.el.span("30", class_name="ml-2"),
                            class_name="mb-2"
                        ),
                        rx.el.div(
                            rx.el.span("⏱️ Çalışma Süresi: ", class_name="font-medium text-gray-700"),
                            rx.el.span("0s", class_name="ml-2"),
                            class_name="mb-2"
                        ),
                        rx.el.div(
                            rx.el.span("👥 Tespit Edilen: ", class_name="font-medium text-gray-700"),
                            rx.el.span("0", class_name="ml-2"),
                            class_name="mb-2"
                        ),
                    ),
                    class_name="bg-white p-4 rounded-lg shadow-md mb-4 border border-blue-200"
                ),
                
                # Violation Log Table
                rx.el.div(
                    rx.el.h3("İhlal Kaydı", class_name="text-lg font-semibold mb-4 text-blue-900"),
                    rx.el.table(
                        rx.el.thead(
                            rx.el.tr(
                                rx.el.th("No", class_name="px-4 py-2 text-left"),
                                rx.el.th("Zaman", class_name="px-4 py-2 text-left"),
                                rx.el.th("İhlal Türü", class_name="px-4 py-2 text-left"),
                                rx.el.th("Detay", class_name="px-4 py-2 text-left"),
                                class_name="bg-blue-100"
                            )
                        ),
                        rx.el.tbody(
                            rx.el.tr(
                                rx.el.td(
                                    "Henüz ihlal kaydı bulunmuyor",
                                    class_name="px-4 py-8 text-center text-gray-500",
                                    col_span="4"
                                )
                            )
                        ),
                        class_name="w-full border-collapse"
                    ),
                    class_name="bg-white p-4 rounded-lg shadow-md border border-blue-200"
                ),
                
                class_name="w-2/3 pr-4 space-y-4"
            ),
            
            # Right Section - Settings & Stats
            rx.el.div(
                # Detection Settings
                rx.el.div(
                    rx.el.h3("Algılama Ayarları", class_name="text-lg font-semibold mb-2 text-blue-900"),
                    rx.el.div(
                        rx.el.div(
                            rx.text("Güven Eşiği:", class_name="font-medium text-gray-700"),
                            rx.el.div(
                                rx.el.input(
                                    value="0.25",
                                    type="number",
                                    class_name="w-20 px-2 py-1 border rounded text-center"
                                ),
                                class_name="flex items-center gap-2"
                            ),
                            class_name="flex justify-between items-center mb-3"
                        ),
                        rx.el.div(
                            rx.text("IoU Eşiği:", class_name="font-medium text-gray-700"),
                            rx.el.div(
                                rx.el.input(
                                    value="0.7",
                                    type="number",
                                    class_name="w-20 px-2 py-1 border rounded text-center"
                                ),
                                class_name="flex items-center gap-2"
                            ),
                            class_name="flex justify-between items-center"
                        ),
                    ),
                    class_name="bg-white p-4 rounded-lg shadow-md mb-4 border border-blue-200"
                ),
                
                # Detection Summary
                rx.el.div(
                    rx.el.h3("Algılama Özeti", class_name="text-lg font-semibold mb-2 text-blue-900"),
                    rx.el.div(
                        rx.el.div(
                            rx.el.span("👤 Yüz Tespiti:", class_name="text-gray-700"),
                            rx.el.span(f"{DashboardState.face_detection_count}", class_name="ml-2 font-bold"),
                            class_name="flex justify-between mb-2"
                        ),
                        rx.el.div(
                            rx.el.span("👁️ Göz Hareketi:", class_name="text-gray-700"),
                            rx.el.span(f"{DashboardState.eye_movement_count}", class_name="ml-2 font-bold"),
                            class_name="flex justify-between mb-2"
                        ),
                        rx.el.div(
                            rx.el.span("👄 Ağız Hareketi:", class_name="text-gray-700"),
                            rx.el.span(f"{DashboardState.mouth_movement_count}", class_name="ml-2 font-bold"),
                            class_name="flex justify-between mb-2"
                        ),
                        rx.el.div(
                            rx.el.span("👥 Çoklu Yüz:", class_name="text-gray-700"),
                            rx.el.span(f"{DashboardState.multi_face_count}", class_name="ml-2 font-bold text-red-600"),
                            class_name="flex justify-between mb-2"
                        ),
                        rx.el.div(
                            rx.el.span("📱 Nesne Tespiti:", class_name="text-gray-700"),
                            rx.el.span(f"{DashboardState.object_detection_count}", class_name="ml-2 font-bold text-red-600"),
                            class_name="flex justify-between mb-2"
                        ),
                        rx.el.div(
                            rx.el.span("🎤 Ses Tespiti:", class_name="text-gray-700"),
                            rx.el.span(f"{DashboardState.audio_detection_count}", class_name="ml-2 font-bold text-red-600"),
                            class_name="flex justify-between"
                        ),
                    ),
                    class_name="bg-white p-4 rounded-lg shadow-md mb-4 border border-blue-200"
                ),
                
                # System Status
                rx.el.div(
                    rx.el.h3("Sistem Durumu", class_name="text-lg font-semibold mb-2 text-blue-900"),
                    rx.el.div(
                        rx.el.div(
                            rx.el.span("🟢", class_name="text-2xl mr-2"),
                            rx.el.span(f"Kamera: {DashboardState.camera_status}", class_name="text-green-600"),
                            class_name="mb-2"
                        ),
                        rx.el.div(
                            rx.el.span("🟢", class_name="text-2xl mr-2"),
                            rx.el.span(f"AI Algılama: {DashboardState.ai_detection_status}", class_name="text-green-600"),
                            class_name="mb-2"
                        ),
                        rx.el.div(
                            rx.el.span("🟢", class_name="text-2xl mr-2"),
                            rx.el.span(f"Kayıt: {DashboardState.recording_status}", class_name="text-green-600"),
                            class_name="mb-2"
                        ),
                    ),
                    class_name="bg-white p-4 rounded-lg shadow-md mb-4 border border-blue-200"
                ),
                
                # Control Buttons
                rx.el.div(
                    rx.el.h3("Kontroller", class_name="text-lg font-semibold mb-2 text-blue-900"),
                    rx.el.div(
                        rx.button(
                            "▶️ Başlat",
                            class_name="bg-green-500 hover:bg-green-600 text-white px-6 py-2 rounded-lg w-full mb-2"
                        ),
                        rx.button(
                            "⏸️ Duraklat",
                            class_name="bg-yellow-500 hover:bg-yellow-600 text-white px-6 py-2 rounded-lg w-full mb-2"
                        ),
                        rx.button(
                            "💾 Rapor Oluştur",
                            class_name="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg w-full mb-2"
                        ),
                        rx.button(
                            "🗑️ Temizle",
                            class_name="bg-red-500 hover:bg-red-600 text-white px-6 py-2 rounded-lg w-full"
                        ),
                    ),
                    class_name="bg-white p-4 rounded-lg shadow-md border border-blue-200"
                ),
                
                class_name="w-1/3 space-y-4"
            ),
            
            class_name="flex max-w-7xl mx-auto px-4"
        ),
        
        class_name="min-h-screen bg-gradient-to-br from-blue-50 to-white"
    )
