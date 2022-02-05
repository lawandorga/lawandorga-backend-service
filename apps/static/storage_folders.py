def get_storage_folder_encrypted_record_document(rlc_id: int, record_id: int) -> str:
    return "rlcs/" + str(rlc_id) + "/encrypted_records/" + str(record_id) + "/"


def get_storage_base_files_folder(rlc_id: int) -> str:
    return "rlcs/" + str(rlc_id) + "/"
