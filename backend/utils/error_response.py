from fastapi import HTTPException


def bad_request(message: str):

    raise HTTPException(
        status_code=400,
        detail={
            "status": "error",
            "message": message
        }
    )


def server_error(message: str):

    raise HTTPException(
        status_code=500,
        detail={
            "status": "error",
            "message": message
        }
    )