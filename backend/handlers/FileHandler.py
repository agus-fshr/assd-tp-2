

class FileMetadataObject:
    def __init__(self, path):
        self.complete_filepath = path
        self.file_reference_name = path.split("/")[-1]
        self.file_extension = self.name.split(".")[-1].lower()
        self.file_import_status = "Pending"

    @property
    def path(self):
        return self.complete_filepath
    
    @property
    def name(self):
        return self.file_reference_name
    
    @property
    def filename(self):
        return self.complete_filepath.split("/")[-1]
    
    @property
    def ext(self):
        return self.file_extension
    @property
    def extension(self):
        return self.file_extension

    @property
    def status(self):
        return self.file_import_status
    
    def rename(self, new_name):
        self.file_reference_name = new_name

    def set_error(self):
        self.file_import_status = "Error"

    def set_ok(self):
        self.file_import_status = "OK"



class FileImportHandler:
    def __init__(self, fileTypes="All Files (*.*)"):
        self.file_meta_list = []                 # list of FileMetadataObject objects
        self.fileIndexesByType = {}             # dict of lists of indexes of files by type
        self.fileTypes = fileTypes

    @property
    def types(self):
        return self.fileTypes

    def pending_files(self, ext=""):
        filesMeta = []
        for fmeta in self.file_meta_list:
            if fmeta.status == "Pending":
                if ext == "" or fmeta.extension == ext:
                    filesMeta.append(fmeta)
        return filesMeta

    def get_file(self, name, path):
        for fmeta in self.file_meta_list:
            if fmeta.name == name and fmeta.path == path:
                return fmeta
        return None


    def available_files(self, ext=""):
        filesMeta = []
        for fmeta in self.file_meta_list:
            if fmeta.status == "OK":
                if ext == "" or fmeta.extension == ext:
                    filesMeta.append(fmeta)
        return filesMeta            

    # Add files to the list of files pending to import
    def add(self, filepaths=[]):
        for path in filepaths:
            self.add_file(path)

    def add_file(self, path):
        new_file = FileMetadataObject(path)
        existing_files_indexes = self.fileIndexesByType.get(new_file.extension, [])
        for i in existing_files_indexes:
            if self.file_meta_list[i].name == new_file.name:
                raise ValueError(f"File named '{new_file.name}' already exists in the list")
        self.file_meta_list.append(new_file)
        self.fileIndexesByType.setdefault(new_file.extension, []).append(len(self.file_meta_list)-1)


    def rename(self, fmeta, new_name):
        # Check that the name is not empty
        if new_name == "":
            raise ValueError("Name cannot be empty")
        
        index = self.file_meta_list.index(fmeta)

        # Check that the name is not already in the list with the same extension
        existingIndexes = self.fileIndexesByType.get(fmeta.extension, [])
        for i in existingIndexes:
            if i != index and self.file_meta_list[i].name == fmeta.name:
                raise ValueError(f"File named '{fmeta.name}' already exists with the same extension")

        # Update the file metadata
        self.file_meta_list[index].rename(new_name)

    def delete(self, fmeta):
        index = self.file_meta_list.index(fmeta)
        self.fileIndexesByType[fmeta.extension].remove(index)
        del self.file_meta_list[index]

    def clear(self, extension=""):
        if extension == "":
            self.file_meta_list = []
            self.fileIndexesByType = {}
        else:
            for i in self.fileIndexesByType.get(extension, []):
                del self.file_meta_list[i]
            del self.fileIndexesByType[extension]
    
    def all_files(self, extension=""):
        if extension != "":
            return [self.file_meta_list[i] for i in self.fileIndexesByType.get(extension, [])]
        return self.file_meta_list
