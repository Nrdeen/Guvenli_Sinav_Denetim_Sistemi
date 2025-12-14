import reflex as rx
from datetime import datetime
import requests

API_URL = 'http://localhost:8001'

class AdminDashboardState(rx.State):
    '''حالة لوحة تحكم الأستاذة'''
    
    # Exam Management
    exam_name: str = ''
    exam_code: str = ''
    exam_duration: str = '120'
    exam_date: str = ''
    exam_url: str = ''
    exam_instructions: str = ''
    
    # Messages
    success_message: str = ''
    error_message: str = ''
    
    # UI State
    show_exam_form: bool = True
    show_question_form: bool = False
    
    # Students for exam
    student_id: str = ''
    student_name: str = ''
    student_email: str = ''
    added_students: list[dict] = []
    
    def open_exam_form(self):
        '''Sınav oluşturma formunu aç'''
        self.show_exam_form = True
        self.show_question_form = False
        # تفريغ الحقول
        self.exam_name = ''
        self.exam_code = ''
        self.exam_duration = '120'
        self.exam_date = ''
        self.exam_url = ''
        self.exam_instructions = ''
        self.success_message = ''
        self.error_message = ''
        self.added_students = []
    
    def add_student_to_exam(self):
        '''Öğrenciyi sınava ekle'''
        if not self.student_id or not self.student_name:
            self.error_message = 'Lütfen öğrenci numarası ve adını doldurun'
            return
        
        # Öğrenci tekrarını kontrol et
        for student in self.added_students:
            if student['student_id'] == self.student_id.upper():
                self.error_message = 'Öğrenci zaten listede mevcut'
                return
        
        self.added_students.append({
            'student_id': self.student_id.upper(),
            'student_name': self.student_name,
            'student_email': self.student_email or f"{self.student_id}@example.com"
        })
        
        # تفريغ الحقول
        self.student_id = ''
        self.student_name = ''
        self.student_email = ''
        self.error_message = ''
    
    def remove_student_from_exam(self, student_id: str):
        '''إزالة طالب من القائمة'''
        self.added_students = [s for s in self.added_students if s['student_id'] != student_id]
    
    def create_exam(self):
        '''Yeni sınav oluştur'''
        if not self.exam_name or not self.exam_code:
            self.error_message = 'Lütfen tüm alanları doldurun'
            return
        
        try:
            # إرسال البيانات إلى API
            response = requests.post(
                f'{API_URL}/api/exams',
                json={
                    'exam_name': self.exam_name,
                    'exam_code': self.exam_code.upper(),
                    'duration_minutes': int(self.exam_duration),
                    'exam_date': self.exam_date if self.exam_date else None,
                    'exam_url': self.exam_url if self.exam_url else None,
                    'exam_instructions': self.exam_instructions if self.exam_instructions else None
                },
                timeout=5
            )
            
            if response.status_code == 200:
                self.success_message = f'Sınav oluşturuldu: {self.exam_name} (Kod: {self.exam_code.upper()})'
                self.error_message = ''
                
                # إضافة الطلاب إلى الاختبار
                if self.added_students:
                    for student in self.added_students:
                        try:
                            student_response = requests.post(
                                f'{API_URL}/api/students',
                                json={
                                    'student_id': student['student_id'],
                                    'student_name': student['student_name'],
                                    'student_email': student['student_email'],
                                    'exam_code': self.exam_code.upper()
                                },
                                timeout=5
                            )
                            if student_response.status_code != 200:
                                print(f"فشل في إضافة الطالب {student['student_id']}: {student_response.text}")
                        except Exception as e:
                            print(f"خطأ في إضافة الطالب {student['student_id']}: {e}")
                
                # الانتقال إلى نموذج إضافة الأسئلة
                self.show_exam_form = False
                self.show_question_form = True
            else:
                error_data = response.json()
                self.error_message = f"{error_data.get('detail', 'Sınav oluşturulurken hata oluştu')}"
                self.success_message = ''
        except Exception as e:
            self.error_message = f"Sunucu bağlantı hatası: {str(e)}"
            self.success_message = ''
    
    def set_exam_name(self, value: str):
        self.exam_name = value
    
    def set_exam_code(self, value: str):
        self.exam_code = value
    
    def set_exam_duration(self, value: str):
        self.exam_duration = value
    
    def set_exam_date(self, value: str):
        self.exam_date = value
    
    def set_exam_url(self, value: str):
        self.exam_url = value
    
    def set_exam_instructions(self, value: str):
        self.exam_instructions = value
    
    def set_student_id(self, value: str):
        self.student_id = value
    
    def set_student_name(self, value: str):
        self.student_name = value
    
    def set_student_email(self, value: str):
        self.student_email = value
    
    def show_exam_form(self):
        '''إظهار نموذج إنشاء الاختبار'''
        self.show_exam_form = True
        self.success_message = ''
        self.error_message = ''


def admin_dashboard_page() -> rx.Component:
    '''Öğretmen kontrol paneli'''
    return rx.box(
        rx.el.div(
            # Header
            rx.el.div(
                rx.el.div(
                    rx.link(
                        rx.button(
                            'Çıkış Yap',
                            class_name='bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg'
                        ),
                        href='/'
                    ),
                    class_name='mb-4'
                ),
                rx.el.h1(
                    'Öğretmen Kontrol Paneli',
                    class_name='text-3xl font-bold text-blue-900 mb-2 text-center'
                ),
                rx.el.p(
                    'Sınavları ve öğrencileri yönetin',
                    class_name='text-gray-600 text-center mb-8'
                ),
                class_name='max-w-7xl mx-auto px-4 py-8'
            ),
            
            # Success/Error Messages
            rx.cond(
                AdminDashboardState.success_message != '',
                rx.el.div(
                    rx.el.div(
                        ' ' + AdminDashboardState.success_message,
                        class_name='bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded text-center'
                    ),
                    class_name='max-w-7xl mx-auto px-4 mb-4'
                ),
                rx.fragment()
            ),
            
            rx.cond(
                AdminDashboardState.error_message != '',
                rx.el.div(
                    rx.el.div(
                        ' ' + AdminDashboardState.error_message,
                        class_name='bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded text-center'
                    ),
                    class_name='max-w-7xl mx-auto px-4 mb-4'
                ),
                rx.fragment()
            ),
            
            # Quick Actions
            rx.el.div(
                rx.el.div(
                    # Action Card 1
                    rx.link(
                        rx.el.div(
                            rx.el.div(
                                rx.el.div('📊', class_name='text-5xl mb-3'),
                                rx.el.h3('Canlı İzleme', class_name='text-xl font-bold text-blue-900 mb-2'),
                                rx.el.p('Aktif öğrencileri görüntüle', class_name='text-gray-600'),
                                class_name='text-center'
                            ),
                            class_name='bg-white border-2 border-blue-200 p-6 rounded-lg shadow-lg hover:shadow-xl hover:border-blue-400 transition'
                        ),
                        href='/dashboard'
                    ),
                    
                    # Action Card 1.5 - System Dashboard
                    rx.link(
                        rx.el.div(
                            rx.el.div(
                                rx.el.div('💻', class_name='text-5xl mb-3'),
                                rx.el.h3('Sistem Paneli', class_name='text-xl font-bold text-blue-900 mb-2'),
                                rx.el.p('Tüm verileri görüntüle', class_name='text-gray-600'),
                                class_name='text-center'
                            ),
                            class_name='bg-white border-2 border-gray-300 p-6 rounded-lg shadow-lg hover:shadow-xl hover:border-gray-500 transition'
                        ),
                        href='/system-dashboard'
                    ),
                    
                    # Action Card 2
                    rx.el.div(
                        rx.el.div(
                            rx.el.div('📝', class_name='text-5xl mb-3'),
                            rx.el.h3('Sınav Oluştur', class_name='text-xl font-bold text-blue-900 mb-2'),
                            rx.el.p('Öğrenciler için yeni sınav', class_name='text-gray-600'),
                            class_name='text-center'
                        ),
                        on_click=AdminDashboardState.open_exam_form,
                        class_name='bg-white border-2 border-green-300 p-6 rounded-lg shadow-lg hover:shadow-xl hover:border-green-500 transition cursor-pointer'
                    ),
                    
                    # Action Card 3
                    rx.link(
                        rx.el.div(
                            rx.el.div(
                                rx.el.div('🎓', class_name='text-5xl mb-3'),
                                rx.el.h3('Öğrenci Girişi', class_name='text-xl font-bold text-blue-900 mb-2'),
                                rx.el.p('Öğrenci giriş sayfası', class_name='text-gray-600'),
                                class_name='text-center'
                            ),
                            class_name='bg-white border-2 border-blue-300 p-6 rounded-lg shadow-lg hover:shadow-xl hover:border-blue-500 transition'
                        ),
                        href='/student-login'
                    ),
                    
                    # Action Card 4
                    rx.link(
                        rx.el.div(
                            rx.el.div(
                                rx.el.div('👥', class_name='text-5xl mb-3'),
                                rx.el.h3('Öğrenci Yönetimi', class_name='text-xl font-bold text-blue-900 mb-2'),
                                rx.el.p('Öğrenci ekle ve sil', class_name='text-gray-600'),
                                class_name='text-center'
                            ),
                            class_name='bg-white border-2 border-gray-300 p-6 rounded-lg shadow-lg hover:shadow-xl hover:border-gray-500 transition'
                        ),
                        href='/students-management'
                    ),
                    
                    class_name='grid grid-cols-5 gap-4 mb-8'
                ),
                class_name='max-w-7xl mx-auto px-4'
            ),
            
            # Main Content
            rx.el.div(
                rx.el.div(
                    # Exam Creation Form
                    rx.cond(
                        AdminDashboardState.show_exam_form,
                        rx.el.div(
                            rx.el.div(
                                rx.el.h2('Yeni Sınav Oluştur', class_name='text-2xl font-bold mb-6 text-blue-900 text-center'),
                                rx.el.form(
                                    rx.el.div(
                                        # Exam Name
                                        rx.el.div(
                                            rx.el.label('Sınav Adı *', class_name='block text-gray-700 font-bold mb-2'),
                                            rx.el.input(
                                                type='text',
                                                placeholder='Sınav adını girin',
                                                value=AdminDashboardState.exam_name,
                                                on_change=AdminDashboardState.set_exam_name,
                                                class_name='w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500'
                                            ),
                                            class_name='mb-4'
                                        ),
                                        
                                        # Exam Code
                                        rx.el.div(
                                            rx.el.label('Sınav Kodu *', class_name='block text-gray-700 font-bold mb-2'),
                                            rx.el.input(
                                                type='text',
                                                placeholder='Örnek: MAT101',
                                                value=AdminDashboardState.exam_code,
                                                on_change=AdminDashboardState.set_exam_code,
                                                class_name='w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500'
                                            ),
                                            class_name='mb-4'
                                        ),
                                        
                                        # Duration
                                        rx.el.div(
                                            rx.el.label('Sınav Süresi (dakika)', class_name='block text-gray-700 font-bold mb-2'),
                                            rx.el.input(
                                                type='number',
                                                placeholder='120',
                                                value=AdminDashboardState.exam_duration,
                                                on_change=AdminDashboardState.set_exam_duration,
                                                class_name='w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500'
                                            ),
                                            class_name='mb-4'
                                        ),
                                        
                                        # Exam Date
                                        rx.el.div(
                                            rx.el.label('Sınav Tarihi (opsiyonel)', class_name='block text-gray-700 font-bold mb-2'),
                                            rx.el.input(
                                                type='datetime-local',
                                                value=AdminDashboardState.exam_date,
                                                on_change=AdminDashboardState.set_exam_date,
                                                class_name='w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500'
                                            ),
                                            class_name='mb-4'
                                        ),
                                        
                                        # Exam URL
                                        rx.el.div(
                                            rx.el.label('Sınav Bağlantısı (opsiyonel)', class_name='block text-gray-700 font-bold mb-2'),
                                            rx.el.input(
                                                type='url',
                                                placeholder='https://example.com/exam',
                                                value=AdminDashboardState.exam_url,
                                                on_change=AdminDashboardState.set_exam_url,
                                                class_name='w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500'
                                            ),
                                            class_name='mb-4'
                                        ),
                                        
                                        # Instructions
                                        rx.el.div(
                                            rx.el.label('Sınav Talimatları (opsiyonel)', class_name='block text-gray-700 font-bold mb-2'),
                                            rx.el.textarea(
                                                placeholder='Sınav talimatlarını buraya girin...',
                                                value=AdminDashboardState.exam_instructions,
                                                on_change=AdminDashboardState.set_exam_instructions,
                                                rows=4,
                                                class_name='w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 resize-vertical'
                                            ),
                                            class_name='mb-4'
                                        ),
                                        
                                        # Students Section
                                        rx.el.div(
                                            rx.el.h3('Öğrenci Ekle', class_name='text-lg font-bold mb-4 text-blue-900'),
                                            
                                            # Add Student Form
                                            rx.el.div(
                                                rx.el.div(
                                                    rx.el.label('Öğrenci Numarası *', class_name='block text-gray-700 font-bold mb-2'),
                                                    rx.el.input(
                                                        type='text',
                                                        placeholder='Öğrenci numarasını girin',
                                                        value=AdminDashboardState.student_id,
                                                        on_change=AdminDashboardState.set_student_id,
                                                        class_name='w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500'
                                                    ),
                                                    class_name='mb-4'
                                                ),
                                                rx.el.div(
                                                    rx.el.label('Öğrenci Adı *', class_name='block text-gray-700 font-bold mb-2'),
                                                    rx.el.input(
                                                        type='text',
                                                        placeholder='Öğrenci adını girin',
                                                        value=AdminDashboardState.student_name,
                                                        on_change=AdminDashboardState.set_student_name,
                                                        class_name='w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500'
                                                    ),
                                                    class_name='mb-4'
                                                ),
                                                rx.el.div(
                                                    rx.el.label('E-posta (opsiyonel)', class_name='block text-gray-700 font-bold mb-2'),
                                                    rx.el.input(
                                                        type='email',
                                                        placeholder='ogrenci@example.com',
                                                        value=AdminDashboardState.student_email,
                                                        on_change=AdminDashboardState.set_student_email,
                                                        class_name='w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500'
                                                    ),
                                                    class_name='mb-4'
                                                ),
                                                rx.el.button(
                                                    'Öğrenci Ekle',
                                                    type='button',
                                                    on_click=AdminDashboardState.add_student_to_exam,
                                                    class_name='w-full bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300 mb-4'
                                                ),
                                                class_name='grid grid-cols-1 md:grid-cols-3 gap-4 mb-4'
                                            ),
                                            
                                            # Students List
                                            rx.cond(
                                                AdminDashboardState.added_students.length() > 0,
                                                rx.el.div(
                                                    rx.el.h4('Eklenen Öğrenciler:', class_name='text-md font-bold mb-2 text-blue-900'),
                                                    rx.el.ul(
                                                        rx.foreach(
                                                            AdminDashboardState.added_students,
                                                            lambda student: rx.el.li(
                                                                rx.el.div(
                                                                    rx.el.span(f"{student['student_id']} - {student['student_name']}", class_name='flex-1'),
                                                                    rx.el.button(
                                                                        '❌',
                                                                        on_click=lambda: AdminDashboardState.remove_student_from_exam(student['student_id']),
                                                                        class_name='ml-2 text-red-500 hover:text-red-700'
                                                                    ),
                                                                    class_name='flex justify-between items-center p-2 bg-gray-50 rounded'
                                                                ),
                                                                class_name='mb-2'
                                                            )
                                                        ),
                                                        class_name='space-y-2'
                                                    ),
                                                    class_name='mb-4'
                                                )
                                            ),
                                            class_name='mb-6 p-4 bg-gray-50 rounded-lg'
                                        ),
                                        
                                        # Submit Button
                                        rx.el.button(
                                            'Sınavı Oluştur',
                                            type='button',
                                            on_click=AdminDashboardState.create_exam,
                                            class_name='w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg transition duration-300'
                                        ),
                                        
                                        class_name='max-w-2xl mx-auto'
                                    ),
                                    on_submit=AdminDashboardState.create_exam,
                                    class_name='bg-white p-8 rounded-lg shadow-lg'
                                ),
                                class_name='max-w-4xl mx-auto mb-8'
                            ),
                            rx.fragment()
                        ),
                        rx.fragment()
                    ),
                    
                    # Welcome Message (when no form is shown)
                    rx.cond(
                        ~AdminDashboardState.show_exam_form,
                        rx.el.div(
                            rx.el.div(
                                rx.el.div('👋', class_name='text-6xl mb-4 text-center'),
                                rx.el.h2('Öğretmen Kontrol Paneline Hoş Geldiniz', class_name='text-3xl font-bold mb-4 text-blue-900 text-center'),
                                rx.el.p(
                                    'Yukarıdaki kartlardan yapmak istediğiniz işlemi seçin',
                                    class_name='text-gray-600 text-center text-lg'
                                ),
                                class_name='bg-white p-8 rounded-lg shadow-lg text-center'
                            ),
                            class_name='max-w-4xl mx-auto'
                        ),
                        rx.fragment()
                    ),
                    
                    class_name='max-w-7xl mx-auto px-4 mb-8'
                ),
                class_name='max-w-7xl mx-auto'
            ),
            
        ),
        class_name="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50"
    )
