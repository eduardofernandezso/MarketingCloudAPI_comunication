def dataframe_json(muestra):
    muestra = muestra.where(pd.notnull(muestra), None)
    insert = muestra.to_dict('records')
    print('Datos se pasaron a JSON')
    return insert

## El Json no puede recibir fechas por lo que este método auxiliar
## convertirá cualquier dato de fecha y hora que pueda tener la cadena de datos. 

def datetime_converter(value: datetime) -> str:
    if isinstance(value, datetime):
        return value.__str__()

## Calculamos el tamaño aproximado de los lotes que enviaremos. 
## Pasaremos el primer elemento de nuestra lista de diccionarios y 
## lo usaremos como un proxy para todos los demás elementos de nuestros datos. 
## En caso de que esta carga útil exceda el límite de 5 MB, los agrupamos en lotes de menos de 4 MB con esta funcion
    
def get_batch_size(record: dict) -> int:
    batch = json.dumps({'items': record}, default=datetime_converter)
    return floor(4000 / (sys.getsizeof(batch) / 1024))

## creará la solicitud de importación e intentará enviar datos a la extensión de datos 
## segun el número de lotes determinado por get_batch_size(). 

def import_data(clientid , clientsecret ,
                data_extension , data):
    
    ## Este método empieza generando nuestro token de acceso: 
    access_token, expires_in, stubObj  = generate_access_token(clientid, clientsecret)
    subdomain = 'mcc*******************'
    rest_url = f'https://{subdomain}.rest.marketingcloudapis.com'
    headers = {'authorization': f'Bearer {access_token}'}
    batch_size = get_batch_size(data[0])
    
    ## si se demora más de 20 minutos en completarse, 
    ## tendremos que volver a autenticarnos y generar un nuevo token de acceso. 
    ## Por lo tanto, en nuestro ciclo de envío de lotes de datos, 
    ## verificaremos iterativamente si el token de acceso caducará en el próximo minuto.
    ## de ser así, generaremos un nuevo token.
    for batch in range(0, len(data), batch_size):
        if expires_in < time() + 60:
            expires_in, access_token, stubObj = generate_access_token(clientid, clientsecret)
            
        batch_data = data[batch:batch + batch_size]    
        insert_request = requests.post(
            url=f'{rest_url}/data/v1/async/dataextensions/key:{data_extension}/rows',
            data=json.dumps({'items': batch_data}, default=datetime_converter),
            headers=headers
        )
        
        
        if insert_request.status_code not in (200, 202):
            raise Exception(f'El Insert fallo porque: {insert_request.json()}')
        else: 
            print('Se insertaron los datos')
    insert_request.close()    
