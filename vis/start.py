import os
import sys
from starlette.applications import Starlette
from starlette.config import Config
from starlette.requests import Request
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

ROOT = os.path.dirname(__file__)

config = Config(os.path.join(ROOT, '.env'))

DEBUG = config('VIS_DEBUG', cast=bool, default=False)
PORT = config('VIS_PORT', cast=int, default=8080)

STATIC_ROOT = ROOT
html_templates = Jinja2Templates(directory=STATIC_ROOT)


async def index(request: Request):
    return html_templates.TemplateResponse('index.html', {
        'request': request,
    })


app = Starlette(debug=DEBUG, routes=[
    Route('/', index, methods=['GET']),
    Mount('/', app=StaticFiles(directory=STATIC_ROOT, html=True), name="index"),
])


if __name__ == '__main__':
    if 'serve' in sys.argv:
        print(f'VIS_DEBUG={DEBUG}')
        print(f'VIS_PORT={PORT}')

        import uvicorn
        uvicorn.run(
            app,
            host='0.0.0.0',
            port=PORT,
            # debug=DEBUG,
            log_level='debug' if DEBUG else None,
        )
