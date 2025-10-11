try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from shiboken6 import wrapInstance
except:
    from PySide2 import QtCore, QtGui, QtWidgets
    from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui
from . import utill as util

class LightingMaker(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Lighting@Maker")
        self.setFixedSize(420, 650)
        self.setStyleSheet("""
            QDialog {
                background-color: #1E1E1E;
                color: white;
                font-family: 'Segoe UI';
                font-size: 13px;
            }
            QPushButton {
                border-radius: 6px;
                padding: 6px 12px;
                background-color: #333;
            }
            QPushButton:checked {
                background-color: #7A33FF;  /* สีที่ใช้เมื่อปุ่มถูกเลือก */
                color: white;
                border: 2px solid #7A33FF;
            }
            QLineEdit {
                background-color: #333;
                color: white;
                border-radius: 4px;
                padding: 3px;
            }
            QLabel {
                color: white;
            }
        """)

        self.main_layout = QtWidgets.QVBoxLayout(self)

        type_box = QtWidgets.QGroupBox("TypeLight")
        type_box.setStyleSheet("QGroupBox {font-weight: bold; border: 1px solid gray; margin-top: 6px;}") 
        type_layout = QtWidgets.QVBoxLayout(type_box)

        self.light_buttons = {}
        grid = QtWidgets.QGridLayout()
        light_types = [
            ("Area Light", "aiAreaLight"),
            ("Skydome Light", "aiSkyDomeLight"),
            ("Mesh Light", "aiMeshLight"),
            ("Photometric", "aiPhotometricLight"),
            ("Light Portal", "aiLightPortal"),
            ("Physical Sky", "aiPhysicalSky"),
        ]
        
        for i, (label, node) in enumerate(light_types):
            btn = QtWidgets.QPushButton(label)
            btn.setCheckable(True)
            btn.clicked.connect(self.get_light_type_function(node, btn))
            grid.addWidget(btn, i // 3, i % 3)
            self.light_buttons[node] = btn
        type_layout.addLayout(grid)
        self.main_layout.addWidget(type_box)

        timezone_box = QtWidgets.QGroupBox("Timezone")
        timezone_box.setStyleSheet("QGroupBox {font-weight: bold; border: 1px solid gray; margin-top: 6px;}")
        tz_layout = QtWidgets.QHBoxLayout(timezone_box)

        self.tz_buttons = {}
        tz_options = ["Morning", "Noon", "Evening", "Night"]

        for label in tz_options:
            btn = QtWidgets.QPushButton(label)
            btn.setCheckable(True)
            btn.clicked.connect(self.get_timezone_function(label, btn))
            tz_layout.addWidget(btn)
            self.tz_buttons[label] = btn

        self.main_layout.addWidget(timezone_box)

        setting_box = QtWidgets.QGroupBox("Light Settings")
        setting_box.setStyleSheet("QGroupBox {font-weight: bold; border: 1px solid gray; margin-top: 6px;}") 
        setting_layout = QtWidgets.QFormLayout(setting_box)

        self.intensity_spin = QtWidgets.QDoubleSpinBox()
        self.intensity_spin.setRange(0.0, 10000.0)
        self.intensity_spin.setValue(1.0)

        self.exposure_spin = QtWidgets.QDoubleSpinBox()
        self.exposure_spin.setRange(-10.0, 20.0)
        self.exposure_spin.setValue(0.0)

        self.color_button = QtWidgets.QPushButton("Pick Color")
        self.color_button.clicked.connect(self.pick_color)
        self.color_button.setStyleSheet("background-color: white; color: black;")

        setting_layout.addRow("Intensity:", self.intensity_spin)
        setting_layout.addRow("Exposure:", self.exposure_spin)
        setting_layout.addRow("Color:", self.color_button)
        self.main_layout.addWidget(setting_box)

        name_layout = QtWidgets.QHBoxLayout()
        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText("Light name...")
        name_layout.addWidget(QtWidgets.QLabel("Name:"))
        name_layout.addWidget(self.name_edit)
        self.main_layout.addLayout(name_layout)

        btn_layout = QtWidgets.QHBoxLayout()
        self.create_btn = QtWidgets.QPushButton("🟣 Create")
        self.create_btn.setStyleSheet("background-color: #7A33FF; color: white; font-weight: bold;")
        self.create_btn.clicked.connect(self.create_light)

        self.cancel_btn = QtWidgets.QPushButton("🔴 Cancel")
        self.cancel_btn.setStyleSheet("background-color: #FF3366; color: white; font-weight: bold;")
        self.cancel_btn.clicked.connect(self.close)

        btn_layout.addStretch()
        btn_layout.addWidget(self.create_btn)
        btn_layout.addWidget(self.cancel_btn)
        self.main_layout.addLayout(btn_layout)

        self.selected_type = "aiSkyDomeLight"
        self.selected_timezone = "Noon"
        self.color = QtGui.QColor(255, 255, 255)

        if not cmds.pluginInfo("mtoa", query=True, loaded=True):
            cmds.loadPlugin("mtoa")
        cmds.setAttr("defaultRenderGlobals.currentRenderer", "arnold", type="string")

    def get_light_type_function(self, node_type, btn):
        def select_light_type():
            for n, b in self.light_buttons.items():
                b.setChecked(False)
                b.setStyleSheet("background-color: #333;")  # ปรับสไตล์ปุ่มที่ไม่ได้เลือก
            btn.setChecked(True)
            btn.setStyleSheet("background-color: #7A33FF; color: white; border: 2px solid #7A33FF;")  # ปรับสไตล์ปุ่มที่เลือก
            self.selected_type = node_type
        return select_light_type

    def get_timezone_function(self, tz, btn):
        def select_timezone():
            for t, b in self.tz_buttons.items():
                b.setChecked(False)
                b.setStyleSheet("background-color: #333;")  # ปรับสไตล์ปุ่มที่ไม่ได้เลือก
            btn.setChecked(True)
            btn.setStyleSheet("background-color: #7A33FF; color: white; border: 2px solid #7A33FF;")  # ปรับสไตล์ปุ่มที่เลือก
            self.selected_timezone = tz

            intensity, color = util.apply_timezone_preset(tz)
            self.intensity_spin.setValue(intensity)
            self.color = QtGui.QColor.fromRgbF(*color)
            self.color_button.setStyleSheet(f"background-color: {self.color.name()};")
        return select_timezone

    def pick_color(self):
        color = QtWidgets.QColorDialog.getColor(self.color, self, "Select Light Color")
        if color.isValid():
            self.color = color
            self.color_button.setStyleSheet(f"background-color: {color.name()};")

    def create_light(self):
        name = self.name_edit.text().strip()
        light_type = self.selected_type

        light = util.create_light(light_type, name)
        if not light:
            return

        color = (self.color.redF(), self.color.greenF(), self.color.blueF())
        util.set_light_attributes(
            light,
            intensity=self.intensity_spin.value(),
            exposure=self.exposure_spin.value(),
            color=color
        )

        print(f"✅ Created {light_type}: {light} [{self.selected_timezone}]")
        self.close()

def run():
    for w in QtWidgets.QApplication.topLevelWidgets():
        if isinstance(w, LightingMaker):
            w.close()
    ptr = wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)
    ui = LightingMaker(parent=ptr)
    ui.show()
