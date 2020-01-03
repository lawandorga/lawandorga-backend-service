#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2020  Dominik Walser
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>

import filecmp
from django.test import SimpleTestCase

from backend.static.encrypted_storage import EncryptedStorage
from backend.static.encryption import AESEncryption


class EncryptedStorageTests(SimpleTestCase):
    def test_up_download_with_encryption(self):
        key = 'secret password'
        iv = AESEncryption.generate_iv()
        file = 'test_files/test_file.png'
        s3_folder = 'tests'
        EncryptedStorage.encrypt_file_and_upload_to_s3(file, key, iv, s3_folder)

        s3_key = 'tests/test_file.png.enc'

        EncryptedStorage.download_from_s3_and_decrypt_file(s3_key, key, iv, 'test_files',
                                                           'test_files/test_file_downloaded_decrypted.png.enc')

        self.assertTrue(filecmp.cmp('test_files/test_file.png', 'test_files/test_file_downloaded_decrypted.png'))

    def test_up_download_with_encryption_big_video(self):
        key = 'secret password'
        iv = AESEncryption.generate_iv()
        file = 'test_files/big_video.mp4'
        s3_folder = 'tests'
        EncryptedStorage.encrypt_file_and_upload_to_s3(file, key, iv, s3_folder)

        s3_key = 'tests/big_video.mp4.enc'

        EncryptedStorage.download_from_s3_and_decrypt_file(s3_key, key, iv, 'test_files',
                                                           'test_files/big_video_downloaded_decrypted.mp4.enc')

        self.assertTrue(filecmp.cmp('test_files/big_video.mp4', 'test_files/big_video_downloaded_decrypted.mp4'))
