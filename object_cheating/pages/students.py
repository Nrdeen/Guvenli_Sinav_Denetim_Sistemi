import reflex as rx
from object_cheating.states.students_state import StudentsState

def students_page() -> rx.Component:
    """Öğrenci yönetimi sayfası."""
    return rx.box(
        # Header
        rx.el.div(
            rx.link(
                rx.button(
                    "← Ana Sayfaya Dön",
                    class_name="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg mb-4"
                ),
                href="/"
            ),
            rx.el.h1(
                "Öğrenci Yönetimi",
                class_name="text-3xl font-bold text-blue-900 mb-8 text-center"
            ),
            class_name="max-w-7xl mx-auto px-4 py-8"
        ),

        # Add Student Form
        rx.el.div(
            rx.el.h2("Yeni Öğrenci Ekle", class_name="text-xl font-semibold mb-4 text-blue-900"),
            rx.el.div(
                rx.input(
                    placeholder="Öğrenci Adı",
                    value=StudentsState.new_student_name,
                    on_change=StudentsState.set_new_student_name,
                    class_name="border border-gray-300 rounded-lg px-3 py-2 mb-2 w-full"
                ),
                rx.input(
                    placeholder="Öğrenci Numarası",
                    value=StudentsState.new_student_id,
                    on_change=StudentsState.set_new_student_id,
                    class_name="border border-gray-300 rounded-lg px-3 py-2 mb-2 w-full"
                ),
                rx.upload(
                    rx.vstack(
                        rx.button(
                            "Öğrenci Fotoğrafı Seç",
                            class_name="w-full"
                        ),
                        rx.text(
                            "Sürükleyip bırakın veya yüklemek için tıklayın",
                            class_name="text-sm text-gray-500"
                        ),
                        rx.foreach(
                            rx.selected_files("upload1"),
                            lambda file: rx.text(file)
                        ),
                    ),
                    id="upload1",
                    border="2px dashed #cbd5e0",
                    padding="2em",
                    width="100%",
                    margin_bottom="1em",
                ),
                rx.el.div(
                    rx.button(
                        "Fotoğraf Yükle",
                        on_click=StudentsState.handle_upload(rx.upload_files(upload_id="upload1")),
                        class_name="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg text-sm font-semibold"
                    ),
                    class_name="flex justify-center mb-4"
                ),
                rx.cond(
                    StudentsState.uploaded_photo,
                    rx.vstack(
                        rx.text("✓ Fotoğraf yüklendi", class_name="text-blue-600 font-semibold mb-2"),
                        rx.image(
                            src=StudentsState.uploaded_photo,
                            alt="Uploaded photo preview",
                            class_name="w-32 h-32 object-cover rounded-lg mb-4"
                        ),
                    ),
                    rx.text(""),
                ),
                rx.el.div(
                    rx.button(
                        "Öğrenci Ekle",
                        on_click=StudentsState.add_student,
                        class_name="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-semibold shadow-md hover:shadow-lg transition-all"
                    ),
                    class_name="flex justify-center mt-4"
                ),
                class_name="bg-white p-6 rounded-lg shadow-md mb-8"
            ),
        ),

        # Students List
        rx.el.div(
            rx.el.h2("Öğrenci Listesi", class_name="text-xl font-semibold mb-4 text-blue-900"),
            rx.el.div(
                rx.foreach(
                    StudentsState.students,
                    lambda student: rx.el.div(
                        rx.el.div(
                            rx.el.span(f"Ad: {student['name']} - ID: {student['student_id']}", class_name="text-gray-700"),
                            rx.button(
                                "Sil",
                                on_click=lambda: StudentsState.delete_student(student['id']),
                                class_name="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-semibold"
                            ),
                            class_name="flex justify-between items-center p-4 border border-gray-200 rounded-lg mb-2"
                        ),
                        rx.cond(
                            student["photo_path"],
                            rx.image(
                                src=f"/{student['photo_path']}",
                                alt=f"Photo of {student['name']}",
                                class_name="w-20 h-20 object-cover rounded-lg mt-2"
                            ),
                            rx.text("Fotoğraf yok", class_name="text-gray-500 mt-2")
                        ),
                        class_name="bg-gray-50 p-4 rounded-lg mb-4"
                    )
                ),
                class_name="bg-white p-6 rounded-lg shadow-md"
            ),
        ),

        class_name="max-w-4xl mx-auto px-4 py-8",
        bg="linear-gradient(to bottom right, #f9fafb, #eff6ff)"
    )