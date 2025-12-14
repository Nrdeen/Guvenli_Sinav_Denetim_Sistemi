import reflex as rx

class TeacherLoginState(rx.State):
    """حالة تسجيل دخول الأستاذة"""
    username: str = ""
    password: str = ""
    error_message: str = ""
    is_logged_in: bool = False
    
    def set_username(self, value: str):
        self.username = value
    
    def set_password(self, value: str):
        self.password = value
    
    def login(self):
        """تسجيل دخول الأستاذة"""
        # التحقق البسيط (يمكن ربطه بقاعدة البيانات لاحقاً)
        if self.username == "admin" and self.password == "admin123":
            self.is_logged_in = True
            self.error_message = ""
            return rx.redirect("/admin/dashboard")
        else:
            self.error_message = "اسم المستخدم أو كلمة المرور غير صحيحة"
            self.is_logged_in = False


def teacher_login_page() -> rx.Component:
    """صفحة تسجيل دخول الأستاذة"""
    return rx.box(
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "تسجيل دخول الأستاذة - Teacher Login",
                    class_name="text-3xl font-bold text-gray-800 mb-8 text-center"
                ),
                
                # Login Card
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            "🎓 لوحة تحكم المعلم",
                            class_name="text-2xl font-bold text-gray-800 mb-6 text-center"
                        ),
                        
                        # Error Message
                        rx.cond(
                            TeacherLoginState.error_message != "",
                            rx.el.div(
                                TeacherLoginState.error_message,
                                class_name="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4 text-center"
                            ),
                            rx.fragment()
                        ),
                        
                        # Username Input
                        rx.el.div(
                            rx.el.label(
                                "اسم المستخدم",
                                class_name="block text-gray-700 font-bold mb-2"
                            ),
                            rx.el.input(
                                type="text",
                                placeholder="admin",
                                value=TeacherLoginState.username,
                                on_change=TeacherLoginState.set_username,
                                class_name="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                            ),
                            class_name="mb-4"
                        ),
                        
                        # Password Input
                        rx.el.div(
                            rx.el.label(
                                "كلمة المرور",
                                class_name="block text-gray-700 font-bold mb-2"
                            ),
                            rx.el.input(
                                type="password",
                                placeholder="••••••••",
                                value=TeacherLoginState.password,
                                on_change=TeacherLoginState.set_password,
                                class_name="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                            ),
                            class_name="mb-6"
                        ),
                        
                        # Login Button
                        rx.button(
                            "تسجيل الدخول →",
                            on_click=TeacherLoginState.login,
                            class_name="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 px-4 rounded-lg"
                        ),
                        
                        # Info Box
                        rx.el.div(
                            rx.el.div(
                                rx.el.span("💡 ", class_name="text-2xl"),
                                rx.el.span("المعلومات الافتراضية:", class_name="font-bold"),
                                class_name="mb-2"
                            ),
                            rx.el.div("Username: admin", class_name="text-sm text-gray-600"),
                            rx.el.div("Password: admin123", class_name="text-sm text-gray-600"),
                            class_name="bg-blue-50 p-4 rounded-lg mt-6 text-right"
                        ),
                        
                        class_name="bg-white p-8 rounded-lg shadow-lg max-w-md w-full"
                    ),
                    class_name="flex justify-center items-center min-h-[70vh]"
                ),
                
                # Back Button
                rx.el.div(
                    rx.link(
                        rx.button(
                            "← العودة للرئيسية",
                            class_name="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg"
                        ),
                        href="/"
                    ),
                    class_name="text-center mt-6"
                ),
                
                class_name="max-w-4xl mx-auto px-4 py-8"
            ),
            class_name="min-h-screen bg-gradient-to-br from-[#e3f2fd] to-[#bbdefb]"
        )
    )
