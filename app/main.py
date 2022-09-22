from fastapi import FastAPI
import routers

app = FastAPI(
    title='CryptoProPython',
    description='Проверка ЭЦП средствами PYTHON'
)
app.include_router(routers.api_router)

