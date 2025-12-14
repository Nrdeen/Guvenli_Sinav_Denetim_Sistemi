import reflex as rx
import requests

API_URL = "http://localhost:8001"

class StudentsManagementState(rx.State):
    """Öğrenci yönetimi sayfası durumu"""

    # Student Management
    student_id: str = ""
    student_name: str = ""
    student_email: str = ""
    exam_code: str = ""

    # Messages
    success_message: str = ""
    error_message: str = ""

    # Student List
    students_list: list[dict] = []

    def on_load(self):
        """Sayfa açıldığında verileri yükle"""
        self.load_students()

    def load_students(self):
        """API'den öğrenci listesini yükle"""
        try:
            # جلب جميع الطلاب من قاعدة البيانات
            response = requests.get(
                f"{API_URL}/api/students/all",
                timeout=5
            )

            if response.status_code == 200:
                students_data = response.json()
                self.students_list = students_data
                if not students_data:
                    self.error_message = "Veritabanında öğrenci yok"
                    self.success_message = ""
                else:
                    self.success_message = f"✅ {len(students_data)} öğrenci yüklendi"
                    self.error_message = ""
            else:
                self.error_message = "Öğrenci listesi yüklenemedi"
                self.students_list = []
        except Exception as e:
            self.error_message = f"❌ Bağlantı hatası: {str(e)}"
            self.students_list = []

    def delete_student(self, student_id: str):
        """Öğrenciyi sil"""
        try:
            # إرسال طلب الحذف إلى API
            response = requests.delete(
                f"{API_URL}/api/students/{student_id}",
                timeout=5
            )

            if response.status_code == 200:
                # Öğrenciyi yerel listeden kaldır
                self.students_list = [s for s in self.students_list if s["id"] != student_id]
                self.success_message = f"✅ Öğrenci {student_id} başarıyla silindi"
                self.error_message = ""
            else:
                error_data = response.json()
                self.error_message = f"❌ {error_data.get('detail', 'Öğrenci silinemedi')}"
                self.success_message = ""
        except Exception as e:
            self.error_message = f"❌ Bağlantı hatası: {str(e)}"
            self.success_message = ""

    def add_student(self):
        """Yeni öğrenci ekle"""
        if not self.student_id or not self.student_name:
            self.error_message = "Lütfen öğrenci numarası ve adını doldurun"
            return

        # Yerel listede tekrar kontrolü
        if any(s["id"] == self.student_id.upper() for s in self.students_list):
            self.error_message = "Öğrenci numarası zaten listede mevcut"
            return

        try:
            # إرسال البيانات إلى API
            response = requests.post(
                f"{API_URL}/api/students",
                json={
                    "student_id": self.student_id.upper(),
                    "student_name": self.student_name,
                    "student_email": self.student_email if self.student_email else None,
                    "exam_code": self.exam_code.upper() if self.exam_code else None
                },
                timeout=5
            )

            if response.status_code == 200:
                response_data = response.json()

                # Öğrenciyi yerel listeye ekle
                new_student = {
                    "id": self.student_id.upper(),
                    "name": self.student_name,
                    "email": self.student_email or f"{self.student_id}@example.com",
                    "exam_code": self.exam_code.upper() if self.exam_code else "Belirtilmemiş"
                }

                # Listede yoksa güncelle
                if not any(s["id"] == new_student["id"] for s in self.students_list):
                    self.students_list.append(new_student)

                self.success_message = f"✅ {response_data.get('message', 'Öğrenci başarıyla eklendi')}"
                self.error_message = ""

                # Alanları temizle
                self.student_id = ""
                self.student_name = ""
                self.student_email = ""
                self.exam_code = ""

                # Sunucudan listeyi yeniden yükle
                self.load_students()
            else:
                error_data = response.json()
                self.error_message = f"❌ {error_data.get('detail', 'Öğrenci eklenirken hata oluştu')}"
                self.success_message = ""
        except Exception as e:
            self.error_message = f"❌ Sunucu bağlantı hatası: {str(e)}"
            self.success_message = ""

def students_management_page() -> rx.Component:
    """Öğrenci yönetimi sayfası"""
    return rx.box(
        rx.el.div(
            # Header with back button
            rx.el.div(
                rx.link(
                    rx.button(
                        "← Kontrol Paneline Dön",
                        class_name="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg mb-4"
                    ),
                    href="/admin/dashboard"
                ),
                rx.el.h1(
                    "👥 Öğrenci Yönetimi",
                    class_name="text-3xl font-bold text-blue-900 mb-2 text-center"
                ),
                rx.el.p(
                    "Sistemden öğrenci ekle ve sil",
                    class_name="text-gray-600 text-center mb-8"
                ),
                class_name="mb-8"
            ),

            # Success/Error Messages
            rx.cond(
                StudentsManagementState.success_message != "",
                rx.el.div(
                    StudentsManagementState.success_message,
                    class_name="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-lg mb-6 text-center"
                ),
                rx.fragment()
            ),
            rx.cond(
                StudentsManagementState.error_message != "",
                rx.el.div(
                    StudentsManagementState.error_message,
                    class_name="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg mb-6 text-center"
                ),
                rx.fragment()
            ),

            # Main Content
            rx.el.div(
                # Add Student Form
                rx.el.div(
                    rx.el.h2("➕ Yeni Öğrenci Ekle", class_name="text-2xl font-bold mb-6 text-blue-900"),
                    rx.el.div(
                        # Student ID
                        rx.el.div(
                            rx.el.label("Öğrenci Numarası *", class_name="block text-gray-700 font-bold mb-2"),
                            rx.el.input(
                                type="text",
                                placeholder="Örnek: STU001",
                                value=StudentsManagementState.student_id,
                                on_change=StudentsManagementState.set_student_id,
                                class_name="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 uppercase"
                            ),
                            class_name="mb-4"
                        ),

                        # Student Name
                        rx.el.div(
                            rx.el.label("Öğrenci Adı *", class_name="block text-gray-700 font-bold mb-2"),
                            rx.el.input(
                                type="text",
                                placeholder="Örnek: Ahmet Yılmaz",
                                value=StudentsManagementState.student_name,
                                on_change=StudentsManagementState.set_student_name,
                                class_name="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                            ),
                            class_name="mb-4"
                        ),

                        # Student Email
                        rx.el.div(
                            rx.el.label("E-posta (opsiyonel)", class_name="block text-gray-700 font-bold mb-2"),
                            rx.el.input(
                                type="email",
                                placeholder="ogrenci@example.com",
                                value=StudentsManagementState.student_email,
                                on_change=StudentsManagementState.set_student_email,
                                class_name="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                            ),
                            class_name="mb-4"
                        ),

                        # Exam Code
                        rx.el.div(
                            rx.el.label("Sınav Kodu (opsiyonel)", class_name="block text-gray-700 font-bold mb-2"),
                            rx.el.input(
                                type="text",
                                placeholder="Örnek: PROG2025",
                                value=StudentsManagementState.exam_code,
                                on_change=StudentsManagementState.set_exam_code,
                                class_name="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 uppercase"
                            ),
                            rx.el.p(
                                "Genel sisteme eklemek için boş bırakın",
                                class_name="text-sm text-gray-500 mt-1"
                            ),
                            class_name="mb-6"
                        ),

                        # Add Button
                        rx.button(
                            "➕ Öğrenci Ekle",
                            on_click=StudentsManagementState.add_student,
                            class_name="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg text-lg shadow-lg"
                        ),

                        class_name="bg-white p-8 rounded-lg shadow-lg max-w-2xl mx-auto"
                    ),
                    class_name="mb-8"
                ),

                # Students List
                rx.el.div(
                    rx.el.div(
                        rx.el.h2("📋 Kayıtlı Öğrenci Listesi", class_name="text-2xl font-bold mb-6 text-blue-900"),
                        rx.button(
                            "🔄 Listeyi Yenile",
                            on_click=StudentsManagementState.load_students,
                            class_name="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg mb-4"
                        ),
                        class_name="flex justify-between items-center mb-6"
                    ),

                    rx.cond(
                        StudentsManagementState.students_list.length() > 0,
                        rx.el.div(
                            rx.el.table(
                                rx.el.thead(
                                    rx.el.tr(
                                        rx.el.th("Öğrenci No", class_name="px-4 py-3 text-right text-gray-700 font-bold bg-gray-100"),
                                        rx.el.th("Ad", class_name="px-4 py-3 text-right text-gray-700 font-bold bg-gray-100"),
                                        rx.el.th("E-posta", class_name="px-4 py-3 text-right text-gray-700 font-bold bg-gray-100"),
                                        rx.el.th("Sınav Kodu", class_name="px-4 py-3 text-right text-gray-700 font-bold bg-gray-100"),
                                        rx.el.th("İşlemler", class_name="px-4 py-3 text-center text-gray-700 font-bold bg-gray-100"),
                                        class_name="border-b-2 border-gray-200"
                                    )
                                ),
                                rx.el.tbody(
                                    rx.foreach(
                                        StudentsManagementState.students_list,
                                        lambda student: rx.el.tr(
                                            rx.el.td(student["id"], class_name="px-4 py-3 border-t font-mono text-gray-800"),
                                            rx.el.td(student["name"], class_name="px-4 py-3 border-t text-gray-800"),
                                            rx.el.td(student["email"], class_name="px-4 py-3 border-t text-sm text-gray-600"),
                                            rx.el.td(student["exam_code"], class_name="px-4 py-3 border-t font-mono text-blue-600"),
                                            rx.el.td(
                                                rx.button(
                                                    "🗑️ Sil",
                                                    on_click=lambda: StudentsManagementState.delete_student(student["id"]),
                                                    class_name="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm shadow-sm"
                                                ),
                                                class_name="px-4 py-3 border-t text-center"
                                            ),
                                            class_name="hover:bg-gray-50 transition-colors"
                                        )
                                    )
                                ),
                                class_name="w-full bg-white shadow-sm rounded-lg overflow-hidden"
                            ),
                            class_name="overflow-x-auto"
                        ),
                        rx.el.div(
                            rx.el.div(
                                "📝",
                                class_name="text-6xl mb-4 text-center text-gray-400"
                            ),
                            rx.el.p(
                                "Şu anda kayıtlı öğrenci yok",
                                class_name="text-gray-600 text-center text-lg mb-2"
                            ),
                            rx.el.p(
                                "Yeni öğrenci eklemek için yukarıdaki formu kullanın",
                                class_name="text-gray-500 text-center text-sm"
                            ),
                            class_name="bg-gray-50 p-12 rounded-lg border-2 border-dashed border-gray-300 text-center"
                        )
                    ),
                    class_name="bg-white p-6 rounded-lg shadow-md"
                ),
                class_name="max-w-6xl mx-auto px-4"
            ),
            class_name="max-w-7xl mx-auto px-4 py-8"
        ),
        on_mount=StudentsManagementState.on_load,
        class_name="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50"
    )