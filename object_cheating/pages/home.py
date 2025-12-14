import reflex as rx

def home_page() -> rx.Component:
    return rx.box(
        # Header Section
        rx.el.div(
            rx.el.h1(
                "Sınav Gözetim Sistemi",
                class_name="text-6xl md:text-7xl font-bold text-blue-900 mb-6 text-center tracking-tight"
            ),
            rx.el.div(
                class_name="w-24 h-1 bg-blue-600 mx-auto mb-6 rounded-full"
            ),
            rx.el.p(
                "Yapay zeka destekli güvenli sınav yönetimi",
                class_name="text-xl md:text-2xl text-gray-600 text-center max-w-3xl mx-auto font-light"
            ),
            class_name="pt-24 pb-20"
        ),
        
        # Cards Container - Side by Side
        rx.el.div(
            # Card 1: Classroom Test (Left)
            rx.el.div(
                rx.el.div(
                    # Icon with background
                    rx.el.div(
                        rx.el.div(
                            "🏫",
                            class_name="text-6xl"
                        ),
                        class_name="w-28 h-28 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-8"
                    ),
                    # Title
                    rx.el.h2(
                        "Sınıf İçi Sınav",
                        class_name="text-3xl font-bold text-blue-900 mb-6 text-center"
                    ),
                    # Description
                    rx.el.p(
                        "Fiziksel sınıf ortamında gerçek zamanlı gözetim ve davranış analizi sistemi",
                        class_name="text-gray-600 text-center mb-10 leading-relaxed text-lg"
                    ),
                    # Features list - vertical
                    rx.el.div(
                        rx.el.div(
                            "Davranış Analizi",
                            class_name="text-gray-700 font-medium py-3 px-6 bg-gray-100 rounded-lg"
                        ),
                        rx.el.div(
                            "Nesne Tespiti",
                            class_name="text-gray-700 font-medium py-3 px-6 bg-gray-100 rounded-lg"
                        ),
                        rx.el.div(
                            "Göz Takibi",
                            class_name="text-gray-700 font-medium py-3 px-6 bg-gray-100 rounded-lg"
                        ),
                        rx.el.div(
                            "Canlı İzleme",
                            class_name="text-gray-700 font-medium py-3 px-6 bg-gray-100 rounded-lg"
                        ),
                        class_name="space-y-3 mb-10"
                    ),
                    # Button
                    rx.el.div(
                        rx.link(
                            rx.button(
                                "Sisteme Gir",
                                class_name="bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 px-16 rounded-lg text-lg shadow-md hover:shadow-lg transition-all duration-300"
                            ),
                            href="/detection"
                        ),
                        class_name="flex justify-center"
                    ),
                    class_name="bg-white p-12 rounded-3xl shadow-2xl hover:shadow-3xl transition-all duration-500 border-2 border-gray-100 h-full flex flex-col"
                ),
                class_name="w-full md:w-1/2 p-4"
            ),
            
            # Card 2: Online Test (Right)
            rx.el.div(
                rx.el.div(
                    # Icon with background
                    rx.el.div(
                        rx.el.div(
                            "💻",
                            class_name="text-6xl"
                        ),
                        class_name="w-28 h-28 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-8"
                    ),
                    # Title
                    rx.el.h2(
                        "Online Sınav",
                        class_name="text-3xl font-bold text-blue-900 mb-6 text-center"
                    ),
                    # Description
                    rx.el.p(
                        "Uzaktan eğitim için kapsamlı online sınav gözetim ve raporlama sistemi",
                        class_name="text-gray-600 text-center mb-10 leading-relaxed text-lg"
                    ),
                    # Features list - vertical
                    rx.el.div(
                        rx.el.div(
                            "Yüz ve Göz Takibi",
                            class_name="text-gray-700 font-medium py-3 px-6 bg-gray-100 rounded-lg"
                        ),
                        rx.el.div(
                            "Ekran Kaydı",
                            class_name="text-gray-700 font-medium py-3 px-6 bg-gray-100 rounded-lg"
                        ),
                        rx.el.div(
                            "Ses Tespiti",
                            class_name="text-gray-700 font-medium py-3 px-6 bg-gray-100 rounded-lg"
                        ),
                        rx.el.div(
                            "Detaylı Raporlama",
                            class_name="text-gray-700 font-medium py-3 px-6 bg-gray-100 rounded-lg"
                        ),
                        class_name="space-y-3 mb-10"
                    ),
                    # Button
                    rx.el.div(
                        rx.link(
                            rx.button(
                                "Sisteme Gir",
                                class_name="bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 px-16 rounded-lg text-lg shadow-md hover:shadow-lg transition-all duration-300"
                            ),
                            href="/admin/dashboard"
                        ),
                        class_name="flex justify-center"
                    ),
                    class_name="bg-white p-12 rounded-3xl shadow-2xl hover:shadow-3xl transition-all duration-500 border-2 border-gray-100 h-full flex flex-col"
                ),
                class_name="w-full md:w-1/2 p-4"
            ),
            
            class_name="flex flex-col md:flex-row justify-center items-stretch max-w-7xl mx-auto px-4 gap-2"
        ),
        
        # Footer Info
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        "🔒",
                        class_name="text-4xl mb-3"
                    ),
                    rx.el.p(
                        "Güvenli",
                        class_name="text-gray-700 font-semibold text-lg"
                    ),
                    rx.el.p(
                        "Şifreli veri koruması",
                        class_name="text-gray-500 text-sm"
                    ),
                    class_name="text-center"
                ),
                rx.el.div(
                    rx.el.div(
                        "🎯",
                        class_name="text-4xl mb-3"
                    ),
                    rx.el.p(
                        "Hassas",
                        class_name="text-gray-700 font-semibold text-lg"
                    ),
                    rx.el.p(
                        "Yüksek doğruluk oranı",
                        class_name="text-gray-500 text-sm"
                    ),
                    class_name="text-center"
                ),
                rx.el.div(
                    rx.el.div(
                        "⚡",
                        class_name="text-4xl mb-3"
                    ),
                    rx.el.p(
                        "Hızlı",
                        class_name="text-gray-700 font-semibold text-lg"
                    ),
                    rx.el.p(
                        "Anlık gerçek zamanlı analiz",
                        class_name="text-gray-500 text-sm"
                    ),
                    class_name="text-center"
                ),
                class_name="flex flex-wrap justify-center gap-16"
            ),
            class_name="mt-24 pb-20"
        ),
        
        class_name="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50"
    )