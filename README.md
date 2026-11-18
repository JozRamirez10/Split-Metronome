# Split Metronome API

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![AI](https://img.shields.io/badge/AI-BeatNet%20%7C%20Madmom-EE4C2C?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Arch](https://img.shields.io/badge/Arch-AMD_x86__64-purple?style=for-the-badge)

A specialized AI-powered microservice designed to analyze musical audio files and automatically synthesize perfectly synchronized metronome tracks. This API utilizes advanced machine learning models (BeatNet and Madmom) to detect downbeats, calculate exact BPM, estimate tuning (Hz), and predict the musical key of any given song. It also includes an automated cleanup endpoint to manage temporary files efficiently.

> **⚠️ Architecture Requirement:** Due to specific hardcoded patches required to maintain compatibility with the obsolete `madmom` library, this microservice **MUST** be executed in a containerized environment (Docker) running strictly on `amd64 / x86_64` architecture.

## 🏗️ Architecture & Tech Stack

-   **Framework:** FastAPI (Python)
-   **AI & DSP Processing:** BeatNet (DBN inference), Madmom (CNN Key Recognition), Librosa
-   **Audio Handling:** SoundFile, PyAudio
-   **Data Processing:** NumPy
-   **Data Validation:** Pydantic
-   **Infrastructure:** Docker (Strictly amd64)

### 🚀 Key Features
-   **AI Beat Detection:** Utilizes BeatNet to accurately detect both standard beats and downbeats across complex audio files.
-   **Metronome Synthesis:** Generates and overlays dual-frequency click tracks (1500Hz for downbeats, 800Hz for normal beats) directly onto the audio.
-   **Musical Analysis:** Automatically extracts standard musical metadata:
    -   Average BPM (Beats Per Minute)
    -   Exact tuning frequency (Hz)
    -   Musical Key Prediction (e.g., C, Am)
-   **Legacy Compatibility Patching:** Includes custom runtime injection to patch Python collections, allowing the obsolete but powerful `madmom` library to compile and run on modern Python environments.
-   **Automated Cleanup Engine:** Dedicated endpoint to securely delete generated metronome files and source audio to prevent storage bloat.

---

## 📂 Repository Structure

~~~text
split_metronome_api/
├── app/
│   ├── controllers/          # Route handlers (metronome processing, cleanup)
│   ├── core/                 # Configuration, environment variables, and constants
│   ├── models/               # Pydantic schemas (AudioRequest, MetronomeResponse)
│   ├── services/             # Beat detection, synthesis, and file cleanup logic
│   ├── utils/                # Global error handlers and the madmom patch injector
│   └── main.py               # FastAPI application entry point
├── docker-compose.yml        # Docker orchestration file
├── Dockerfile                # Image build configuration (Must target amd64)
├── requirements.txt          # Python dependencies (Fixed versions for madmom/numpy)
├── .env.example              # Environment variables template
└── README.md
~~~

---

## 🚀 Getting Started

### Prerequisites
-   **Architecture:** `amd64` / `x86_64` host machine.
-   Docker & Docker Compose *(Execution outside of Docker is strongly discouraged due to system-level dependency conflicts with `madmom` and `pyaudio`)*.

### Environment Setup
This project uses a `.env` file for configuration to define the boundaries of the file system.

1. Copy the example file:
   ~~~bash
   cp .env.example .env
   ~~~
2. Open `.env` and configure your temporary working directory (`TMP_DIR`). The cleanup service strictly validates paths against this directory to prevent path traversal attacks.

---

### Installation & Execution

**Running with Docker (Required)**

Because of the intricate dependencies (like `madmom==0.16.1` and its reliance on deprecated Python `collections`), deploying this service via Docker is the only supported method.

~~~bash
git clone https://github.com/JozRamirez10/Split-Metronome.git
cd Split-Metronome

# 1. Create your local environment file
cp .env.example .env

# STOP 🛑: Open the .env file and configure your TMP_DIR

# 2. Build and run the container in detached mode
# Ensure your host or Docker Desktop is running in amd64 mode.
docker compose up -d --build
~~~

The API will be available at: `http://localhost:7001` (or your configured port).

---

## 🔌 API Endpoints

### 1. Process Metronome
`POST /api/process-metronome`

Analyzes an audio file and generates a metronome track.

**Request Payload:**
~~~json
{
  "input_path": "/path/to/tmp_dir/song.wav"
}
~~~

**Response:**
~~~json
{
  "output_path": "/path/to/tmp_dir/song_metronome.wav",
  "bpm": 120,
  "tuning_hz": 440.1,
  "musical_key": "Am"
}
~~~

### 2. Cleanup Temporary Files
`DELETE /api/cleanup`

Safely deletes a processed file or directory. Only paths residing within the configured `TMP_DIR` will be allowed.

**Request Payload:**
~~~json
{
  "target_path": "/path/to/tmp_dir/song_metronome.wav"
}
~~~

---

## 🛠️ The Madmom Patch

The machine learning library `madmom` relies on `collections.MutableSequence` (and others), which were removed in Python 3.10. To avoid downgrading the entire environment or forking the library, this project includes a dynamic patch in `app/utils/patch_madmom.py`. This script is executed during the initialization of the service to remap the obsolete collections to `collections.abc`, ensuring the CNN models load successfully.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing
1. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
2. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
3. Push to the Branch (`git push origin feature/AmazingFeature`)
4. Open a Pull Request.