from fastapi import FastAPI, HTTPException, status, Request
from fastapi.params import Param
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime, timezone, timedelta
import random
import sympy
import os
import uvicorn

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def custom_error_response(requests: Request, exc: RequestValidationError):
    errors = exc.errors()
    custom_errors = []
    for error in errors:
        custom_error = {
            "type": error["type"],
            "loc": error["loc"],
            "message": error["msg"],
            "input": error["input"]
        }
        custom_errors.append(custom_error)

    return JSONResponse(
        status_code=422,
        content={"error": custom_errors}
    )


@app.get('/', include_in_schema=False)
async def home_page():
    return RedirectResponse(url='/docs')

@app.get('/number',
         responses={
             200: {
                 "description": "Random number generator response",
                 "content": {
                     "application/json": {
                         "example": {"Number": 0}
                     }
                 }
             },
             422: {
                 "description": "If limit is not number",
                 "content": {
                     "application/json": {
                         "example": {
                             "error": {
                                 "type": "string",
                                 "loc": ["string", 0],
                                 "message": "string",
                                 "input": "string"
                             }
                         }
                     }
                 }
             }
         })
async def get_random(limit: int = Param(100)):
    return {'Number': random.randint(0, limit)}


@app.get('/calculator')
async def solve_equation(math=Param(None)):
    if math:
        return {'Solved': f"{sympy.sympify(math)}", "Unsolved": f"{math}"}
    else:
        error_message = {'Error': 'Please provide a expression. Parameter "math" is missing...'}
    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=error_message)


@app.get('/datetime', responses={
    200: {
        "description": "Formatting successful response",
        "content": {
            "application/json": {
                "example": {
                    "formatted_time": "2024/06/14",
                    "input": "%Y/%m/%d"
                }
            }
        }
    }
}
         )
async def date_time(iso: datetime | int = Param(datetime.now()), format_type=Param("%Y/%m/%d")):
    try:
        if format_type:
            modified_iso = iso

            if not str(modified_iso).isdigit():
                modified_iso = datetime.fromisoformat(str(modified_iso))

            elif str(modified_iso).isdigit():
                modified_time = (int(modified_iso) >> 22) + 1420070400000
                modified_iso = datetime.fromtimestamp(modified_time / 1000, timezone.utc)

            formatted = datetime.strftime(modified_iso, str(format_type))

            return {'formatted_time': formatted, 'input': format_type}
        else:
            error_message = {'error': 'please provide a format type. Missing "format_type" parameter'}

    except ValueError as value_error:
        error_message = {'error': f"{value_error}"}

    except OverflowError as Overflowing:
        error_message = {'error': f"{Overflowing}"}

    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=error_message)


@app.get('/timediff')
async def timedif(start_time=Param(None), end_time=Param(None)):
    if not (start_time and end_time):
        missing_param = '"end_time"' if not end_time and start_time else '"start_time"' if not start_time and end_time else '"end_time" and "start_time"'
        error_message = {"error": f"Missing: {missing_param}"}
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=error_message)

    def expose_timestamp(t):
        exposed_time = int(((int(t) >> 22) + 1420070400000) / 1000)
        return exposed_time

    try:
        start_timestamp = (expose_timestamp(start_time) if isinstance(start_time, int)
                           else datetime.fromisoformat(str(start_time)))

        end_timestamp = (expose_timestamp(end_time) if isinstance(end_time, int)
                         else datetime.fromisoformat(str(end_time)))
    except ValueError as value_error_message:
        error_response = {"error": f"{value_error_message}"}
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=error_response)

    duration_delta = start_timestamp - end_timestamp
    print(duration_delta)
    active = (timedelta(seconds=duration_delta) if (isinstance(start_time, int) and isinstance(end_time, int))
              else duration_delta)

    year = active.days // 365
    month = (active.days // 30) % 30
    day = active.days // 86400

    hour = (active.seconds // 3600) % 24
    minute = (active.seconds // 60) % 60
    seconds = (active.seconds % 60)

    return {
        "time_difference": [
            {
                "year": year,
                "month": month,
                "day": day,
                "hour": hour,
                "minute": minute,
                "second": seconds
            }
        ],
        "start_time": f"{start_time}",
        "end_time": f"{end_time}"
    }


@app.get('/string-swap')
async def string_swap(string=Param(None), old=Param(None), new=Param('')):
    if string and old:
        new_string = str(string).replace(str(old), str(new))
        return {'Modified': f'{new_string}'}

    else:
        missing_param = 'string' if not string and old else 'old' if not old and string else 'string and old'
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail={'error': f'Missing parameter: {missing_param}'})

if __name__ == "__main__":
    uvicorn.run(app)
