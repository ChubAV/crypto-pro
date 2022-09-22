from typing import Optional, Union, Any
import base64
# from starlette.datastructures import UploadFile
import pycades
import sys
import platform
from schemas import ResponseSchema, CertificateSchema, ErrorSchema, SingSchema, AboutSchema, ListCertificatesSchema
from enum import Enum
from subprocess import Popen, PIPE
from config import BASE_DIR, DIR_CERTIFICATES, ECHO_PATH, CERTMGR_PATH
import uuid
import os

################################################################

class StoreName(Enum):
    CAPICOM_CA_STORE = pycades.CAPICOM_CA_STORE
    CAPICOM_MY_STORE =  pycades.CAPICOM_MY_STORE
    CAPICOM_OTHER_STORE =  pycades.CAPICOM_OTHER_STORE
    CAPICOM_ROOT_STORE = pycades.CAPICOM_ROOT_STORE

################################################################

def About() -> Union[AboutSchema, ErrorSchema]:
    about = pycades.About()
    result = ResponseSchema(result=False)
    try:
        about_schema = AboutSchema(
            csp_version = about.CSPVersion().toString(),
            sdk_version = about.Version,
            pycades_version = pycades.ModuleVersion(),
            python_version = '{}.{}.{}'.format(sys.version_info.major, sys.version_info.minor, sys.version_info.micro),
            platform_version = platform.platform()
        )
        result.details = about_schema
        result.result = True
    except Exception as e:
        print(e)
        result.errors = ErrorSchema(
            code=str(e),
            description=str(e)
        )
    
    return result

################################################################

def DataToBase64(data: bytes) -> str:
    """
    Преобразование байтов в строку base64
    """
    return base64.b64encode(data).decode('utf-8')

################################################################

def TextToBase64(text: str) -> str:
    """
    Преобразование текста в строку base64
    """
    return DataToBase64(text.encode('utf-8'))

################################################################

# async def FileToBase64(f: bytes) -> str:
#     """
#     Преобразование файла в строку base64
#     """
#     # data = await f.read()
#     return DataToBase64(f)

################################################################

async def getHashObject(data: bytes) -> Any:
    """
    Вычисление хэша для файла или набора байт
    """
    sBase64 = DataToBase64(data)
    hashedData = pycades.HashedData()
    hashedData.Algorithm = pycades.CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_256
    hashedData.DataEncoding = pycades.CADESCOM_BASE64_TO_BINARY
    hashedData.Hash(sBase64)
    return hashedData

################################################################

def parse_sing(signed_data) -> SingSchema:
    signers = signed_data.Signers
    signer1 = signers.Item(1)
    cert1 = signer1.Certificate
    date_sign1 = signer1.SigningTime
    singer_schema = CertificateSchema(
        issuer_name=cert1.IssuerName,
        subject_name=cert1.SubjectName,
        thumbprint=cert1.Thumbprint,
        serial_number=cert1.SerialNumber,
        valid_from_date=cert1.ValidFromDate,
        valid_to_date=cert1.ValidToDate,
        certificate=cert1.Export(0),    
    )

    return SingSchema(
                singer=singer_schema,
                date_sign=date_sign1
                )

################################################################

def parse_cert(cert_data) -> CertificateSchema:

    result = CertificateSchema(
        issuer_name=cert_data.IssuerName,
        subject_name=cert_data.SubjectName,
        thumbprint=cert_data.Thumbprint,
        serial_number=cert_data.SerialNumber,
        valid_from_date=cert_data.ValidFromDate,
        valid_to_date=cert_data.ValidToDate,
        # certificate=cert1.Export(0),    
    )

    return result

################################################################

def VerifyHash(hash: Any, sign: str) -> Any:
    """
    Проверка подписи для хэша
    """
    signedData = pycades.SignedData()
    signedData.VerifyHash(hash, sign, pycades.CADESCOM_CADES_BES)
    return signedData


################################################################

def VerifyString(text_base64:str, sign:str) -> Any:
    """
    Проверка подписи для текста
    """

    signedData = pycades.SignedData()
    signedData.ContentEncoding = pycades.CADESCOM_BASE64_TO_BINARY
    signedData.Content = text_base64
    # print('------- До -------')
    signedData.VerifyCades(sign,pycades.CADESCOM_CADES_BES,1)
    # print('------- после -------')
    return signedData


################################################################

def VerifyCades(sign:str)-> Any:
    """
    Проверка подписи для контейнера, который содержит подпись и данные
    """
    signedData = pycades.SignedData()
    signedData.VerifyCades(sign, pycades.CADESCOM_CADES_BES)
    return signedData

################################################################

def VerifyText2Text(text:str, sign:str) -> Union[SingSchema, ErrorSchema]:
        """
        Проверка подписи в случаи когда приходят данные в ввиде текста и подпись в виде текста
        """
        try:
            text_base64 = TextToBase64(text)
            # print('====================')
            result = VerifyString(text_base64, sign)
            return parse_sing(result)
        except Exception as e:
            print(e)
            return ErrorSchema(
                code=str(e),
                description=str(e)
            )


################################################################

def VerifyText(sign: str) -> Union[SingSchema, ErrorSchema]:
    """
    Проверка подписи в случаи когда приходят данные в ввиде только текста
    """
    try:
        result = VerifyCades(sign)
        return parse_sing(result)
    except Exception as e:
        print(e)
        return ErrorSchema(
            code=str(e),
            description=str(e)
        )

################################################################

async def VerifyFile2File(file: bytes, sign: bytes) -> Union[SingSchema, ErrorSchema]:
    """
    Проверка подписи в случаи когда приходят данные в ввиде файла данных и файла подписи 
    """
    try:
        hash = await getHashObject(file)
        sBase64 = DataToBase64(sign)
        result = VerifyHash(hash, sBase64)
        return parse_sing(result)
    except Exception as e:
        print(e)
        return ErrorSchema(
            code=str(e),
            description=str(e)
        )

################################################################

async def VerifyFile2Text(file: bytes, sign: str) -> Union[SingSchema, ErrorSchema]:
    """
    Проверка подписи в случаи когда приходят данные в ввиде файла данных и текста подписи
    """
    try:
        hash = await getHashObject(file)
        result = VerifyHash(hash, sign)
        return parse_sing(result)
    except Exception as e:
        print(e)
        return ErrorSchema(
            code=str(e),
            description=str(e)
        )

################################################################

async def VerifyFile(file: bytes) -> Union[SingSchema, ErrorSchema]:
    """
    Проверка подписи в случаи когда приходят данные в ввиде только файла данных
    """
    try:
        fBase64 = DataToBase64(file)
        result = VerifyCades(fBase64)
        return parse_sing(result)
    except Exception as e:
        print(e)
        return ErrorSchema(
            code=str(e),
            description=str(e)
        )

################################################################
async def Verify(data: Union[bytes, str], sign: Optional[Union[bytes, str]] = None) -> ResponseSchema:
    """
    Диспетчер между различныйми способами проверки подписи
    переключается в зависимости от типа входных данных
    """
    result = ResponseSchema(result=False)
    # print(isinstance(data, StarletteUploadFile))
    temp = None
    if isinstance(data, bytes) and isinstance(sign, bytes):
        # print('--------------------------------f2f')
        temp = await VerifyFile2File(data, sign)
    elif isinstance(data, bytes) and isinstance(sign, str):
        temp = await VerifyFile2Text(data, sign)
    elif isinstance(data, bytes) and sign is None:
        temp = await VerifyFile(data)
    elif isinstance(data, str) and isinstance(sign, str):
        temp = VerifyText2Text(data, sign)
    elif isinstance(data, str) and sign is None:
        temp = VerifyText(data)
    else:
        pass
    
    if isinstance(temp, SingSchema):
        result.details = temp
        result.result = True
    elif isinstance(temp, ErrorSchema):
        result.errors = temp

    return result

################################################################

def infoCertificateBase64(data:str) -> Union[CertificateSchema, ErrorSchema]:
    """ 
    Выдает информацию о сертификате
    выходные данные - сертификат в формате base64
    """
    try:
        certifitate =  pycades.Certificate()
        certifitate.Import(data)
        return CertificateSchema(
            issuer_name=certifitate.IssuerName,
            subject_name=certifitate.SubjectName,
            thumbprint=certifitate.Thumbprint,
            serial_number=certifitate.SerialNumber,
            valid_from_date=certifitate.ValidFromDate,
            valid_to_date=certifitate.ValidToDate,
            certificate = data
        )

    except Exception as e:
        print(e)
        return ErrorSchema(
            code=str(e),
            description=str(e)
        )

################################################################

def InfoCertificate(data: Union[str, bytes]) -> ResponseSchema:
    """ 
    Выдает информацию о сертификате
    """
    result = ResponseSchema(
        result=False,
        details=None,
        errors=None,
    )
    temp = None
    
    if isinstance(data, str):
        temp = infoCertificateBase64(data)
    else:
        pass
    
    if isinstance(temp, CertificateSchema):
        result.details = temp
        result.result = True
    elif isinstance(temp, ErrorSchema):
        result.errors = temp
    
    return result

################################################################

def GetStoreCertificates(store):
    """ 
    Выдает список сертификатов в хранилище
    """
    oStore =  pycades.Store()
    oStore.Open(
        pycades.CAPICOM_CURRENT_USER_STORE,
        store,
        pycades.CAPICOM_STORE_OPEN_MAXIMUM_ALLOWED)
    certificates = oStore.Certificates
    oStore.Close()
    return certificates

################################################################

def ListCertificatesInSystem(store: Optional[StoreName] = None):
    """ 
    формирует ответ со списком сертификатов
    """
    result = ResponseSchema(
        result=False,
        details=None,
        errors=None,
    )
    list_certificates = ListCertificatesSchema()
    try:
        for s in StoreName:
            if s == store or s is None:
                certificates = GetStoreCertificates(s.value)
                if certificates.Count>0:
                    for i in range(1,certificates.Count+1):
                        # print(certificates.Item(i).SubjectName)
                        list_certificates.certificates.append(parse_cert(certificates.Item(i)))
                        list_certificates.count += 1
        result.details = list_certificates
        result.result = True
    except Exception as e:
        print(e)
        result.erros = ErrorSchema(
            code=str(e),
            description=str(e)
        )
    return result

################################################################

def save_certifitate_to_file(data: bytes) -> str:
    file_path = os.path.join(DIR_CERTIFICATES, str(uuid.uuid4()) + '.cer')
    with open(file_path, 'wb') as file:
        file.write(data)
    return file_path

################################################################
def remove_certifitate_file(file_path: str) -> bool:
    try:
        os.remove(file_path)
        return True
    except Exception as e:
        return False    

################################################################
def ImportCertificateEXE(cert_file_path: str):
    process = Popen(f"{ECHO_PATH} o | {CERTMGR_PATH} -inst -store root -f {cert_file_path}", shell=True, stdout=PIPE)
    output, err = process.communicate()
    exit_code = process.wait()
    output = output.decode().strip().lower().split("\n")
    if err is not None or exit_code != 0:
        return 'error run certmgr'
    
    for l in output:
        if 'errorcode' in l:
            return l
    else:
        return 'not data'