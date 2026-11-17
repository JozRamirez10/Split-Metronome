import os
import logging
import warnings
import threading
import numpy as np
import librosa
import soundfile as sf

from app.utils.patch_madmom import apply_madmom_patch
apply_madmom_patch()

from BeatNet.BeatNet import BeatNet
from madmom.features.key import CNNKeyRecognitionProcessor, key_prediction_to_label
from app.core.config import TMP_DIR
from app.core.constants import (
    DEFAULT_SAMPLE_RATE,
    MAX_FILE_SIZE_MB,
    ALLOWED_AUDIO_EXTENSIONS,
)
from app.models.payload import MetronomeResponse

FILE_NOT_FOUND = "File not found"
BAD_REQUEST_EXT = "Invalid file extension"
BAD_REQUEST_SIZE = "File size exceeds maximum allowed"
SECURITY_ERROR = "Path traversal attempt blocked for path"

logger = logging.getLogger(__name__)

class SplitMetronomeService:

    def __init__(self):
        warnings.filterwarnings("ignore")
        logger.info("*** Load BeatNet (DBN) and Madmom Key CNN models in memory...")
        self.estimator = BeatNet(
            1, mode="offline", inference_model="DBN", plot=[], thread=False
        )
        self.key_estimator = CNNKeyRecognitionProcessor()
        logger.info("*** Models loaded successfully and ready for requests")
        self.lock = threading.Lock()

    def process_audio(self, input_path: str) -> MetronomeResponse:
        abs_path = self._validate_input_file(input_path)

        with self.lock:
            base_name, _ = os.path.splitext(abs_path)
            output_path = f"{base_name}_metronome.wav"

            logger.info(f"*** Analyzing beats for: {abs_path}")
            beats_detected = self.estimator.process(abs_path)

            logger.info("*** Loading audio waveform...")
            y, sr = librosa.load(abs_path, sr=DEFAULT_SAMPLE_RATE)

            bpm = self._calculate_bpm(beats_detected)
            tuning_hz = self._calculate_tuning_hz(y, sr)
            musical_key = self._calculate_musical_key(abs_path)

            logger.info("*** Synthesizing click tracks...")
            metronome_track = self._synthesize_click_track(beats_detected, y, sr)

            sf.write(output_path, metronome_track, sr)
            logger.info(
                f"*** File generated: {output_path} | "
                f"BPM: {bpm} | Tuning: {tuning_hz} Hz | Key: {musical_key}"
            )

            return MetronomeResponse(
                output_path=output_path,
                bpm=bpm,
                tuning_hz=tuning_hz,
                musical_key=musical_key,
            )

    def _calculate_bpm(self, beats_detected: np.ndarray) -> int:
        if beats_detected is None or len(beats_detected) <= 1:
            return 0
        all_beat_times = beats_detected[:, 0]
        ibi = np.diff(all_beat_times)
        median_ibi = float(np.median(ibi))
        return int(round(60.0 / median_ibi)) if median_ibi > 0 else 0

    def _calculate_tuning_hz(self, y: np.ndarray, sr: int) -> float:
        tuning_offset = librosa.estimate_tuning(
            y=y, sr=sr, resolution=0.01, n_fft=4096
        )
        return round(440.0 * (2.0 ** (float(tuning_offset) / 12.0)), 1)

    def _calculate_musical_key(self, abs_path: str) -> str:
        prediction = self.key_estimator(abs_path)
        raw_label = key_prediction_to_label(prediction) 
        parts = raw_label.split()
        if len(parts) == 2:
            note, mode = parts
            return f"{note}m" if mode.lower() == "minor" else note
        return raw_label

    def _synthesize_click_track(
        self, beats_detected: np.ndarray, y: np.ndarray, sr: int
    ) -> np.ndarray:
        downbeat_times = beats_detected[beats_detected[:, 1] == 1][:, 0]
        normal_beat_times = beats_detected[beats_detected[:, 1] > 1][:, 0]

        click_downbeats = librosa.clicks(
            times=downbeat_times, sr=sr, length=len(y), click_freq=1500
        )
        click_normals = librosa.clicks(
            times=normal_beat_times, sr=sr, length=len(y), click_freq=800
        )
        return click_downbeats + click_normals

    def _validate_input_file(self, input_path: str) -> str:

        abs_path = os.path.abspath(input_path)
        if not abs_path.startswith(TMP_DIR):
            msg_error = f"{SECURITY_ERROR}: {input_path}"
            logger.warning(msg_error)
            raise PermissionError(msg_error)

        _, ext = os.path.splitext(abs_path)
        if ext.lower() not in ALLOWED_AUDIO_EXTENSIONS:
            msg_error = f"{BAD_REQUEST_EXT}: {ext}. Allowed: {ALLOWED_AUDIO_EXTENSIONS}"
            logger.warning(msg_error)
            raise ValueError(msg_error)

        if not os.path.exists(abs_path):
            msg_error = f"{FILE_NOT_FOUND}: {input_path}"
            logger.error(msg_error)
            raise FileNotFoundError(msg_error)

        size_mb = os.path.getsize(abs_path) / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            msg_error = f"{BAD_REQUEST_SIZE}: {size_mb:.2f} MB. Max {MAX_FILE_SIZE_MB} MB"
            logger.warning(msg_error)
            raise ValueError(msg_error)

        return abs_path

split_metronome = SplitMetronomeService()