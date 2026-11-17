import logging
from fastapi import APIRouter
from app.models.payload import AudioRequest, MetronomeResponse
from app.models.cleanup_payload import CleanupRequest, CleanupResponse
from app.services.split_metronome_service import split_metronome
from app.services.cleanup_service import cleanup_service
from app.utils.error_handler import error_handler_api

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

@router.post("/process-metronome", response_model=MetronomeResponse)
def process_metronome(request: AudioRequest):
    try:
        return split_metronome.process_audio(request.input_path)
    except Exception as e:
        raise error_handler_api(e, "split metronome")

@router.delete("/cleanup", response_model=CleanupResponse)
def cleanup_temp_folder(payload: CleanupRequest):

    logger.info(f"*** Received cleanup request for: {payload.target_path}")

    try:
        path_deleted = cleanup_service.cleanup_path(payload.target_path)
        if path_deleted:
            return CleanupResponse(
                path_deleted=path_deleted
            )
        else:
            raise FileNotFoundError(f"Path does not exist: {payload.target_path}")

    except Exception as e:
        raise error_handler_api(e, "path cleanup")