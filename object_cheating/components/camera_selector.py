"""
مكون اختيار الكاميرا - معطل
Camera Selector Component - Disabled
النظام يختار كاميرا Logitech تلقائياً
"""
import reflex as rx
from object_cheating.states.camera_state import CameraState

def camera_selector() -> rx.Component:
    """مكون مخفي - الكاميرا تُختار تلقائياً"""
    # إرجاع fragment فارغ لإخفاء المكون تماماً
    return rx.fragment()