
from fastapi import APIRouter, File, HTTPException, UploadFile, Form, Request

from app.utils.pdf_parser import (
    extract_text_from_pdf,
    PDFExtractionError,
    PDFTextNotFoundError,
)
from app.ml.resume_extractor import ResumeExtractor
from app.schemas.matching import ResumeAnalysisResponse
import json


router = APIRouter(
    prefix="/api/resume",
    tags=["Resume"],
)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/extract")
async def extract_resume(
    file: UploadFile = File(...),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=415,
            detail="Only PDF files are supported.",
        )

    try:
        # Read at most one byte beyond the limit.
        file_bytes = await file.read(MAX_FILE_SIZE + 1)

        if len(file_bytes) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="File exceeds the 5 MB size limit.",
            )

        result = extract_text_from_pdf(file_bytes)

        return {
            "filename": file.filename,
            **result,
        }

    except PDFTextNotFoundError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    except PDFExtractionError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    finally:
        await file.close()


resume_extractor = ResumeExtractor()


@router.post(
    "/analyze",
    response_model=ResumeAnalysisResponse,
)
async def analyze_resume(
    file: UploadFile = File(...),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=415,
            detail="Only PDF files are supported.",
        )

    try:
        file_bytes = await file.read(MAX_FILE_SIZE + 1)

        if len(file_bytes) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="File exceeds the 5 MB size limit.",
            )

        pdf_result = extract_text_from_pdf(file_bytes)

        analysis = resume_extractor.analyze(
            pdf_result["extracted_text"]
        )

        return {
            "filename": file.filename,
            **pdf_result,
            **analysis,
        }

    except PDFTextNotFoundError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    except PDFExtractionError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    finally:
        await file.close()


@router.post("/match")
async def match_resume_with_job(
    request: Request,
    file: UploadFile = File(...),

    # Job information supplied by the user
    job_text: str = Form(...),
    job_skills: str = Form(...),
    job_title: str = Form(...),
    job_category: str = Form(...),
    required_experience: float = Form(...),

    # Candidate information that cannot reliably be inferred
    candidate_category: str = Form(...),
    candidate_experience: float | None = Form(None),
    candidate_title: str | None = Form(None),
):
    """
    Extract resume information and compare it with job requirements.
    """

    # 1. Validate uploaded file
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=415,
            detail="Only PDF files are supported.",
        )

    try:
        pdf_bytes = await file.read(MAX_FILE_SIZE + 1)

        if len(pdf_bytes) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="PDF file exceeds the 5 MB limit.",
            )

        # 2. Extract text from PDF
        pdf_result = extract_text_from_pdf(pdf_bytes)

        # 3. Extract candidate information
        resume_analysis = resume_extractor.analyze(
            pdf_result["extracted_text"]
        )

        # 4. Parse job skills supplied as a JSON array
        try:
            parsed_job_skills = json.loads(job_skills)

        except json.JSONDecodeError:
            # Support comma-separated skills as a fallback.
            if job_skills.strip().startswith(("[", "{")):
                raise HTTPException(
                    status_code=422,
                    detail="job_skills contains invalid JSON.",
                )

            parsed_job_skills = [
                skill.strip()
                for skill in job_skills.split(",")
                if skill.strip()
            ]

        if (
            not isinstance(parsed_job_skills, list)
            or not parsed_job_skills
            or not all(
                isinstance(skill, str) and skill.strip()
                for skill in parsed_job_skills
            )
        ):
            raise HTTPException(
                status_code=422,
                detail="job_skills must contain at least one non-empty skill.",
            )

        if not job_text.strip():
            raise HTTPException(
                status_code=422,
                detail="Job description cannot be empty.",
            )

        # 5. Use manual corrections when provided.
        # Otherwise, use information extracted from the resume.
        final_candidate_title = (
            candidate_title.strip()
            if candidate_title and candidate_title.strip()
            else resume_analysis["candidate_title"]
        )

        final_candidate_experience = (
            candidate_experience
            if candidate_experience is not None
            else resume_analysis["years_experience"]
        )

        if not final_candidate_title:
            raise HTTPException(
                status_code=422,
                detail="Candidate job title is missing. Please provide it.",
            )

        if final_candidate_experience is None:
            raise HTTPException(
                status_code=422,
                detail="Candidate experience could not be extracted. Please provide it.",
            )

        # 6. Get the existing matching service
        matching_service = request.app.state.matching_service

        if matching_service is None:
            raise HTTPException(
                status_code=503,
                detail="Matching service is not available.",
            )

        if required_experience < 0:
            raise HTTPException(
                status_code=422,
                detail="Required experience cannot be negative."
            )

        if candidate_experience is not None and candidate_experience < 0:
            raise HTTPException(
                status_code=422,
                detail="Candidate experience cannot be negative."
            )
        
        # 7. Calculate compatibility
        match_result = matching_service.calculate_match(
            resume_text=pdf_result["extracted_text"],
            job_text=job_text,
            resume_skills=resume_analysis["skills"],
            job_skills=parsed_job_skills,
            candidate_experience=final_candidate_experience,
            required_experience=required_experience,
            candidate_category=candidate_category,
            job_category=job_category,
            candidate_title=final_candidate_title,
            job_title=job_title,
        )

        # 8. Return combined response
        return {
            "filename": file.filename,
            "resume_analysis": {
                **resume_analysis,
                "page_count": pdf_result["page_count"],
                "character_count": pdf_result["character_count"],
                "candidate_title": final_candidate_title,
                "years_experience": final_candidate_experience,
            },
            "match_result": match_result,
        }

    except PDFTextNotFoundError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    except PDFExtractionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    finally:
        await file.close()
