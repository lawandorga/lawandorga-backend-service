from core.upload.use_cases.upload import (
    create_upload_link,
    delete_upload_link,
    delete_uploaded_file,
    disable_upload_link,
    upload_data,
)

USECASES = {
    "upload/create_link": create_upload_link,
    "upload/disable_link": disable_upload_link,
    "upload/delete_link": delete_upload_link,
    "upload/upload_data": upload_data,
    "upload/delete_file": delete_uploaded_file,
}
