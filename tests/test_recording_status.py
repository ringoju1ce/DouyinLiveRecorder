import json
import importlib.util
import tempfile
import time
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('recording_status', Path(__file__).resolve().parents[1] / 'src/recording_status.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
RecordingStatus = module.RecordingStatus


class RecordingStatusTest(unittest.TestCase):
    def test_tasks_heartbeat_and_switch(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'status.json'
            status = RecordingStatus(path, interval=0.02)
            status.start()
            self.assertFalse(path.exists())
            status.set_enabled(True)
            read = lambda: json.loads(path.read_text())
            self.assertFalse(read()['recording'])
            with status.task('recording', '主播', 'video.ts'):
                with status.task('transcoding', '视频', 'video.mp4'):
                    data = read()
                    self.assertTrue(data['recording'])
                    self.assertTrue(data['transcoding'])
                    self.assertEqual(len(data['tasks']), 2)
                    before = data['updated_at']
                    time.sleep(0.08)
                    self.assertNotEqual(before, read()['updated_at'])
                self.assertFalse(read()['transcoding'])
            self.assertEqual(read()['tasks'], [])
            status.set_enabled(False)
            self.assertFalse(path.exists())
            time.sleep(0.04)
            self.assertFalse(path.exists())

    def test_cleanup_after_exception(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'status.json'
            status = RecordingStatus(path)
            status.set_enabled(True)
            with self.assertRaises(ValueError):
                with status.task('recording', 'test', 'video.ts'):
                    raise ValueError()
            self.assertEqual(json.loads(path.read_text())['tasks'], [])


if __name__ == '__main__':
    unittest.main()
