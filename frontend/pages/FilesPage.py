from PyQt5.QtWidgets import QLabel, QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout, QMessageBox
from PyQt5.Qt import QSizePolicy
from PyQt5.QtCore import Qt

from frontend.pages.BaseClassPage import *
from frontend.widgets.BasicWidgets import Button

class FilesPage(BaseClassPage):
    def __init__(self):
        super().__init__()

    title = "Files"

    def initUI(self, layout):
        # Local widgets
        self.table = QTableWidget(0, 3)     # (rows, cols) table to display files
        topHLayout = QHBoxLayout()          # Horizontal layout for top buttons
        
        # Connect signals
        self.table.itemChanged.connect(self.on_table_edit)

        # Setup table widget
        self.table.setHorizontalHeaderLabels(["    Name    ", "    Status    ", "File Path"])
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Column 0 will stretch
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Column 1 will resize to its contents
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Column 2 will resize to its contents

        # Setup Top layout and add Buttons with their callbacks
        topHLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        topHLayout.addWidget( Button("Add Files", on_click=self.popup_file_explorer_dialog) )
        topHLayout.addSpacing(20)
        topHLayout.addWidget( Button("Clear Files", on_click=self.clear_files_from_table) )
        topHLayout.addStretch(1)

        # Add widgets to the page layout
        layout.addLayout(topHLayout)
        layout.addWidget(self.table)


    def clear_files_from_table(self):
        self.model.clear_files()
        self.update_table()


    # Import the files listed in the table
    def import_files(self):
        self.model.import_files()
        self.update_table()


    # Open a file explorer dialog to select files
    def popup_file_explorer_dialog(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter(self.model.file_handler.name_filter) 
        try:
            if file_dialog.exec_():                                 # Search for files
                list_of_filepaths = file_dialog.selectedFiles()
                self.model.file_handler.add(list_of_filepaths)
        except ValueError as e:
            QMessageBox.critical(self, 'Error', str(e))
            self.update_table()
            return
        file_dialog.close()
        self.update_table()                                         # Show them
        self.import_files()                                         # Import them
        self.update_table()                                         # Show them again


    # Callback for when a table item is edited
    def on_table_edit(self, item):
        if item.column() != 0:  # only allow editing the 'name' column
            return

        # check if the proposed name already exists, if so, don't allow the change
        try:
            newname = item.text()
            index = item.row()
            fmeta = self.model.file_handler.file_at(index)
            self.model.file_handler.rename(fmeta, newname)
        except ValueError as e:
            QMessageBox.critical(self, 'Error', str(e))
            
        self.update_table()


    # Update the table with the current file metadata
    def update_table(self):
        self.table.blockSignals(True)  # block signals to avoid triggering on_table_edit
        
        all_files = self.model.file_handler.all_files()
        self.table.setRowCount(len(all_files))
    
        for i, fmeta in enumerate(all_files):
            item0 = QTableWidgetItem(fmeta.name)
            item0.setFlags(item0.flags() | Qt.ItemIsEditable)  # make item editable
            self.table.setItem(i, 0, item0)
    
            item1 = QTableWidgetItem(fmeta.status)
            item1.setFlags(item1.flags() & ~Qt.ItemIsEditable) # make item read-only
            item1.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 1, item1)
    
            item2 = QTableWidgetItem(fmeta.path)
            item2.setFlags(item2.flags() & ~Qt.ItemIsEditable)  # make item read-only
            self.table.setItem(i, 2, item2)
        
        self.table.blockSignals(False)


    def on_tab_focus(self):
        self.update_table()