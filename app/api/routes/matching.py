
from fastapi import APIRouter, Depends, HTTPException, Request

from app.schemas.matching import MatchingRequest, MatchingResponse


router = APIRouter(prefix="/api", tags=["Matching"])


def get_matching_service(request: Request):
    service = getattr(request.app.state, "matching_service", None)

    if service is None:
        raise HTTPException(
            status_code=503,
            detail="Matching service is not available."
        )

    return service


@router.post("/match", response_model=MatchingResponse)
def match_resume_to_job(
    payload: MatchingRequest,
    service=Depends(get_matching_service),
):
    try:
        result = service.calculate_match(**payload.model_dump())
        return result

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error)
        ) from error
