from core.files_new.use_cases.file import (
    delete_file,
    migrate_old_files,
    upload_a_file,
    upload_multiple_files,
)

USECASES = {
    "files/upload_multiple_files": upload_multiple_files,
    "files/upload_file": upload_a_file,
    "files/delete_file": delete_file,
    "files/migrate_old_files": migrate_old_files,
}
