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
from memri.schema import LinkedInAccount, LinkedInLink
from linkedin.LinkedInClient import LinkedInClient
from typing import List


ROOT = os.path.dirname(__file__)

config = Config(os.path.join(ROOT, '.env'))

DEBUG = config('VIS_DEBUG', cast=bool, default=False)
PORT = config('VIS_PORT', cast=int, default=8080)
OWNER_KEY = config('VIS_OWNER_KEY', cast=str)
DATABASE_KEY = config('VIS_DATABASE_KEY', cast=str)
POD_URL = config('VIS_POD_URL', cast=str)

STATIC_ROOT = ROOT
html_templates = Jinja2Templates(directory=STATIC_ROOT)

graph = LinkedInGraph(owner_key=OWNER_KEY, database_key=DATABASE_KEY,
                      create_account=True)

linkedin = LinkedInClient()


async def get_index(request: Request):
    return html_templates.TemplateResponse('index.html', {
        'request': request,
    })


async def get_vgraph(request: Request):
    return html_templates.TemplateResponse('vgraph.html', {
        'request': request,
        'owner_key': OWNER_KEY,
        'database_key': DATABASE_KEY,
        'pod_url': POD_URL
    })


async def get_graph(request: Request):
    accounts = graph.get_accounts()
    links = graph.get_links(accounts)

    data = {
        "nodes": [i.to_json() for i in accounts],
        "links": [{"source": i.source.id, "target": i.target.id,
                   "type": i.name} for i in links],
    }

    return JSONResponse(data)


async def get_profile(request: Request):
    params = request.query_params
    session_id = params.get("session")

    if session_id:
        linkedin.driver.session_id = session_id

    profile = linkedin.get_my_profile()

    data = {
        'profile': profile,
        'session': linkedin.driver.session_id,
    }

    return JSONResponse(data)


async def create_session(request: Request):
    linkedin.goto_main_page()

    data = {
        'session': linkedin.driver.session_id,
        'password_enabled': linkedin.is_password_enabled()
    }

    return JSONResponse(data)


async def session_password(request: Request):
    params = await request.json()
    email = params.get("login")
    password = params.get("password")
    session_id = params.get("session")

    if session_id:
        linkedin.driver.session_id = session_id

    linkedin.enter_password(email, password)

    data = {
        'session': linkedin.driver.session_id,
        'pin_enabled': linkedin.is_pin_enabled()
    }

    return JSONResponse(data)


async def session_pin(request: Request):
    params = await request.json()
    pin = params.get("pin")
    session_id = params.get("session")

    if session_id:
        linkedin.driver.session_id = session_id

    linkedin.enter_pin(pin)

    data = {
        'session': linkedin.driver.session_id,
    }

    return JSONResponse(data)


async def collect_connections(request: Request):
    params = await request.json()
    profile = params.get("profile")
    session_id = params.get("session")

    if session_id:
        linkedin.driver.session_id = session_id

    connections = linkedin.get_my_connections()

    graph.create_connections(
        owner=LinkedInAccount(
            externalId=profile["handle"],
            handle=profile["handle"],
            displayName=profile["displayName"],
            description=profile.get("description"),
            isMe=True,
        ),
        connections=[
            LinkedInAccount(
                externalId=i["profile_id"],
                handle=i["profile_id"],
                displayName=i["profile_name"],
                description=i.get("profile_occupation"),
                locationName=i.get("profile_location"),
                avatarUrl=i.get("profile_img"),
            ) for i in connections
        ]
    )

    data = {
        'session': linkedin.driver.session_id,
        'total': len(connections),
    }

    return JSONResponse(data)


def startup():
    print('Ready to go')


app = Starlette(
    debug=DEBUG,
    routes=[
        Route('/session', create_session, methods=['POST']),
        Route('/session/password', session_password, methods=['PUT']),
        Route('/session/pin', session_pin, methods=['PUT']),
        Route('/connections', collect_connections, methods=['POST']),
        Route('/profile', get_profile, methods=['GET']),
        Route('/graph', get_graph, methods=['GET']),
        Route('/vgraph', get_vgraph, methods=['GET']),
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
