import reflex as rx
import requests
from datetime import datetime
from typing import List, Dict

API_URL = "http://localhost:8000"  # عنوان Backend API
EXAM_CODE = "PROG2025"  # رمز الاختبار الافتراضي

class GuvenliDashboardState(rx.State):
    """State for Güvenli Sınav Dashboard - Multi-Student Monitoring"""
    
    # Exam info
    exam_code: str = EXAM_CODE
    exam_name: str = "Loading..."
    is_loading: bool = False
    error_message: str = ""
    
    # Students list
    students: List[Dict] = []
    total_students: int = 0
    active_students: int = 0
    total_all_violations: int = 0
    
    # Auto-refresh
    auto_refresh: bool = True
    last_update: str = "لم يتم التحديث بعد"
    
    def load_exam_info(self):
        """تحميل معلومات الاختبار"""
        try:
            response = requests.get(f"{API_URL}/api/exams/{self.exam_code}/info", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.exam_name = data.get("exam_name", "")
                self.error_message = ""
            else:
                self.error_message = "فشل تحميل معلومات الاختبار - تأكد من تشغيل Backend"
        except Exception as e:
            self.error_message = f"خطأ في الاتصال بالخادم: {str(e)}"
            self.exam_name = "غير متصل"
    
    def load_students(self):
        """تحميل قائمة الطلاب وحالتهم"""
        self.is_loading = True
        try:
            response = requests.get(f"{API_URL}/api/exams/{self.exam_code}/students", timeout=5)
            if response.status_code == 200:
                self.students = response.json()
                self.total_students = len(self.students)
                self.active_students = sum(1 for s in self.students if s.get("is_active", False))
                self.total_all_violations = sum(s.get("total_violations", 0) for s in self.students)
                self.last_update = datetime.now().strftime("%H:%M:%S")
                self.error_message = ""
            else:
                self.error_message = "فشل تحميل بيانات الطلاب"
        except Exception as e:
            self.error_message = f"خطأ في الاتصال: {str(e)}"
        finally:
            self.is_loading = False
    
    def refresh_data(self):
        """تحديث البيانات يدوياً"""
        self.load_exam_info()
        self.load_students()


def live_dashboard() -> rx.Component:
    """لوحة تحكم مباشرة لمراقبة جميع الطلاب"""
    return rx.box(
        rx.el.div(
            # Header
            rx.el.div(
                rx.link(
                    rx.button(
                        "← العودة للرئيسية",
                        class_name="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg mb-4"
                    ),
                    href="/"
                ),
                rx.el.h1(
                    "لوحة المراقبة المباشرة - Güvenli Sınav",
                    class_name="text-3xl font-bold text-gray-800 mb-2 text-center"
                ),
                rx.el.div(
                    rx.el.span(f"الاختبار: ", class_name="font-semibold"),
                    rx.el.span(GuvenliDashboardState.exam_name, class_name="text-blue-600"),
                    rx.el.span(f" ({GuvenliDashboardState.exam_code})", class_name="text-gray-500 ml-2"),
                    class_name="text-center mb-4"
                ),
                class_name="max-w-7xl mx-auto px-4 py-8"
            ),
            
            # Error Message
            rx.cond(
                GuvenliDashboardState.error_message != "",
                rx.el.div(
                    rx.el.div(
                        "⚠️ ",
                        GuvenliDashboardState.error_message,
                        class_name="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded text-center"
                    ),
                    class_name="max-w-7xl mx-auto px-4 mb-4"
                ),
                rx.fragment()
            ),
            
            # Stats Summary
            rx.el.div(
                rx.el.div(
                    # Stat Card 1
                    rx.el.div(
                        rx.el.div(
                            rx.el.div("👥", class_name="text-4xl mb-2"),
                            rx.el.div(
                                GuvenliDashboardState.total_students.to_string(),
                                class_name="text-3xl font-bold text-gray-800"
                            ),
                            rx.el.div("إجمالي الطلاب", class_name="text-gray-600"),
                            class_name="text-center"
                        ),
                        class_name="bg-[#ffec99] p-6 rounded-lg shadow-md"
                    ),
                    
                    # Stat Card 2
                    rx.el.div(
                        rx.el.div(
                            rx.el.div("🟢", class_name="text-4xl mb-2"),
                            rx.el.div(
                                GuvenliDashboardState.active_students.to_string(),
                                class_name="text-3xl font-bold text-green-600"
                            ),
                            rx.el.div("طلاب نشطون", class_name="text-gray-600"),
                            class_name="text-center"
                        ),
                        class_name="bg-green-50 p-6 rounded-lg shadow-md"
                    ),
                    
                    # Stat Card 3
                    rx.el.div(
                        rx.el.div(
                            rx.el.div("🚨", class_name="text-4xl mb-2"),
                            rx.el.div(
                                GuvenliDashboardState.total_all_violations.to_string(),
                                class_name="text-3xl font-bold text-red-600"
                            ),
                            rx.el.div("إجمالي الانتهاكات", class_name="text-gray-600"),
                            class_name="text-center"
                        ),
                        class_name="bg-red-50 p-6 rounded-lg shadow-md"
                    ),
                    
                    # Stat Card 4
                    rx.el.div(
                        rx.el.div(
                            rx.el.div("🕐", class_name="text-4xl mb-2"),
                            rx.el.div(
                                GuvenliDashboardState.last_update,
                                class_name="text-xl font-bold text-gray-800"
                            ),
                            rx.el.div("آخر تحديث", class_name="text-gray-600"),
                            class_name="text-center"
                        ),
                        class_name="bg-blue-50 p-6 rounded-lg shadow-md"
                    ),
                    
                    class_name="grid grid-cols-4 gap-4 mb-6"
                ),
                class_name="max-w-7xl mx-auto px-4"
            ),
            
            # Control Buttons
            rx.el.div(
                rx.el.div(
                    rx.button(
                        "🔄 تحديث البيانات",
                        on_click=GuvenliDashboardState.refresh_data,
                        class_name="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg mr-2"
                    ),
                    rx.button(
                        "📊 تحميل معلومات الاختبار",
                        on_click=GuvenliDashboardState.load_exam_info,
                        class_name="bg-green-500 hover:bg-green-600 text-white px-6 py-2 rounded-lg mr-2"
                    ),
                    rx.button(
                        "👥 تحديث قائمة الطلاب",
                        on_click=GuvenliDashboardState.load_students,
                        class_name="bg-purple-500 hover:bg-purple-600 text-white px-6 py-2 rounded-lg"
                    ),
                    class_name="flex justify-center mb-6"
                ),
                class_name="max-w-7xl mx-auto px-4"
            ),
            
            # Students Table
            rx.el.div(
                rx.el.div(
                    rx.el.h2("📋 قائمة الطلاب والمراقبة المباشرة", class_name="text-2xl font-bold mb-4 text-gray-800"),
                    
                    rx.cond(
                        GuvenliDashboardState.is_loading,
                        rx.el.div(
                            "⏳ جاري تحميل البيانات...",
                            class_name="text-center py-12 text-gray-500 text-xl"
                        ),
                        rx.cond(
                            GuvenliDashboardState.students.length() > 0,
                            rx.el.div(
                                rx.el.table(
                                    # Table Header
                                    rx.el.thead(
                                        rx.el.tr(
                                            rx.el.th("الحالة", class_name="px-4 py-3 text-center bg-yellow-200 font-bold"),
                                            rx.el.th("رقم الطالب", class_name="px-4 py-3 text-right bg-yellow-200 font-bold"),
                                            rx.el.th("الاسم", class_name="px-4 py-3 text-right bg-yellow-200 font-bold"),
                                            rx.el.th("إجمالي", class_name="px-4 py-3 text-center bg-red-100 font-bold text-red-700"),
                                            rx.el.th("👤 وجه", class_name="px-4 py-3 text-center bg-gray-100 font-bold text-xs"),
                                            rx.el.th("👁️ عين", class_name="px-4 py-3 text-center bg-gray-100 font-bold text-xs"),
                                            rx.el.th("👄 فم", class_name="px-4 py-3 text-center bg-gray-100 font-bold text-xs"),
                                            rx.el.th("👥 متعدد", class_name="px-4 py-3 text-center bg-gray-100 font-bold text-xs"),
                                            rx.el.th("📱 أشياء", class_name="px-4 py-3 text-center bg-gray-100 font-bold text-xs"),
                                            rx.el.th("🎤 صوت", class_name="px-4 py-3 text-center bg-gray-100 font-bold text-xs"),
                                            class_name="border-b-2 border-gray-300"
                                        )
                                    ),
                                    
                                    # Table Body
                                    rx.el.tbody(
                                        rx.foreach(
                                            GuvenliDashboardState.students,
                                            lambda student: rx.el.tr(
                                                # Status
                                                rx.el.td(
                                                    rx.cond(
                                                        student["is_active"],
                                                        rx.el.span("🟢 نشط", class_name="text-green-600 font-bold"),
                                                        rx.el.span("🔴 غير نشط", class_name="text-gray-400")
                                                    ),
                                                    class_name="px-4 py-3 border-b text-center"
                                                ),
                                                # Student ID
                                                rx.el.td(
                                                    student["student_id"],
                                                    class_name="px-4 py-3 border-b font-mono text-sm"
                                                ),
                                                # Student Name
                                                rx.el.td(
                                                    student["student_name"],
                                                    class_name="px-4 py-3 border-b font-semibold"
                                                ),
                                                # Total Violations
                                                rx.el.td(
                                                    str(student["total_violations"]),
                                                    class_name="px-4 py-3 border-b text-center font-bold"
                                                ),
                                                # Face Violations
                                                rx.el.td(
                                                    str(student["face_violations"]),
                                                    class_name="px-4 py-3 border-b text-center text-sm"
                                                ),
                                                # Eye Violations
                                                rx.el.td(
                                                    str(student["eye_violations"]),
                                                    class_name="px-4 py-3 border-b text-center text-sm"
                                                ),
                                                # Mouth Violations
                                                rx.el.td(
                                                    str(student["mouth_violations"]),
                                                    class_name="px-4 py-3 border-b text-center text-sm"
                                                ),
                                                # Multi-face Violations
                                                rx.el.td(
                                                    str(student["multi_face_violations"]),
                                                    class_name="px-4 py-3 border-b text-center text-sm"
                                                ),
                                                # Object Violations
                                                rx.el.td(
                                                    str(student["object_violations"]),
                                                    class_name="px-4 py-3 border-b text-center text-sm"
                                                ),
                                                # Audio Violations
                                                rx.el.td(
                                                    str(student["audio_violations"]),
                                                    class_name="px-4 py-3 border-b text-center text-sm"
                                                ),
                                                class_name="hover:bg-yellow-50 transition"
                                            )
                                        )
                                    ),
                                    
                                    class_name="w-full border-collapse shadow-lg"
                                ),
                                class_name="overflow-x-auto"
                            ),
                            rx.el.div(
                                "📭 لا يوجد طلاب مسجلون في هذا الاختبار",
                                class_name="text-center py-12 text-gray-500 text-xl"
                            )
                        )
                    ),
                    
                    class_name="bg-white p-6 rounded-lg shadow-md"
                ),
                class_name="max-w-7xl mx-auto px-4 mb-8"
            ),
            
           
            
            class_name="min-h-screen bg-gradient-to-br from-[#fff9db] to-[#ffeaa7]"
        )
    )
