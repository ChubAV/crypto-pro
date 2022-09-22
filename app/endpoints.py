from fastapi import APIRouter, UploadFile, Form, File, Query
from  schemas import ResponseSchema
from services import Verify, InfoCertificate, About, ListCertificatesInSystem, StoreName, ImportCertificateEXE, save_certifitate_to_file, remove_certifitate_file

main_router = APIRouter()

################################################################

@main_router.get("/about/", response_model=ResponseSchema, summary='Информация о системе', description='Информация о системе - Версия КриптоПро, версия SDK, верия pycades, версия Python, Версия ОС')
async def info():
    """ 
    Выдает информацию о Крипто-Про и платформе
    """
    result = About()
    return result

################################################################

@main_router.post(
                "/verify/f2f/",
                response_model=ResponseSchema,
                summary='Проверка ЭЦП - файл+файл',
                description='Проверка электронной цифровой подписи. Входные данные: файл данных + файл подписи'
                )
async def f2f(
            file: UploadFile = File(default=..., description="Файл данных"),
            sign: UploadFile = File(default=..., description="Файл подписи")
    ):
    """ 
    Проверка подписи 
    файл + файл подписи
    """
    data = await file.read()
    sdata = await sign.read()
    result = await Verify(data, sdata)
    return result
################################################################

@main_router.post("/verify/f2s/",
                response_model=ResponseSchema, 
                summary='Проверка ЭЦП - файл+строка',
                description='Проверка электронной цифровой подписи. Входные данные: файл данных + строка подписи'
                )
async def f2s(
            file: UploadFile = File(default=..., description="Файл данных"),
            sign: str = Query(default=..., description="Строка подписи")
            ):
    """ 
    Проверка подписи 
    файл + срока подписи
    """
    data = await file.read()
    result = await Verify(data, sign)
    return result
################################################################

@main_router.post("/verify/f/",
                response_model=ResponseSchema,
                summary='Проверка ЭЦП - файл(эцп внутри)',
                description='Проверка электронной цифровой подписи. Входные данные: файл данных, который содержит подпись внутри'
)
async def f(file: UploadFile = File(default=..., description="Файл данных")):
    """ 
    Проверка подписи 
    файл c подписью внутри
    """
    data = await file.read()
    result = await Verify(data)
    return result
################################################################

@main_router.post("/verify/s2s/",
                response_model=ResponseSchema,
                summary='Проверка ЭЦП - строка+строка',
                description='Проверка электронной цифровой подписи. Входные данные: строка с данными + подпись как строка'
                )
async def s2s(text:str = Form(..., description="Строка - данных"), sign: str = Form(..., description="Строка - подпись")):
    """ 
    Проверка подписи 
    строка + строка подписи
    """
    result = await Verify(text, sign)
    return result
################################################################

@main_router.post("/verify/s/",
                response_model=ResponseSchema,
                summary='Проверка ЭЦП - строка(эцп внутри)',
                description='Проверка электронной цифровой подписи. Входные данные: строка, которая содержит подпись внутри'
                )
async def s(sign:str = Form(..., description="Строка с данными и подписью")):
    """ 
    Проверка подписи 
    строка c подписью внутри
    """

    result = await Verify(sign)
    return result
################################################################

@main_router.get("/certificates/store/ca/",
                response_model=ResponseSchema,
                summary='Список сертификатов СА',
                description='Выдает список сертификатов промежуточных УЦ'
                )
async def get_list_certificates_ca():
    """ 
    Выдает список сертификатов промежуточных(ca) УЦ
    """
    result = ListCertificatesInSystem(StoreName.CAPICOM_CA_STORE)
    return result
################################################################

@main_router.get("/certificates/store/root/",
                response_model=ResponseSchema,
                summary='Список сертификатов ROOT',
                description='Выдает список сертификатов корневых(root) УЦ'
    )
async def get_list_certificates_root():
    """ 
    Выдает список сертификатов ROOT УЦ
    """
    result = ListCertificatesInSystem(StoreName.CAPICOM_ROOT_STORE)
    return result
    
################################################################

@main_router.post("/certificates/info/base64/",
                response_model=ResponseSchema,
                summary='Информация о сертификате',
                description='Выдает информацию о сертификате. Входные данные - сертификат как строка в Base64'
)
async def certificate_info_base64(cert_base64: str = Query(..., description="Cертификат как строка в Base64")):
    """ 
    Выдает информацию о сертификате
    выходные данные - сертификат в формате base64
    """
    result = InfoCertificate(cert_base64)
    return result

################################################################

@main_router.post("/certificates/import/",
                summary='Импорт сертификата',
                description='Импортирует сертифика УЦ'
)
async def import_certificate(file: UploadFile = File(..., description="Файл сертификата УЦ")):
    """ 
    Импорт сертификатов
    """
    data = await file.read()
    cert_file_path = save_certifitate_to_file(data)
    result = ImportCertificateEXE(cert_file_path)
    remove_certifitate_file(cert_file_path)
    return {'result': result}

################################################################

# @main_router.post("/test/")
# async def test():
#     result = ImportCertificateEXE()
#     return {"msg", result}