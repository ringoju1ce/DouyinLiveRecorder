"""Publish a heartbeat and the recorder's active work for external monitors."""
import datetime
import json
import logging
import os
import threading
import uuid
from contextlib import contextmanager


class RecordingStatus:
    def __init__(self, path, interval=10):
        self.path = os.fspath(path)
        self.interval = interval
        self.lock = threading.RLock()
        self.tasks = {}
        self.enabled = False

    def start(self):
        try:
            os.unlink(self.path)
        except FileNotFoundError:
            pass
        except OSError:
            logging.exception("Unable to remove stale recorder status")
        threading.Thread(target=self._heartbeat, daemon=True, name='status-heartbeat').start()

    def set_enabled(self, enabled):
        with self.lock:
            if self.enabled == enabled:
                return
            self.enabled = enabled
            if enabled:
                self.write()
            else:
                try:
                    os.unlink(self.path)
                except FileNotFoundError:
                    pass
                except OSError:
                    logging.exception("Unable to remove recorder status")

    def _heartbeat(self):
        while True:
            threading.Event().wait(self.interval)
            self.write()

    def write(self):
        with self.lock:
            if not self.enabled:
                return
            tasks = list(self.tasks.values())
            data = {
                'updated_at': datetime.datetime.now().astimezone().isoformat(),
                'recording': any(t['state'] == 'recording' for t in tasks),
                'transcoding': any(t['state'] == 'transcoding' for t in tasks),
                'tasks': tasks,
            }
            temporary = None
            try:
                directory = os.path.dirname(os.path.abspath(self.path))
                os.makedirs(directory, exist_ok=True)
                temporary = os.path.join(directory, '.recording-status-' + uuid.uuid4().hex)
                fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o666)
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False)
                    f.write('\n')
                os.replace(temporary, self.path)
            except OSError:
                logging.exception('Unable to write recorder status')
                if temporary and os.path.exists(temporary):
                    try:
                        os.unlink(temporary)
                    except OSError:
                        logging.exception("Unable to remove temporary status file")

    @contextmanager
    def task(self, state, name, output):
        task_id = uuid.uuid4().hex
        with self.lock:
            self.tasks[task_id] = {'id': task_id, 'name': name, 'state': state,
                                   'started_at': datetime.datetime.now().astimezone().isoformat(),
                                   'output': output}
            self.write()
        try:
            yield
        finally:
            with self.lock:
                self.tasks.pop(task_id, None)
                self.write()
