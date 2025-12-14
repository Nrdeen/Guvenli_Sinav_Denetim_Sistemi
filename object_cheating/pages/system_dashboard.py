import reflex as rx
import requests
from datetime import datetime

API_URL = "http://localhost:8000"

class SystemDashboardState(rx.State):
    """حالة لوحة تحكم النظام"""
    
    # Summary Stats
    teachers_count: int = 0
    exams_count: int = 0
    students_count: int = 0
    registrations_count: int = 0
    active_sessions_count: int = 0
    violations_count: int = 0
    
    # Detailed Lists
    teachers_list: list[dict] = []
    exams_list: list[dict] = []
    registrations_list: list[dict] = []
    sessions_list: list[dict] = []
    violations_list: list[dict] = []
    
    # UI State
    selected_tab: str = "summary"
    is_loading: bool = False
    error_message: str = ""
    last_update: str = ""
    
    def load_dashboard_data(self):
        """تحميل بيانات لوحة التحكم"""
        self.is_loading = True
        self.error_message = ""
        
        try:
            response = requests.get(f"{API_URL}/api/dashboard/stats", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Update summary
                summary = data.get("summary", {})
                self.teachers_count = summary.get("teachers_count", 0)
                self.exams_count = summary.get("exams_count", 0)
                self.students_count = summary.get("students_count", 0)
                self.registrations_count = summary.get("registrations_count", 0)
                self.active_sessions_count = summary.get("active_sessions_count", 0)
                self.violations_count = summary.get("violations_count", 0)
                
                # Update lists
                self.teachers_list = data.get("teachers", [])
                self.exams_list = data.get("exams", [])
                self.registrations_list = data.get("registrations", [])
                self.sessions_list = data.get("active_sessions", [])
                self.violations_list = data.get("violations", [])
                
                self.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            else:
                self.error_message = f"خطأ في تحميل البيانات: {response.status_code}"
        except Exception as e:
            self.error_message = f"خطأ في الاتصال: {str(e)}"
        finally:
            self.is_loading = False
    
    def set_tab(self, tab: str):
        """تغيير التبويب النشط"""
        self.selected_tab = tab


def system_dashboard_page() -> rx.Component:
    """صفحة لوحة تحكم النظام الشاملة"""
    return rx.box(
        rx.el.div(
            # Header
            rx.el.div(
                rx.el.div(
                    rx.link(
                        rx.button(
                            "← العودة",
                            class_name="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg"
                        ),
                        href="/admin-dashboard"
                    ),
                    rx.button(
                        "🔄 تحديث البيانات",
                        on_click=SystemDashboardState.load_dashboard_data,
                        class_name="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg"
                    ),
                    class_name="flex gap-2 mb-4"
                ),
                rx.el.h1(
                    "🖥️ نظام مراقبة الامتحانات الآمن - System Dashboard",
                    class_name="text-3xl font-bold text-gray-800 mb-2 text-center"
                ),
                rx.el.p(
                    "لوحة التحكم الشاملة لجميع بيانات النظام",
                    class_name="text-gray-600 text-center mb-2"
                ),
                rx.cond(
                    SystemDashboardState.last_update != "",
                    rx.el.p(
                        f"آخر تحديث: {SystemDashboardState.last_update}",
                        class_name="text-gray-500 text-sm text-center mb-6"
                    ),
                    rx.fragment()
                ),
                class_name="max-w-7xl mx-auto px-4 py-8"
            ),
            
            # Error Message
            rx.cond(
                SystemDashboardState.error_message != "",
                rx.el.div(
                    rx.el.div(
                        "⚠️ " + SystemDashboardState.error_message,
                        class_name="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded text-center"
                    ),
                    class_name="max-w-7xl mx-auto px-4 mb-4"
                ),
                rx.fragment()
            ),
            
            # Summary Cards
            rx.el.div(
                rx.el.div(
                    # Teachers Card
                    rx.el.div(
                        rx.el.div(
                            rx.el.div("👨‍🏫", class_name="text-4xl mb-2"),
                            rx.el.h3("الأساتذة", class_name="text-lg font-bold text-gray-700 mb-1"),
                            rx.el.p(
                                SystemDashboardState.teachers_count.to_string(),
                                class_name="text-3xl font-bold text-blue-600"
                            ),
                            class_name="text-center"
                        ),
                        on_click=lambda: SystemDashboardState.set_tab("teachers"),
                        class_name="bg-blue-50 p-6 rounded-lg shadow-md hover:shadow-lg transition cursor-pointer border-2 border-blue-200"
                    ),
                    
                    # Exams Card
                    rx.el.div(
                        rx.el.div(
                            rx.el.div("📝", class_name="text-4xl mb-2"),
                            rx.el.h3("الاختبارات", class_name="text-lg font-bold text-gray-700 mb-1"),
                            rx.el.p(
                                SystemDashboardState.exams_count.to_string(),
                                class_name="text-3xl font-bold text-green-600"
                            ),
                            class_name="text-center"
                        ),
                        on_click=lambda: SystemDashboardState.set_tab("exams"),
                        class_name="bg-green-50 p-6 rounded-lg shadow-md hover:shadow-lg transition cursor-pointer border-2 border-green-200"
                    ),
                    
                    # Students Card
                    rx.el.div(
                        rx.el.div(
                            rx.el.div("👨‍🎓", class_name="text-4xl mb-2"),
                            rx.el.h3("الطلاب", class_name="text-lg font-bold text-gray-700 mb-1"),
                            rx.el.p(
                                SystemDashboardState.students_count.to_string(),
                                class_name="text-3xl font-bold text-purple-600"
                            ),
                            class_name="text-center"
                        ),
                        on_click=lambda: SystemDashboardState.set_tab("students"),
                        class_name="bg-purple-50 p-6 rounded-lg shadow-md hover:shadow-lg transition cursor-pointer border-2 border-purple-200"
                    ),
                    
                    # Registrations Card
                    rx.el.div(
                        rx.el.div(
                            rx.el.div("📋", class_name="text-4xl mb-2"),
                            rx.el.h3("التسجيلات", class_name="text-lg font-bold text-gray-700 mb-1"),
                            rx.el.p(
                                SystemDashboardState.registrations_count.to_string(),
                                class_name="text-3xl font-bold text-yellow-600"
                            ),
                            class_name="text-center"
                        ),
                        on_click=lambda: SystemDashboardState.set_tab("registrations"),
                        class_name="bg-yellow-50 p-6 rounded-lg shadow-md hover:shadow-lg transition cursor-pointer border-2 border-yellow-200"
                    ),
                    
                    # Active Sessions Card
                    rx.el.div(
                        rx.el.div(
                            rx.el.div("🖥️", class_name="text-4xl mb-2"),
                            rx.el.h3("الجلسات النشطة", class_name="text-lg font-bold text-gray-700 mb-1"),
                            rx.el.p(
                                SystemDashboardState.active_sessions_count.to_string(),
                                class_name="text-3xl font-bold text-cyan-600"
                            ),
                            class_name="text-center"
                        ),
                        on_click=lambda: SystemDashboardState.set_tab("sessions"),
                        class_name="bg-cyan-50 p-6 rounded-lg shadow-md hover:shadow-lg transition cursor-pointer border-2 border-cyan-200"
                    ),
                    
                    # Violations Card
                    rx.el.div(
                        rx.el.div(
                            rx.el.div("⚠️", class_name="text-4xl mb-2"),
                            rx.el.h3("الانتهاكات", class_name="text-lg font-bold text-gray-700 mb-1"),
                            rx.el.p(
                                SystemDashboardState.violations_count.to_string(),
                                class_name="text-3xl font-bold text-red-600"
                            ),
                            class_name="text-center"
                        ),
                        on_click=lambda: SystemDashboardState.set_tab("violations"),
                        class_name="bg-red-50 p-6 rounded-lg shadow-md hover:shadow-lg transition cursor-pointer border-2 border-red-200"
                    ),
                    
                    class_name="grid grid-cols-3 gap-6 mb-8"
                ),
                class_name="max-w-7xl mx-auto px-4"
            ),
            
            # Detailed Tables
            rx.el.div(
                # Teachers Table
                rx.cond(
                    SystemDashboardState.selected_tab == "teachers",
                    rx.el.div(
                        rx.el.h2("👨‍🏫 قائمة الأساتذة", class_name="text-2xl font-bold mb-4 text-gray-800"),
                        rx.cond(
                            SystemDashboardState.teachers_list.length() > 0,
                            rx.el.div(
                                rx.el.table(
                                    rx.el.thead(
                                        rx.el.tr(
                                            rx.el.th("ID", class_name="px-4 py-3 text-right bg-blue-100 font-bold"),
                                            rx.el.th("اسم المستخدم", class_name="px-4 py-3 text-right bg-blue-100 font-bold"),
                                            rx.el.th("الاسم الكامل", class_name="px-4 py-3 text-right bg-blue-100 font-bold"),
                                            rx.el.th("البريد الإلكتروني", class_name="px-4 py-3 text-right bg-blue-100 font-bold"),
                                        )
                                    ),
                                    rx.el.tbody(
                                        rx.foreach(
                                            SystemDashboardState.teachers_list,
                                            lambda teacher: rx.el.tr(
                                                rx.el.td(teacher["id"].to_string(), class_name="px-4 py-3 border-b"),
                                                rx.el.td(teacher["username"], class_name="px-4 py-3 border-b font-mono"),
                                                rx.el.td(teacher["full_name"], class_name="px-4 py-3 border-b"),
                                                rx.el.td(teacher["email"], class_name="px-4 py-3 border-b text-sm text-gray-600"),
                                                class_name="hover:bg-gray-50"
                                            )
                                        )
                                    ),
                                    class_name="w-full border-collapse"
                                ),
                                class_name="overflow-x-auto"
                            ),
                            rx.el.p("لا يوجد أساتذة", class_name="text-gray-500 text-center py-8")
                        ),
                        class_name="bg-white p-6 rounded-lg shadow-md"
                    ),
                    rx.fragment()
                ),
                
                # Exams Table
                rx.cond(
                    SystemDashboardState.selected_tab == "exams",
                    rx.el.div(
                        rx.el.h2("📝 قائمة الاختبارات", class_name="text-2xl font-bold mb-4 text-gray-800"),
                        rx.cond(
                            SystemDashboardState.exams_list.length() > 0,
                            rx.el.div(
                                rx.el.table(
                                    rx.el.thead(
                                        rx.el.tr(
                                            rx.el.th("رمز الاختبار", class_name="px-4 py-3 text-right bg-green-100 font-bold"),
                                            rx.el.th("اسم الاختبار", class_name="px-4 py-3 text-right bg-green-100 font-bold"),
                                            rx.el.th("المدة (دقيقة)", class_name="px-4 py-3 text-right bg-green-100 font-bold"),
                                            rx.el.th("الحالة", class_name="px-4 py-3 text-right bg-green-100 font-bold"),
                                            rx.el.th("وقت البدء", class_name="px-4 py-3 text-right bg-green-100 font-bold"),
                                        )
                                    ),
                                    rx.el.tbody(
                                        rx.foreach(
                                            SystemDashboardState.exams_list,
                                            lambda exam: rx.el.tr(
                                                rx.el.td(exam["exam_code"], class_name="px-4 py-3 border-b font-mono text-blue-600 font-bold"),
                                                rx.el.td(exam["exam_name"], class_name="px-4 py-3 border-b"),
                                                rx.el.td(exam["duration_minutes"].to_string(), class_name="px-4 py-3 border-b text-center"),
                                                rx.el.td(
                                                    rx.el.span(
                                                        exam["status"],
                                                        class_name="px-2 py-1 rounded text-sm font-bold bg-green-100 text-green-800"
                                                    ),
                                                    class_name="px-4 py-3 border-b"
                                                ),
                                                rx.el.td(
                                                    rx.cond(
                                                        exam["start_time"],
                                                        exam["start_time"],
                                                        "غير محدد"
                                                    ),
                                                    class_name="px-4 py-3 border-b text-sm text-gray-600"
                                                ),
                                                class_name="hover:bg-gray-50"
                                            )
                                        )
                                    ),
                                    class_name="w-full border-collapse"
                                ),
                                class_name="overflow-x-auto"
                            ),
                            rx.el.p("لا توجد اختبارات", class_name="text-gray-500 text-center py-8")
                        ),
                        class_name="bg-white p-6 rounded-lg shadow-md"
                    ),
                    rx.fragment()
                ),
                
                # Registrations Table
                rx.cond(
                    SystemDashboardState.selected_tab == "registrations",
                    rx.el.div(
                        rx.el.h2("📋 قائمة التسجيلات", class_name="text-2xl font-bold mb-4 text-gray-800"),
                        rx.cond(
                            SystemDashboardState.registrations_list.length() > 0,
                            rx.el.div(
                                rx.el.table(
                                    rx.el.thead(
                                        rx.el.tr(
                                            rx.el.th("رقم الطالب", class_name="px-4 py-3 text-right bg-yellow-100 font-bold"),
                                            rx.el.th("اسم الطالب", class_name="px-4 py-3 text-right bg-yellow-100 font-bold"),
                                            rx.el.th("رمز الاختبار", class_name="px-4 py-3 text-right bg-yellow-100 font-bold"),
                                            rx.el.th("اسم الاختبار", class_name="px-4 py-3 text-right bg-yellow-100 font-bold"),
                                            rx.el.th("الحالة", class_name="px-4 py-3 text-right bg-yellow-100 font-bold"),
                                            rx.el.th("تاريخ التسجيل", class_name="px-4 py-3 text-right bg-yellow-100 font-bold"),
                                        )
                                    ),
                                    rx.el.tbody(
                                        rx.foreach(
                                            SystemDashboardState.registrations_list,
                                            lambda reg: rx.el.tr(
                                                rx.el.td(reg["student_id"], class_name="px-4 py-3 border-b font-mono"),
                                                rx.el.td(reg["student_name"], class_name="px-4 py-3 border-b"),
                                                rx.el.td(reg["exam_code"], class_name="px-4 py-3 border-b font-mono text-blue-600"),
                                                rx.el.td(reg["exam_name"], class_name="px-4 py-3 border-b"),
                                                rx.el.td(
                                                    rx.el.span(
                                                        reg["status"],
                                                        class_name="px-2 py-1 rounded text-sm font-bold bg-blue-100 text-blue-800"
                                                    ),
                                                    class_name="px-4 py-3 border-b"
                                                ),
                                                rx.el.td(
                                                    rx.cond(
                                                        reg["registered_at"],
                                                        reg["registered_at"],
                                                        "غير محدد"
                                                    ),
                                                    class_name="px-4 py-3 border-b text-sm text-gray-600"
                                                ),
                                                class_name="hover:bg-gray-50"
                                            )
                                        )
                                    ),
                                    class_name="w-full border-collapse"
                                ),
                                class_name="overflow-x-auto"
                            ),
                            rx.el.p("لا توجد تسجيلات", class_name="text-gray-500 text-center py-8")
                        ),
                        class_name="bg-white p-6 rounded-lg shadow-md"
                    ),
                    rx.fragment()
                ),
                
                # Active Sessions Table
                rx.cond(
                    SystemDashboardState.selected_tab == "sessions",
                    rx.el.div(
                        rx.el.h2("🖥️ الجلسات النشطة", class_name="text-2xl font-bold mb-4 text-gray-800"),
                        rx.cond(
                            SystemDashboardState.sessions_list.length() > 0,
                            rx.el.div(
                                rx.el.table(
                                    rx.el.thead(
                                        rx.el.tr(
                                            rx.el.th("رقم الطالب", class_name="px-4 py-3 text-right bg-cyan-100 font-bold"),
                                            rx.el.th("اسم الطالب", class_name="px-4 py-3 text-right bg-cyan-100 font-bold"),
                                            rx.el.th("رمز الاختبار", class_name="px-4 py-3 text-right bg-cyan-100 font-bold"),
                                            rx.el.th("اسم الاختبار", class_name="px-4 py-3 text-right bg-cyan-100 font-bold"),
                                            rx.el.th("وقت البدء", class_name="px-4 py-3 text-right bg-cyan-100 font-bold"),
                                            rx.el.th("آخر نبضة", class_name="px-4 py-3 text-right bg-cyan-100 font-bold"),
                                        )
                                    ),
                                    rx.el.tbody(
                                        rx.foreach(
                                            SystemDashboardState.sessions_list,
                                            lambda session: rx.el.tr(
                                                rx.el.td(session["student_id"], class_name="px-4 py-3 border-b font-mono"),
                                                rx.el.td(session["student_name"], class_name="px-4 py-3 border-b"),
                                                rx.el.td(session["exam_code"], class_name="px-4 py-3 border-b font-mono text-blue-600"),
                                                rx.el.td(session["exam_name"], class_name="px-4 py-3 border-b"),
                                                rx.el.td(
                                                    rx.cond(
                                                        session["started_at"],
                                                        session["started_at"],
                                                        "غير محدد"
                                                    ),
                                                    class_name="px-4 py-3 border-b text-sm text-gray-600"
                                                ),
                                                rx.el.td(
                                                    rx.cond(
                                                        session["last_heartbeat"],
                                                        session["last_heartbeat"],
                                                        "غير محدد"
                                                    ),
                                                    class_name="px-4 py-3 border-b text-sm text-green-600"
                                                ),
                                                class_name="hover:bg-gray-50"
                                            )
                                        )
                                    ),
                                    class_name="w-full border-collapse"
                                ),
                                class_name="overflow-x-auto"
                            ),
                            rx.el.p("لا توجد جلسات نشطة", class_name="text-gray-500 text-center py-8")
                        ),
                        class_name="bg-white p-6 rounded-lg shadow-md"
                    ),
                    rx.fragment()
                ),
                
                # Violations Table
                rx.cond(
                    SystemDashboardState.selected_tab == "violations",
                    rx.el.div(
                        rx.el.h2("⚠️ قائمة الانتهاكات", class_name="text-2xl font-bold mb-4 text-gray-800"),
                        rx.cond(
                            SystemDashboardState.violations_list.length() > 0,
                            rx.el.div(
                                rx.el.table(
                                    rx.el.thead(
                                        rx.el.tr(
                                            rx.el.th("رقم الطالب", class_name="px-4 py-3 text-right bg-red-100 font-bold"),
                                            rx.el.th("اسم الطالب", class_name="px-4 py-3 text-right bg-red-100 font-bold"),
                                            rx.el.th("رمز الاختبار", class_name="px-4 py-3 text-right bg-red-100 font-bold"),
                                            rx.el.th("نوع الانتهاك", class_name="px-4 py-3 text-right bg-red-100 font-bold"),
                                            rx.el.th("الخطورة", class_name="px-4 py-3 text-right bg-red-100 font-bold"),
                                            rx.el.th("الوصف", class_name="px-4 py-3 text-right bg-red-100 font-bold"),
                                            rx.el.th("وقت الاكتشاف", class_name="px-4 py-3 text-right bg-red-100 font-bold"),
                                        )
                                    ),
                                    rx.el.tbody(
                                        rx.foreach(
                                            SystemDashboardState.violations_list,
                                            lambda viol: rx.el.tr(
                                                rx.el.td(viol["student_id"], class_name="px-4 py-3 border-b font-mono"),
                                                rx.el.td(viol["student_name"], class_name="px-4 py-3 border-b"),
                                                rx.el.td(viol["exam_code"], class_name="px-4 py-3 border-b font-mono text-blue-600"),
                                                rx.el.td(viol["violation_type"], class_name="px-4 py-3 border-b font-bold text-red-600"),
                                                rx.el.td(
                                                    rx.el.span(
                                                        viol["severity"],
                                                        class_name="px-2 py-1 rounded text-sm font-bold bg-red-100 text-red-800"
                                                    ),
                                                    class_name="px-4 py-3 border-b"
                                                ),
                                                rx.el.td(
                                                    rx.cond(
                                                        viol["description"],
                                                        viol["description"],
                                                        "-"
                                                    ),
                                                    class_name="px-4 py-3 border-b text-sm"
                                                ),
                                                rx.el.td(
                                                    rx.cond(
                                                        viol["detected_at"],
                                                        viol["detected_at"],
                                                        "غير محدد"
                                                    ),
                                                    class_name="px-4 py-3 border-b text-sm text-gray-600"
                                                ),
                                                class_name="hover:bg-gray-50"
                                            )
                                        )
                                    ),
                                    class_name="w-full border-collapse"
                                ),
                                class_name="overflow-x-auto"
                            ),
                            rx.el.p("لا توجد انتهاكات", class_name="text-gray-500 text-center py-8")
                        ),
                        class_name="bg-white p-6 rounded-lg shadow-md"
                    ),
                    rx.fragment()
                ),
                
                class_name="max-w-7xl mx-auto px-4 mb-8"
            ),
            
            class_name="min-h-screen bg-gradient-to-br from-[#f0f4f8] to-[#d9e2ec]",
            on_mount=SystemDashboardState.load_dashboard_data
        )
    )