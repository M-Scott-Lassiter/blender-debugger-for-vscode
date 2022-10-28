import os

import bpy

from .debug_server import check_for_debugpy

class DebuggerPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    path: bpy.props.StringProperty(
        name="Location of debugpy (site-packages folder)",
        subtype="DIR_PATH",
        default=check_for_debugpy()
    )

    timeout: bpy.props.IntProperty(
        name="Timeout",
        default=20
    )

    port: bpy.props.IntProperty(
        name="Port",
        min=0,
        max=65535,
        default=5678
    )

    debugpath: bpy.props.StringProperty(
        name="File or Folder to Debug",
        subtype="FILE_PATH",
        default= os.path.dirname(__file__)
    )

    watch_For_Updates: bpy.props.BoolProperty(
        name="Watch for Updates",
        default=True
    )

    def draw(self, context):
        layout = self.layout
        row_path = layout
        row_path.label(text="The addon will try to auto-find the location of debugpy. If no path is found or you would like to use a different path, set it here.")
        row_path.prop(self, "path")

        row_timeout = layout.split()
        row_timeout.prop(self, "timeout")
        row_timeout.label(text="Timeout in seconds for the attach confirmation listener.")

        row_port = layout.split()
        row_port.prop(self, "port")
        row_port.label(text="Port to use. Should match port in VS Code's launch.json.")

        row_debug = layout.split()
        row_debug.prop(self, "debugpath")
        row_debug.prop(self, "watch_For_Updates")