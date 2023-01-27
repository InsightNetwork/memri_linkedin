import os
import sys
from starlette.applications import Starlette
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from memri.LinkedInGraph import LinkedInGraph


ROOT = os.path.dirname(__file__)

config = Config(os.path.join(ROOT, '.env'))

DEBUG = config('VIS_DEBUG', cast=bool, default=False)
PORT = config('VIS_PORT', cast=int, default=8080)
OWNER_KEY = config('VIS_OWNER_KEY', cast=str)
DATABASE_KEY = config('VIS_DATABASE_KEY', cast=str)

STATIC_ROOT = ROOT
html_templates = Jinja2Templates(directory=STATIC_ROOT)

graph = LinkedInGraph(owner_key=OWNER_KEY, database_key=DATABASE_KEY,
                      create_account=False)


async def get_index(request: Request):
    return html_templates.TemplateResponse('index.html', {
        'request': request,
    })


async def get_graph(request: Request):
    persons = graph.get_persons()
    links = graph.get_links(persons)

    data = {
        "nodes": [i.to_json() for i in persons],
        "links": [{"source": i.source.id, "target": i.target.id,
                   "type": i.name} for i in links],
    }

    return JSONResponse(data)


def startup():
    print('Ready to go')


app = Starlette(
    debug=DEBUG,
    routes=[
        Route('/graph', get_graph, methods=['GET']),
        Route('/', get_index, methods=['GET']),
        Mount('/', app=StaticFiles(directory=STATIC_ROOT, html=True),
              name="index"),
    ],
    on_startup=[startup],
)


if __name__ == '__main__':
    if 'serve' in sys.argv:
        print(f'VIS_DEBUG={DEBUG}')
        print(f'VIS_PORT={PORT}')

        import uvicorn
        uvicorn.run(
            app,
            host='0.0.0.0',
            port=PORT,
            log_level='debug' if DEBUG else None,
        )
