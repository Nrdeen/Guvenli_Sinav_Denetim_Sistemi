import reflex as rx
from object_cheating.states.camera_state import CameraState

def input_panel() -> rx.Component:
    button_style = "bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 w-full text-center rounded-lg shadow-md"
    disabled_style = "bg-gray-400 text-gray-600 px-6 py-2 w-full text-center rounded-lg cursor-not-allowed"
    active_camera_style = "bg-red-500 hover:bg-red-600 text-white px-6 py-2 w-full text-center rounded-lg shadow-md"

    # Check if image or video is active (not camera)
    other_media_active = rx.cond(
        (CameraState.uploaded_image != "") | CameraState.video_playing,
        True,
        False
    )

    return rx.el.div(
        rx.el.div(
            rx.el.h3("Medya Kontrolleri", class_name="text-lg font-semibold mb-2 text-blue-900"),
            # First row (Image - Video)
            rx.el.div(
                rx.upload(
                    rx.button(
                        "📷 Resim",
                        class_name=rx.cond(
                            CameraState.camera_active | other_media_active,
                            disabled_style,
                            button_style
                        ),
                    ),
                    multiple=False,
                    border="none",
                    padding="0",
                    margin="0",
                    id="image_upload",
                    style={"border": "none"},
                    disabled=CameraState.camera_active | other_media_active,
                ),
                rx.button(
                    "Upload",
                    on_click=CameraState.handle_image_upload(
                        rx.upload_files(upload_id="image_upload")
                    ),
                    class_name="hidden",
                    id="upload_button",
                ),
                rx.script("""
                    document.addEventListener('change', function(e) {
                        if (e.target && e.target.closest('#image_upload')) {
                            setTimeout(() => {
                                document.getElementById('upload_button').click();
                            }, 100);
                        }
                    });
                """),
                rx.upload(
                    rx.button(
                        "🎬 Video",
                        class_name=rx.cond(
                            CameraState.camera_active | other_media_active,
                            disabled_style,
                            button_style
                        ),
                    ),
                    multiple=False,
                    border="none",
                    padding="0",
                    margin="0",
                    id="video_upload",
                    style={"border": "none"},
                    disabled=CameraState.camera_active | other_media_active,
                ),
                rx.button(
                    "Upload",
                    on_click=CameraState.handle_video_upload(
                        rx.upload_files(upload_id="video_upload")
                    ),
                    class_name="hidden",
                    id="upload_video_button",
                ),
                rx.script("""
                    document.addEventListener('change', function(e) {
                        if (e.target && e.target.closest('#video_upload')) {
                            setTimeout(() => {
                                document.getElementById('upload_video_button').click();
                            }, 100);
                        }
                    });
                """),
                class_name="grid grid-cols-2 gap-4 w-full"
            ),
            # Second row (Webcam - Save)
            rx.el.div(
                rx.button(
                    rx.cond(
                        CameraState.camera_active,
                        "⏹️ Kamerayı Durdur",
                        "🎥 Web Kamera"
                    ),
                    on_click=CameraState.toggle_camera,
                    class_name=rx.cond(
                        CameraState.camera_active,
                        active_camera_style,
                        rx.cond(
                            other_media_active,
                            disabled_style,
                            button_style
                        )
                    ),
                    disabled=other_media_active
                ),
                rx.button("💾 Kaydet", 
                          on_click=CameraState.save_current_frame, 
                          class_name=rx.cond(
                            CameraState.current_frame != "",
                            button_style,
                            disabled_style
                          ),
                          disabled=CameraState.current_frame == ""
                ),
                class_name="grid grid-cols-2 gap-4 w-full mt-4"
            ),
            # Third row (Clear, centered)
            rx.el.div(
                rx.button(
                    "🗑️ Temizle",
                    on_click=CameraState.try_clear_camera,
                    class_name=rx.cond(
                        CameraState.current_frame != "",
                        button_style,
                        disabled_style
                    ),
                    disabled=CameraState.current_frame == ""
                ),
                class_name="flex justify-center w-full mt-4"
            ),
            class_name="w-full p-6 bg-white rounded-lg shadow-md max-w-md mx-auto border border-blue-200"
        )
    )