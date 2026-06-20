from Components.SystemInfo import BoxInfo
from Components.config import config
from Tools.Directories import fileWriteLine, fileReadLine
from Plugins.Plugin import PluginDescriptor
from enigma import eAVControl
import os
import threading

MODULE_NAME = "OSDCalibrationStartup"


def _write_proc_hex(path, value):
    try:
        fileWriteLine(path, "%08x\n" % int(value), source=MODULE_NAME)
        return True
    except Exception as e:
        print("[%s] write to %s failed: %s" % (MODULE_NAME, path, e))
        return False


def setConfiguredPosition():
    """
    Apply saved config.osd values to the framebuffer/sysfs so OSD position/size/alpha/3D are restored on GUI start.
    """
    try:
        # Prefer Amlogic/sysfs path when available (supports free_scale/window_axis)
        if BoxInfo.getItem("AmlogicFamily") or BoxInfo.getItem("CanChangeOsdPositionAML"):
            try:
                value = "%s %s %s %s" % (config.osd.dst_left.value, config.osd.dst_top.value, config.osd.dst_width.value, config.osd.dst_height.value)
                print("[%s] Write to /sys/class/graphics/fb0/window_axis: %s" % (MODULE_NAME, value))
                fileWriteLine("/sys/class/graphics/fb0/window_axis", value, source=MODULE_NAME)
                fileWriteLine("/sys/class/graphics/fb0/free_scale", "0x10001", source=MODULE_NAME)
            except Exception as e:
                print("[%s] Write window_axis/free_scale failed: %s" % (MODULE_NAME, e))
        else:
            # Write dst_* registers (hex)
            _write_proc_hex("/proc/stb/fb/dst_left", config.osd.dst_left.value)
            _write_proc_hex("/proc/stb/fb/dst_width", config.osd.dst_width.value)
            _write_proc_hex("/proc/stb/fb/dst_top", config.osd.dst_top.value)
            _write_proc_hex("/proc/stb/fb/dst_height", config.osd.dst_height.value)

            # Some kernels require an explicit apply
            try:
                if os.path.exists("/proc/stb/fb/dst_apply"):
                    fileWriteLine("/proc/stb/fb/dst_apply", "1", source=MODULE_NAME)
                    print("[%s] Wrote dst_apply to apply dst_* settings" % MODULE_NAME)
            except Exception as e:
                print("[%s] write dst_apply failed: %s" % (MODULE_NAME, e))

        # OSD alpha
        try:
            if hasattr(config, "av") and eAVControl.getInstance().hasOSDAlpha():
                try:
                    alpha = int(config.av.osd_alpha.value)
                    print("[%s] Setting OSD alpha to %d" % (MODULE_NAME, alpha))
                    try:
                        eAVControl.getInstance().setOSDAlpha(alpha)
                    except Exception as e:
                        print("[%s] setOSDAlpha call failed: %s" % (MODULE_NAME, e))
                except Exception as e:
                    print("[%s] reading alpha value failed: %s" % (MODULE_NAME, e))
        except Exception as e:
            print("[%s] OSD alpha apply failed: %s" % (MODULE_NAME, e))

        # 3D mode / znorm
        try:
            if os.path.exists("/proc/stb/fb/3dmode"):
                # read configured value
                try:
                    value = config.osd.threeDmode.value
                except Exception:
                    value = ""

                # read choices if possible
                try:
                    choices = fileReadLine("/proc/stb/fb/3dmode_choices", "", source=MODULE_NAME).split()
                except Exception:
                    choices = []

                # map names if needed
                if value and value not in choices:
                    if value == "sidebyside":
                        mapped = "sbs"
                    elif value == "topandbottom":
                        mapped = "tab"
                    elif value == "auto":
                        mapped = "off"
                    else:
                        mapped = value
                    value_to_write = mapped
                else:
                    value_to_write = value

                # write 3dmode
                try:
                    print("[%s] Write 3dmode: %s" % (MODULE_NAME, value_to_write))
                    fileWriteLine("/proc/stb/fb/3dmode", value_to_write, source=MODULE_NAME)
                except Exception as e:
                    print("[%s] Write 3dmode failed: %s" % (MODULE_NAME, e))

                # write znorm
                try:
                    zn = int(config.osd.threeDznorm.value)
                    print("[%s] Write znorm: %d" % (MODULE_NAME, zn))
                    fileWriteLine("/proc/stb/fb/znorm", str(zn), source=MODULE_NAME)
                except Exception as e:
                    print("[%s] Write znorm failed: %s" % (MODULE_NAME, e))
        except Exception as e:
            print("[%s] 3D apply failed: %s" % (MODULE_NAME, e))

    except Exception as e:
        print("[%s] setConfiguredPosition general failure: %s" % (MODULE_NAME, e))


def _schedule_reapplies(delays=(0.5, 1.5, 3.0)):
    """
    Schedule repeated calls to setConfiguredPosition at the specified delays (seconds).
    """
    for d in delays:
        try:
            threading.Timer(d, setConfiguredPosition).start()
        except Exception as e:
            print("[%s] scheduling reapply at %.1fs failed: %s" % (MODULE_NAME, d, e))


def startup(reason, **kwargs):
    # Apply immediately, and schedule several reapplies in case something else overwrites settings later.
    setConfiguredPosition()
    _schedule_reapplies()


def Plugins(**kwargs):
    return [PluginDescriptor(name="OSD Calibration startup", where=PluginDescriptor.WHERE_SESSIONSTART, fnc=startup)]
