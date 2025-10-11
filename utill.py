import maya.cmds as cmds

def create_light(light_type, name=None):
    if not cmds.pluginInfo("mtoa", query=True, loaded=True):
        cmds.loadPlugin("mtoa")

    try:
        light = cmds.createNode(light_type)
    except Exception as e:
        cmds.warning(f"⚠️ Failed to create {light_type}: {e}")
        return None

    if name:
        light = cmds.rename(light, name)
    return light

def set_light_attributes(light, intensity=1.0, exposure=0.0, color=(1, 1, 1)):
    if not cmds.objExists(light):
        cmds.warning(f"Light {light} does not exist.")
        return
    try:
        cmds.setAttr(f"{light}.intensity", intensity)
        cmds.setAttr(f"{light}.exposure", exposure)
        cmds.setAttr(f"{light}.color", *color, type="double3")
    except Exception as e:
        cmds.warning(f"Error setting attributes: {e}")

def apply_timezone_preset(tz_name):
    presets = {
        "Morning": (1.5, (1.0, 0.9, 0.7)),
        "Noon": (3.0, (1.0, 1.0, 1.0)),
        "Evening": (0.8, (1.0, 0.6, 0.4)),
        "Night": (0.3, (0.6, 0.7, 1.0))
    }

    return presets.get(tz_name, (1.0, (1.0, 1.0, 1.0)))
