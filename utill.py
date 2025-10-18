import maya.cmds as cmds


def create_light(light_type, name):
    if not name:
        name = f"{light_type}_#"

    if cmds.objExists(name):
        cmds.warning(f"{name} already exists.")
        return None

    light = cmds.shadingNode(light_type, asLight=True, name=name)
    return light


def set_light_attributes(light, intensity, exposure, color):
    if cmds.objExists(light):
        cmds.setAttr(f"{light}.intensity", intensity)
        cmds.setAttr(f"{light}.aiExposure", exposure)
        cmds.setAttr(f"{light}.color", *color, type="double3")


def apply_timezone_preset(tz):
    presets = {
        "Morning": (0.8, (1.0, 0.9, 0.8)),
        "Noon": (1.0, (1.0, 1.0, 1.0)),
        "Evening": (0.6, (1.0, 0.7, 0.5)),
        "Night": (0.3, (0.6, 0.7, 1.0))
    }
    return presets.get(tz, (1.0, (1.0, 1.0, 1.0)))
