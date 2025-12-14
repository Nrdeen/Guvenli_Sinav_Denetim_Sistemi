import reflex as rx
from datetime import datetime
import requests

API_URL = "http://localhost:8000"

class CreateExamState(rx.State):
    """حالة صفحة إنشاء الاختبار"""

    # Exam Management
    exam_name: str = ""
    exam_code: str = ""
    exam_duration: str = "120"
    exam_date: str = ""
    exam_url: str = ""
    exam_instructions: str = ""

    # Messages
    success_message: str = ""
    error_message: str = ""

    def create_exam(self):
        """إنشاء اختبار جديد"""
        if not self.exam_name or not self.exam_code:
            self.error_message = "يرجى ملء جميع الحقول المطلوبة"
            return

        try:
            # إرسال البيانات إلى API
            response = requests.post(
                f"{API_URL}/api/exams",
                json={
                    "exam_name": self.exam_name,
                    "exam_code": self.exam_code.upper(),
                    "duration_minutes": int(self.exam_duration),
                    "exam_date": self.exam_date if self.exam_date else None,
                    "exam_url": self.exam_url if self.exam_url else None,
                    "exam_instructions": self.exam_instructions if self.exam_instructions else None
                },
                timeout=5
            )

            if response.status_code == 200:
                self.success_message = f"✅ تم إنشاء الاختبار بنجاح: {self.exam_name} (رمز: {self.exam_code.upper()})"
                self.error_message = ""

                # تفريغ الحقول بعد النجاح
                self.exam_name = ""
                self.exam_code = ""
                self.exam_duration = "120"
                self.exam_date = ""
                self.exam_url = ""
                self.exam_instructions = ""
            else:
                error_data = response.json()
                self.error_message = f"❌ {error_data.get('detail', 'حدث خطأ أثناء إنشاء الاختبار')}"
                self.success_message = ""
        except Exception as e:
            self.error_message = f"❌ خطأ في الاتصال بالخادم: {str(e)}"
            self.success_message = ""

def create_exam_page() -> rx.Component:
    """صفحة إنشاء اختبار جديد"""
    return rx.box(
        rx.el.div(
            # Header with back button
            rx.el.div(
                rx.link(
                    rx.button(
                        "← العودة إلى لوحة التحكم",
                        class_name="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg mb-4"
                    ),
                    href="/admin/dashboard"
                ),
                rx.el.h1(
                    "📝 إنشاء اختبار جديد",
                    class_name="text-3xl font-bold text-gray-800 mb-2 text-center"
                ),
                rx.el.p(
                    "أدخل تفاصيل الاختبار الجديد للطلاب",
                    class_name="text-gray-600 text-center mb-8"
                ),
                class_name="mb-8"
            ),

            # Success/Error Messages
            rx.cond(
                CreateExamState.success_message != "",
                rx.el.div(
                    CreateExamState.success_message,
                    class_name="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-lg mb-6 text-center"
                ),
                rx.fragment()
            ),
            rx.cond(
                CreateExamState.error_message != "",
                rx.el.div(
                    CreateExamState.error_message,
                    class_name="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg mb-6 text-center"
                ),
                rx.fragment()
            ),

            # Exam Creation Form
            rx.el.div(
                rx.el.div(
                    # Exam Name
                    rx.el.div(
                        rx.el.label("اسم الاختبار *", class_name="block text-gray-700 font-bold mb-2"),
                        rx.el.input(
                            type="text",
                            placeholder="مثال: اختبار البرمجة النهائي",
                            value=CreateExamState.exam_name,
                            on_change=CreateExamState.set_exam_name,
                            class_name="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                        ),
                        class_name="mb-4"
                    ),

                    # Exam Code
                    rx.el.div(
                        rx.el.label("رمز الاختبار (للطلاب) *", class_name="block text-gray-700 font-bold mb-2"),
                        rx.el.input(
                            type="text",
                            placeholder="مثال: PROG2025",
                            value=CreateExamState.exam_code,
                            on_change=CreateExamState.set_exam_code,
                            class_name="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 uppercase"
                        ),
                        rx.el.p(
                            "رمز فريد يستخدمه الطلاب للوصول إلى الاختبار",
                            class_name="text-sm text-gray-500 mt-1"
                        ),
                        class_name="mb-4"
                    ),

                    # Duration
                    rx.el.div(
                        rx.el.label("مدة الاختبار (دقيقة)", class_name="block text-gray-700 font-bold mb-2"),
                        rx.el.input(
                            type="number",
                            placeholder="120",
                            value=CreateExamState.exam_duration,
                            on_change=CreateExamState.set_exam_duration,
                            class_name="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                        ),
                        class_name="mb-4"
                    ),

                    # Date
                    rx.el.div(
                        rx.el.label("تاريخ الاختبار", class_name="block text-gray-700 font-bold mb-2"),
                        rx.el.input(
                            type="datetime-local",
                            value=CreateExamState.exam_date,
                            on_change=CreateExamState.set_exam_date,
                            class_name="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                        ),
                        class_name="mb-4"
                    ),

                    # Exam URL/Link
                    rx.el.div(
                        rx.el.label("رابط الاختبار (اختياري)", class_name="block text-gray-700 font-bold mb-2"),
                        rx.el.input(
                            type="url",
                            placeholder="https://forms.google.com/... أو رابط آخر",
                            value=CreateExamState.exam_url,
                            on_change=CreateExamState.set_exam_url,
                            class_name="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                        ),
                        rx.el.p(
                            "يمكنك إضافة رابط Google Forms أو أي منصة اختبارات أخرى",
                            class_name="text-sm text-gray-500 mt-1"
                        ),
                        class_name="mb-4"
                    ),

                    # Instructions
                    rx.el.div(
                        rx.el.label("تعليمات الاختبار (اختياري)", class_name="block text-gray-700 font-bold mb-2"),
                        rx.el.textarea(
                            placeholder="أدخل تعليمات الاختبار هنا...",
                            value=CreateExamState.exam_instructions,
                            on_change=CreateExamState.set_exam_instructions,
                            rows=4,
                            class_name="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 resize-vertical"
                        ),
                        rx.el.p(
                            "تعليمات إضافية سيراها الطلاب قبل بدء الاختبار",
                            class_name="text-sm text-gray-500 mt-1"
                        ),
                        class_name="mb-6"
                    ),

                    # Create Button
                    rx.button(
                        "📝 إنشاء الاختبار",
                        on_click=CreateExamState.create_exam,
                        class_name="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-3 px-4 rounded-lg text-lg shadow-lg"
                    ),

                    class_name="bg-white p-8 rounded-lg shadow-lg max-w-2xl mx-auto"
                ),
                class_name="max-w-4xl mx-auto px-4"
            ),
            class_name="max-w-6xl mx-auto px-4 py-8"
        ),
        class_name="min-h-screen bg-gradient-to-br from-[#e8f5e9] to-[#c8e6c9]"
    )