"""

Utilities to dump:
    - % time HW Composition is enabled vs. 2D Composition (C2D)
    - GPU clock frequency
    - # of layers composited per frame by SurfaceFlinger
    - layer information - source/dest crop, scaling factor, composition type (GLES or overlay)
        - see `adb shell dumpsys SurfaceFlinger`
        - Help understand when to use MDP or GLES (GPU composition)
    - analyze Open GL ES trace to understand commands sent to HW.

"""