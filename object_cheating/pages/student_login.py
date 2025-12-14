import reflex as rx
import requests

API_URL = "http://localhost:8001"

class StudentLoginState(rx.State):
    """Öğrenci giriş durumu"""
    student_id: str = ""
    login_exam_code: str = ""
    student_name: str = ""
    error_message: str = ""
    is_loading: bool = False
    
    def set_student_id(self, value: str):
        self.student_id = value.upper()
    
    def set_exam_code(self, value: str):
        self.login_exam_code = value.upper()
    
    def login(self):
        """Öğrenci girişi ve doğrulama"""
        if not self.student_id or not self.login_exam_code:
            self.error_message = "Lütfen öğrenci numarası ve sınav kodunu girin"
            return
        
        self.is_loading = True
        self.error_message = ""
        
        try:
            # Sınavın varlığını kontrol et
            exam_response = requests.get(f"{API_URL}/api/exams/{self.login_exam_code}/info", timeout=5)
            if exam_response.status_code != 200:
                self.error_message = "Sınav kodu geçersiz"
                return
            
            # Öğrencinin sınava kayıtlı olup olmadığını kontrol et
            students_response = requests.get(f"{API_URL}/api/exams/{self.login_exam_code}/registered-students", timeout=5)
            if students_response.status_code == 200:
                registered_students = students_response.json()
                student_ids = [s['student_id'] for s in registered_students]
                
                if self.student_id not in student_ids:
                    self.error_message = "Bu sınava kayıtlı değilsiniz. Lütfen öğretmeninizle iletişime geçin"
                    return
            
            # Öğrenci verilerini al
            student_response = requests.get(f"{API_URL}/api/students/{self.student_id}", timeout=5)
            if student_response.status_code == 200:
                student_data = student_response.json()
                self.student_name = student_data.get('full_name', f'Öğrenci {self.student_id}')
            else:
                self.student_name = f'Öğrenci {self.student_id}'
            
            # Sınav sayfasına yönlendir
            return rx.redirect(f"/exam/{self.login_exam_code}?student_id={self.student_id}")
            
        except Exception as e:
            # Backend çalışmıyorsa, test için girişe izin ver
            self.error_message = f"⚠️ Bağlantı hatası: {str(e)}"
            return rx.redirect(f"/exam/{self.login_exam_code}?student_id={self.student_id}")
        finally:
            self.is_loading = False


def student_login_page() -> rx.Component:
    """Öğrenci giriş sayfası"""
    return rx.box(
        rx.el.div(
            rx.el.div(
                # Back Button
                rx.link(
                    rx.button(
                        "← Ana Sayfaya Dön",
                        class_name="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg mb-4"
                    ),
                    href="/"
                ),
                
                rx.el.h1(
                    "Öğrenci Girişi",
                    class_name="text-3xl font-bold text-blue-900 mb-8 text-center"
                ),
                
                # Login Card
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.div("🎓", class_name="text-6xl mb-4"),
                            rx.el.h2(
                                "Sınava Hoş Geldiniz",
                                class_name="text-2xl font-bold text-blue-900 mb-2"
                            ),
                            rx.el.p(
                                "Başlamak için bilgilerinizi girin",
                                class_name="text-gray-600 mb-6"
                            ),
                            class_name="text-center"
                        ),
                        
                        # Error Message
                        rx.cond(
                            StudentLoginState.error_message != "",
                            rx.el.div(
                                StudentLoginState.error_message,
                                class_name="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4 text-center"
                            ),
                            rx.fragment()
                        ),
                        
                        # Student ID Input
                        rx.el.div(
                            rx.el.label(
                                "Öğrenci Numarası / Student ID",
                                class_name="block text-gray-700 font-bold mb-2 text-center"
                            ),
                            rx.el.input(
                                type="text",
                                placeholder="ST11",
                                value=StudentLoginState.student_id,
                                on_change=StudentLoginState.set_student_id,
                                class_name="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 text-center font-mono text-lg uppercase"
                            ),
                            rx.el.p(
                                "Örnek: STU001, STU002, STU003",
                                class_name="text-sm text-gray-500 mt-1 text-center"
                            ),
                            class_name="mb-6"
                        ),
                        
                        # Exam Code Input
                        rx.el.div(
                            rx.el.label(
                                "Sınav Kodu / Exam Code",
                                class_name="block text-gray-700 font-bold mb-2 text-center"
                            ),
                            rx.el.input(
                                type="text",
                                placeholder="ASM209",
                                value=StudentLoginState.login_exam_code,
                                on_change=StudentLoginState.set_exam_code,
                                class_name="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 text-center font-mono text-lg uppercase"
                            ),
                            rx.el.p(
                                "Sınav kodunu öğretmeninizden alın",
                                class_name="text-sm text-gray-500 mt-1 text-center"
                            ),
                            class_name="mb-6"
                        ),
                        
                        # Login Button
                        rx.button(
                            rx.cond(
                                StudentLoginState.is_loading,
                                "⏳ Doğrulanıyor...",
                                "Sınava Giriş →"
                            ),
                            on_click=StudentLoginState.login,
                            disabled=StudentLoginState.is_loading,
                            class_name="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-bold py-4 px-4 rounded-lg text-lg shadow-lg"
                        ),
                        
                        # Important Notes
                        rx.el.div(
                            rx.el.h3(
                                "⚠️ Önemli Talimatlar:",
                                class_name="font-bold text-gray-800 mb-3"
                            ),
                            rx.el.ul(
                                rx.el.li("✅ Kameranın açık olduğundan emin olun", class_name="mb-2 text-sm"),
                                rx.el.li("✅ Sessiz ve iyi aydınlatılmış bir yerde oturun", class_name="mb-2 text-sm"),
                                rx.el.li("✅ Sınav sayfasından ayrılmayın", class_name="mb-2 text-sm"),
                                rx.el.li("✅ Sistem tüm kopya girişimlerini izler", class_name="mb-2 text-sm"),
                                rx.el.li("⚠️ Tüm ihlaller kaydedilecektir", class_name="text-sm text-red-600 font-bold"),
                                class_name="list-none text-gray-700"
                            ),
                            class_name="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-lg mt-6"
                        ),
                        
                        class_name="bg-white p-8 rounded-lg shadow-lg max-w-md w-full"
                    ),
                    class_name="flex justify-center items-center min-h-[70vh]"
                ),
                
                class_name="max-w-4xl mx-auto px-4 py-8"
            ),
            class_name="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50"
        )
    )
