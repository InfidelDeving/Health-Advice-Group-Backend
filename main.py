from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.userRoutes import user_router

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    user_router,
    prefix="/user",
    tags=["User"]
)


@app.get("/")
def default_route():
    return {"server status" : "ok"}


# set up coors policy so it doesn't tell u to fuk off
# import routes from routing files
# add routes to the app itself so it can actually use them

# optionally create default route


# IN ROUTES FILE
# CREATE API ROUTER
# CREATE ENDPOINTS