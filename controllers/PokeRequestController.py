import os
import json 
import logging

from fastapi import HTTPException
from models.PokeRequest import PokemonRequest
from utils.database import execute_query_json
from utils.AQueue import AQueue
from utils.ABlob import ABlob
from azure.storage.blob import BlobServiceClient

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_SAK")
AZURE_STORAGE_CONTAINER = os.getenv("AZURE_STORAGE_CONTAINER")

# configurar el logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def select_pokemon_request( id: int ):
    try:
        query = "select * from pokequeue.requests where id = ?"
        params = (id,)
        result = await execute_query_json( query , params )
        result_dict = json.loads(result)
        return result_dict
    except Exception as e:
        logger.error( f"Error selecting report request {e}" )
        raise HTTPException( status_code=500 , detail="Internal Server Error" )

async def update_pokemon_request( pokemon_request: PokemonRequest) -> dict:
    try:
        query = " exec pokequeue.update_poke_request ?, ?, ? "
        if not pokemon_request.url:
            pokemon_request.url = "";

        params = ( pokemon_request.id, pokemon_request.status, pokemon_request.url  )
        result = await execute_query_json( query , params, True )
        result_dict = json.loads(result)
        return result_dict
    except Exception as e:
        logger.error( f"Error updating report request {e}" )
        raise HTTPException( status_code=500 , detail="Internal Server Error" )

async def insert_pokemon_request( pokemon_request: PokemonRequest) -> dict:
    try:
        query = " exec pokequeue.create_poke_request ? "
        params = ( pokemon_request.pokemon_type,  )
        result = await execute_query_json( query , params, True )
        result_dict = json.loads(result)

        await AQueue().insert_message_on_queue( result )

        return result_dict
    except Exception as e:
        logger.error( f"Error inserting report request {e}" )
        raise HTTPException( status_code=500 , detail="Internal Server Error" )

async def get_all_request() -> dict:
    query = """
        select 
            r.id as ReportId, 
            s.description as Status, 
            r.type as PokemonType, 
            r.url, 
            r.created, 
            r.updated
        from pokequeue.requests r 
        inner join pokequeue.status s 
        on r.id_status = s.id 
    """
    result = await execute_query_json( query  )
    result_dict = json.loads(result)
    blob = ABlob()
    for record in result_dict:
        id = record['ReportId']
        record['url'] = f"{record['url']}?{blob.generate_sas(id)}"
    return result_dict

async def delete_pokemon_request( id: int ):
    try:
        # Paso 1: Validar que el registro existe en BD
        check_query = "SELECT COUNT(*) as count FROM pokequeue.requests WHERE id = ?"
        check_params = (id,)
        check_result = await execute_query_json( check_query , check_params )
        check_dict = json.loads(check_result)
        
        if not check_dict or check_dict[0]['count'] == 0:
            raise HTTPException(status_code=404, detail="Request no encontrado.")
        
        # Paso 2: Validar y preparar la eliminación del CSV
        blob_name = f"poke_report_{id}.csv"
        blob_service_client = BlobServiceClient.from_connection_string( AZURE_STORAGE_CONNECTION_STRING)
        blob_client = blob_service_client.get_blob_client( container = AZURE_STORAGE_CONTAINER, blob=blob_name )
        
        # Verificar si el archivo existe
        csv_exists = blob_client.exists()
        
        if csv_exists:
            # Paso 3: Validar que podemos acceder al blob antes de eliminar de BD
            try:
                # Test de acceso al blob (intentar obtener propiedades)
                blob_client.get_blob_properties()
                logger.info(f"Archivo CSV {blob_name} verificado y accesible para eliminación")
            except Exception as blob_test_error:
                logger.error(f"No se puede acceder al archivo CSV {blob_name}: {blob_test_error}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Error accediendo al archivo CSV. No se puede proceder con la eliminación: {str(blob_test_error)}"
                )
        else:
            logger.warning(f"El archivo CSV {blob_name} no existe en el blob storage")
        
        # Paso 4: Eliminar de la base de datos
        query = " exec pokequeue.delete_poke_request ? "
        params = (id,  )
        result = await execute_query_json( query , params, True )
        result_dict = json.loads(result)
        
        logger.info(f"Registro {id} eliminado exitosamente de la base de datos")
        
        # Paso 5: Eliminar el CSV solo si existe
        if csv_exists:
            try:
                # Eliminar el blob con sus snapshots
                blob_client.delete_blob(delete_snapshots='include')
                logger.info(f"Archivo CSV {blob_name} eliminado exitosamente del blob storage")
            except Exception as blob_error:
                logger.error(f"ERROR CRÍTICO: Registro {id} eliminado de BD pero no se pudo eliminar CSV {blob_name}: {blob_error}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Registro eliminado de BD pero error eliminando CSV. Requiere limpieza manual: {str(blob_error)}"
                )
            
        return result_dict
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error deleting report request: {e}")
        if "Request no encontrado" in error_msg:
            logger.warning(f"Request no encontrado: {error_msg}")
            raise HTTPException(status_code=404, detail="Request no encontrado.")
        
        raise HTTPException(status_code=500, detail="Internal Server Error")
