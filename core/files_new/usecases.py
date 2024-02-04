from core.files_new.use_cases.file import (
    delete_file,
    upload_a_file,
    upload_multiple_files,
)

USECASES = {
    "files/upload_multiple_files": upload_multiple_files,
    "files/upload_file": upload_a_file,
    "files/delete_file": delete_file,
}
