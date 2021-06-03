# TODO refactor this into classes, 1 storage folders specific, 1 general filename manipulation


def clean_string(string):
    special_char_map = {ord('ä'): 'ae', ord('ü'): 'ue', ord('ö'): 'oe', ord('ß'): 'ss', ord('Ä'): 'AE', ord('Ö'): 'OE',
                        ord('Ü'): 'UE', }
    return string.translate(special_char_map)


def clean_filename(key):
    key_parts = key.split('/')
    filename = clean_string(key_parts[-1])
    key = '/'.join(key_parts[:-1] + [filename])
    return key


def get_storage_folder_encrypted_record_document(rlc_id: int, record_id: int) -> str:
    return "rlcs/" + str(rlc_id) + "/encrypted_records/" + str(record_id) + "/"


def get_storage_base_files_folder(rlc_id: int) -> str:
    return "rlcs/" + str(rlc_id) + "/"
