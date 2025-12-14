import reflex as rx
from object_cheating.components.camera_feed import camera_feed
from object_cheating.components.camera_selector import camera_selector
from object_cheating.states.camera_state import CameraState

API_URL = "http://localhost:8001"


class StudentExamState(rx.State):
    """Öğrenci sınav sayfası durumu"""
    student_id: str = ""
    exam_code_in_state: str = ""
    exam_name: str = ""
    exam_url: str = ""
    exam_instructions: str = ""
    student_photo_url: str = ""
    error_message: str = ""
    is_loading: bool = False
    monitoring_started: bool = False

    def on_load(self):
        """Sayfa açıldığında sınav verilerini yükle"""
        import requests
        # Yol ve sorgudan parametreleri al
        self.exam_code_in_state = self.router.page.params.get("student_exam_code", "")
        self.student_id = self.router.page.params.get("student_id", "")
        
        if not self.exam_code_in_state or not self.student_id:
            self.error_message = "Geçersiz veriler - Lütfen tekrar giriş yapın"
            return
        
        self.is_loading = True
        self.error_message = ""
        try:
            # Sınav verilerini al
            exam_response = requests.get(f"{API_URL}/api/exams/{self.exam_code_in_state}/info", timeout=5)
            if exam_response.status_code == 200:
                exam_data = exam_response.json()
                self.exam_name = exam_data.get("name", "Sınav")
                self.exam_url = exam_data.get("url", "")
                self.exam_instructions = exam_data.get("instructions", "")
            else:
                self.exam_name = f"Sınav {self.exam_code_in_state}"
                self.exam_url = ""
                self.exam_instructions = ""
                
            # Öğrenci fotoğrafını al
            photo_response = requests.get(f"{API_URL}/api/students/{self.student_id}/photo", timeout=5)
            if photo_response.status_code == 200:
                photo_data = photo_response.json()
                self.student_photo_url = photo_data.get("photo_url", "")
            else:
                self.student_photo_url = ""
        except Exception as e:
            # Sunucu bağlı değilse, varsayılan verileri kullan
            self.exam_name = f"Sınav {self.exam_code_in_state}"
            self.exam_url = ""
            self.exam_instructions = ""
            self.student_photo_url = ""
        finally:
            self.is_loading = False
    
    async def start_monitoring(self):
        """Akıllı izlemeyi başlat"""
        self.monitoring_started = True
        # Kamerayı etkinleştir
        await CameraState.toggle_camera(self)
        # Otomatik algılamayı etkinleştir
        await CameraState.toggle_detection(self, True)


def student_exam_page() -> rx.Component:
    """Öğrenci sınav sayfası"""
    return rx.box(
        rx.el.div(
            # Header Section
            rx.el.div(
                rx.el.h1(
                    "🎓 Sınav Sayfası",
                    class_name="text-3xl font-bold text-blue-900 mb-2 text-center"
                ),
                rx.el.div(
                    rx.el.span(
                        f"Öğrenci: {StudentExamState.student_id}",
                        class_name="text-lg text-gray-700 mx-3"
                    ),
                    rx.el.span(
                        "•",
                        class_name="text-gray-400 mx-2"
                    ),
                    rx.el.span(
                        f"Sınav Kodu: {StudentExamState.exam_code_in_state}",
                        class_name="text-lg text-gray-700 mx-3"
                    ),
                    class_name="flex justify-center items-center mb-2"
                ),
                rx.el.h2(
                    StudentExamState.exam_name,
                    class_name="text-xl text-green-600 font-semibold text-center mb-4"
                ),
                class_name="mb-6"
            ),
            # Error Message
            rx.cond(
                StudentExamState.error_message != "",
                rx.el.div(
                    StudentExamState.error_message,
                    class_name="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg mb-4 text-center"
                ),
                rx.fragment()
            ),
            # Main Content Area
            rx.el.div(
                # Left Side - Camera Monitoring
                rx.el.div(
                    rx.el.h3(
                        "📹 Akıllı İzleme",
                        class_name="text-xl font-bold text-blue-900 mb-4"
                    ),
                    rx.cond(
                        StudentExamState.student_photo_url != "",
                        rx.el.div(
                            rx.el.img(
                                src=StudentExamState.student_photo_url,
                                class_name="w-24 h-24 rounded-full object-cover border-4 border-green-500 mx-auto mb-4"
                            ),
                            rx.el.p(
                                "Kayıtlı öğrenci fotoğrafı",
                                class_name="text-sm text-gray-600 text-center mb-4"
                            ),
                            class_name="mb-4"
                        ),
                        rx.fragment()
                    ),
                    # Camera selector component
                    camera_selector(),
                    # Camera feed
                    camera_feed(),
                    rx.cond(
                        StudentExamState.monitoring_started,
                        rx.el.div(
                            rx.el.div(
                                "✅ İzleme Aktif",
                                class_name="text-green-600 font-bold text-center mb-2"
                            ),
                            rx.el.p(
                                "Sistem, sınav dürüstlüğünü sağlamak için aktivitenizi izliyor",
                                class_name="text-sm text-gray-600 text-center"
                            ),
                            class_name="bg-green-50 border border-green-200 p-4 rounded-lg mt-4"
                        ),
                        rx.button(
                            "🚀 İzlemeyi ve Sınavı Başlat",
                            on_click=StudentExamState.start_monitoring,
                            class_name="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-4 px-6 rounded-lg mt-4 text-lg shadow-lg"
                        )
                    ),
                    class_name="bg-white p-6 rounded-lg shadow-lg"
                ),
                # Right Side - Exam Questions Area
                rx.el.div(
                    rx.el.h3(
                        "📝 Sınav Soruları",
                        class_name="text-xl font-bold text-blue-900 mb-4"
                    ),
                    rx.el.div(
                        rx.el.h4(
                            "⚠️ Önemli Talimatlar:",
                            class_name="font-bold text-gray-800 mb-3"
                        ),
                        rx.el.ul(
                            rx.el.li("✅ Kameranın önünde dik oturun", class_name="mb-2 text-sm"),
                            rx.el.li("✅ Doğrudan ekrana bakın", class_name="mb-2 text-sm"),
                            rx.el.li("✅ Ekrandan uzağa bakmayın", class_name="mb-2 text-sm"),
                            rx.el.li("✅ Telefon veya başka cihaz kullanmayın", class_name="mb-2 text-sm"),
                            rx.el.li("⚠️ Şüpheli davranışlar kaydedilecektir", class_name="text-sm text-red-600 font-bold"),
                            class_name="list-none text-gray-700"
                        ),
                        class_name="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-lg mb-6"
                    ),
                    # Exam Instructions
                    rx.cond(
                        StudentExamState.exam_instructions != "",
                        rx.el.div(
                            rx.el.h4(
                                "📌 Öğretmen Talimatları:",
                                class_name="font-bold text-gray-800 mb-2"
                            ),
                            rx.el.div(
                                StudentExamState.exam_instructions,
                                class_name="text-gray-700 whitespace-pre-wrap"
                            ),
                            class_name="bg-blue-50 border border-blue-200 p-4 rounded-lg mb-4"
                        ),
                        rx.fragment()
                    ),
                    
                    # Exam Content Area
                    rx.cond(
                        StudentExamState.monitoring_started,
                        # Show exam content when monitoring is active
                        rx.cond(
                            StudentExamState.exam_url != "",
                            # External exam link
                            rx.el.div(
                                rx.el.div(
                                    "🔗 Sınav Bağlantısı",
                                    class_name="text-xl font-bold text-gray-800 mb-4 text-center"
                                ),
                                rx.el.a(
                                    rx.button(
                                        "📝 Sınavı Yeni Pencerede Aç",
                                        class_name="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 px-6 rounded-lg text-lg shadow-lg"
                                    ),
                                    href=StudentExamState.exam_url,
                                    target="_blank",
                                    class_name="block mb-4"
                                ),
                                rx.el.div(
                                    rx.el.p(
                                        "⚠️ Not: Bu pencereyi kapatmayın - İzleme devam ediyor",
                                        class_name="text-red-600 font-bold text-center mb-2"
                                    ),
                                    rx.el.p(
                                        "Bağlantıyı ayrı bir pencerede açın ve bu pencereyi açık tutun",
                                        class_name="text-gray-600 text-center text-sm"
                                    ),
                                    class_name="bg-yellow-50 border border-yellow-300 p-4 rounded-lg"
                                ),
                                class_name="bg-white p-6 rounded-lg border-2 border-blue-300"
                            ),
                            # No exam link - placeholder
                            rx.el.div(
                                rx.el.div(
                                    "📚",
                                    class_name="text-6xl mb-4 text-center"
                                ),
                                rx.el.h4(
                                    "Soru Alanı",
                                    class_name="text-lg font-bold text-gray-700 mb-2 text-center"
                                ),
                                rx.el.p(
                                    "Öğretmen tarafından sınav bağlantısı eklenmedi",
                                    class_name="text-gray-600 text-center mb-4"
                                ),
                                rx.el.p(
                                    "Lütfen öğretmeninizle iletişime geçin",
                                    class_name="text-sm text-gray-500 text-center italic"
                                ),
                                class_name="bg-gray-50 p-8 rounded-lg border-2 border-dashed border-gray-300 text-center min-h-[300px] flex flex-col justify-center"
                            )
                        ),
                        # Before monitoring starts
                        rx.el.div(
                            rx.el.div(
                                "📚",
                                class_name="text-6xl mb-4 text-center"
                            ),
                            rx.el.h4(
                                "Soru Alanı",
                                class_name="text-lg font-bold text-gray-700 mb-2 text-center"
                            ),
                            rx.el.p(
                                "Sınav bağlantısı burada gösterilecek",
                                class_name="text-gray-600 text-center mb-4"
                            ),
                            rx.el.p(
                                "Sınava erişmek için önce izlemeyi başlatın",
                                class_name="text-sm text-gray-500 text-center italic"
                            ),
                            class_name="bg-gray-50 p-8 rounded-lg border-2 border-dashed border-gray-300 text-center min-h-[300px] flex flex-col justify-center"
                        )
                    ),
                    rx.el.div(
                        rx.el.div(
                            "⏱️ Kalan Süre: --:--",
                            class_name="text-lg font-bold text-gray-700"
                        ),
                        class_name="bg-blue-50 border border-blue-200 p-4 rounded-lg mt-4 text-center"
                    ),
                    class_name="bg-white p-6 rounded-lg shadow-lg"
                ),
                class_name="flex gap-4"
            ),
            class_name="max-w-7xl mx-auto px-4 py-8"
        ),
        on_mount=StudentExamState.on_load,
        class_name="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50"
    )