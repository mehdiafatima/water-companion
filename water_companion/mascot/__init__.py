"""
mascot/__init__.py
"""
from water_companion.mascot.water_drop_widget import WaterDropWidget, MascotState
from water_companion.mascot.animations import (
    FloatAnimator,
    make_slide_in_animation,
    make_slide_out_animation,
    spawn_happy_particles,
    spawn_sad_particles,
)

__all__ = [
    "WaterDropWidget",
    "MascotState",
    "FloatAnimator",
    "make_slide_in_animation",
    "make_slide_out_animation",
    "spawn_happy_particles",
    "spawn_sad_particles",
]
