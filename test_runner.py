#  rlcapp - record and organization management software for refugee law clinics
#  Copyright (C) 2019  Dominik Walser
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

import subprocess
import os
import time
from watchdog.events import FileSystemEventHandler, FileCreatedEvent
from watchdog.observers import Observer


class MyFileWatcher(FileSystemEventHandler):
    def on_any_event(self, event):
        if type(event) is FileCreatedEvent:
            if 'tests' in event.src_path and 'pycache' not in event.src_path:
                to_run = event.src_path[os.getcwd().__len__() + 1:-3].replace('/', '.')
                print('i run', to_run)
                subprocess.run(['python', 'manage.py', 'test', to_run], stderr=subprocess.STDOUT)


if __name__ == "__main__":
    event_handler = MyFileWatcher()
    path = os.getcwd()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
