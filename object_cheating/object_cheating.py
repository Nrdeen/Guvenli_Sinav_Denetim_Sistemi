import reflex as rx
from object_cheating.components.camera_feed import camera_feed
from object_cheating.components.camera_selector import camera_selector
from object_cheating.components.controls import controls
from object_cheating.components.treshold import threshold
from object_cheating.components.stats_panel import stats_panel
from object_cheating.components.behavior_panel import behavior_panel
from object_cheating.components.coordinate_panel import coordinate_panel
from object_cheating.components.table import tables_v2
from object_cheating.components.input_panel import input_panel
from object_cheating.components.warning_dialog import warning_dialog
from object_cheating.components.delete_dialog import delete_dialog
from object_cheating.pages.home import home_page
from object_cheating.pages.guvenli_sinav import guvenli_sinav_page
from object_cheating.pages.live_dashboard import live_dashboard
from object_cheating.pages.teacher_login import teacher_login_page
from object_cheating.pages.admin_dashboard import admin_dashboard_page
from object_cheating.pages.create_exam import create_exam_page
from object_cheating.pages.students_management import students_management_page
from object_cheating.pages.student_login import student_login_page
from object_cheating.pages.students import students_page
from object_cheating.states.camera_state import CameraState
from object_cheating.pages.system_dashboard import system_dashboard_page

def detection_page() -> rx.Component:
    return rx.box(
        # Warning dialog at root level for proper overlay
        warning_dialog(),
        delete_dialog(),
        rx.el.div(
            rx.el.div(
                # Back button and Students button
                rx.el.div(
                    rx.link(
                        rx.button(
                            "← Ana Sayfaya Dön",
                            class_name="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg mb-4"
                        ),
                        href="/"
                    ),
                    rx.link(
                        rx.button(
                            " Öğrenciler ",
                            class_name="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg mb-4 ml-4"
                        ),
                        href="/students"
                    ),
                    class_name="mb-4 flex flex-wrap gap-2"
                ),
                rx.el.h1(
                    "Sınıf İçi Sınav Gözetim Sistemi",
                    class_name="text-3xl font-bold text-blue-900 mb-8 text-center"
                ),
                rx.el.div(
                    # Left Section: Camera Feed, Controls, and Table in separate sections
                    rx.el.div(
                        rx.el.div(
                            camera_selector(),
                            camera_feed(),
                            controls(),
                            class_name="bg-white p-4 rounded-lg shadow-md space-y-4 border border-gray-200"
                        ),
                        rx.el.div(
                            tables_v2(),
                            class_name="bg-white p-4 rounded-lg shadow-md space-y-4 border border-gray-200"
                        ),
                        class_name="w-full lg:w-2/3 lg:pr-4 space-y-4 mb-4 lg:mb-0"
                    ),
                    # Right Section: Threshold, Show Label Name, Behavior, Coordinate Panels
                    rx.el.div(
                        threshold(),
                        stats_panel(),
                        behavior_panel(),
                        coordinate_panel(),
                        input_panel(),
                        class_name="w-full lg:w-1/3 space-y-4"
                    ),
                    class_name="flex flex-col lg:flex-row"
                ),
                class_name="max-w-7xl mx-auto px-4 py-8"
            ),
            class_name="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50",
            on_mount=CameraState.auto_start_camera
        ),
    )

app = rx.App(
    theme=rx.theme(
        accent_color="grass",
    )
)

# Add pages
app.add_page(home_page, route="/")
app.add_page(detection_page, route="/detection")
app.add_page(students_page, route="/students")
app.add_page(guvenli_sinav_page, route="/guvenli-sinav")
app.add_page(live_dashboard, route="/dashboard")
app.add_page(teacher_login_page, route="/teacher-login")
app.add_page(admin_dashboard_page, route="/admin/dashboard")
app.add_page(create_exam_page, route="/create-exam")
app.add_page(students_management_page, route="/students-management")
app.add_page(admin_dashboard_page, route="/admin-dashboard")
app.add_page(system_dashboard_page, route="/system-dashboard")
app.add_page(student_login_page, route="/student-login")
from object_cheating.pages.student_exam import student_exam_page
# Use a unique dynamic route name to avoid shadowing other State vars
app.add_page(student_exam_page, route="/exam/[student_exam_code]")
# Alias routes to handle alternate paths/typos used by some users
app.add_page(student_exam_page, route="/siber-guvenlik/[student_exam_code]")
app.add_page(student_exam_page, route="/Siber-Guvenlik/[student_exam_code]")