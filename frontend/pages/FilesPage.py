from PyQt5.QtWidgets import QLabel, QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout, QMessageBox
from PyQt5.Qt import QSizePolicy
from PyQt5.QtCore import Qt

from frontend.pages.PageBaseClass import *
from frontend.widgets.BasicWidgets import Button

class FilesPage(PageBaseClass):
    def __init__(self):
        super().__init__()  # Init base class
        self.title = "File Explorer"

    def initUI(self, layout):
        # Local widgets
        self.table = QTableWidget(0, 3) # (rows, columns) table to display files
        topHLayout = QHBoxLayout()      # Horizontal layout for top buttons
        
        # Connect signals
        self.table.itemChanged.connect(self.on_table_edit)

        # Top layout
        topHLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        topHLayout.addWidget(Button("Add Files", on_click=self.popup_file_dialog))
        topHLayout.addWidget(Button("Clear Files", on_click=self.clear_files))
        topHLayout.addSpacing(20)
        topHLayout.addWidget(Button("Import Files", on_click=self.import_files))
        topHLayout.addStretch(1)

        # Setup table widget
        self.table.setHorizontalHeaderLabels(["    Name    ", "    Status    ", "File Path"])
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Column 0 will stretch
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Column 1 will resize to its contents
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Column 2 will resize to its contents

        # Add widgets to page layout
        layout.addWidget(QLabel("Load MIDI Files"))
        layout.addLayout(topHLayout)
        layout.addWidget(self.table)


    def clear_files(self):
        self.model.file_metadata = []
        self.update_table()


    def import_files(self):
        self.model.import_files()
        self.update_table()


    def popup_file_dialog(self):
        file_dialog = QFileDialog() # Search for files
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("MIDI Files (*.mid);;All Files (*.*)")
        try:
            if file_dialog.exec_():
                self.model.add_files(file_dialog.selectedFiles())
        except ValueError as e:
            QMessageBox.critical(self, 'Error', str(e))

        self.update_table()


    # Callback for when a cell in the table is edited
    def on_table_edit(self, item):
        if item.column() != 0:  # only allow editing the 'name' column
            return
        # check if the proposed name already exists
        for i, file_info in enumerate(self.model.file_metadata):
            if i == item.row():
                continue
            if file_info["name"] == item.text():
                QMessageBox.critical(self, 'Error', f"File named '{item.text()}' already exists in the list")
                item.setText(self.model.file_metadata[i]["name"])
                self.update_table()
                return
        self.model.file_metadata[item.row()]["name"] = item.text()

    # Update the table with the current file metadata
    def update_table(self):
        self.table.setRowCount(len(self.model.file_metadata))
    
        for i, file_info in enumerate(self.model.file_metadata):
            item0 = QTableWidgetItem(file_info["name"])
            item0.setFlags(item0.flags() | Qt.ItemIsEditable)  # make item editable
            self.table.setItem(i, 0, item0)
    
            item1 = QTableWidgetItem(file_info["status"])
            item1.setFlags(item1.flags() & ~Qt.ItemIsEditable) # make item read-only
            item1.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 1, item1)
    
            item2 = QTableWidgetItem(file_info["path"])
            item2.setFlags(item2.flags() & ~Qt.ItemIsEditable)  # make item read-only
            self.table.setItem(i, 2, item2)


    def on_tab_focus(self):
        self.update_table()