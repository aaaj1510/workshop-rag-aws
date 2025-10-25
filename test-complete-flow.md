# PRUEBA COMPLETA DEL SISTEMA RAG

## Prerrequisitos
1. Stack de CloudFormation desplegado con `infrastructure-base.yaml`
2. Obtener las URLs de las Lambda Functions desde CloudFormation Outputs

## Paso 1: Verificar Infraestructura
Ir a CloudFormation → Tu Stack → Outputs y copiar:
- `DocumentProcessorURL`: URL de la función que procesa documentos
- `QueryHandlerURL`: URL de la función que maneja consultas

## Paso 2: Subir Documento de Prueba
```bash
# Subir el documento de prueba al bucket S3
aws s3 cp test-documents/company_policy.txt s3://rag-workshop-{tu-nombre}-docs-{account-id}/company_policy.txt
```

## Paso 3: Verificar Procesamiento
1. Ir a CloudWatch Logs
2. Buscar el log group: `/aws/lambda/rag-workshop-{tu-nombre}-document-processor`
3. Verificar que el documento se procesó correctamente

## Paso 4: Probar Consultas con Postman/curl

### Consulta 1: Vacaciones
```json
POST {QueryHandlerURL}
Content-Type: application/json

{
  "query": "¿Cuántos días de vacaciones tengo?"
}
```

**Respuesta esperada**: Información sobre 15 días hábiles de vacaciones

### Consulta 2: Beneficios
```json
POST {QueryHandlerURL}
Content-Type: application/json

{
  "query": "¿Qué beneficios médicos ofrece la empresa?"
}
```

**Respuesta esperada**: Detalles sobre seguro médico, dental, pensiones

### Consulta 3: Trabajo Remoto
```json
POST {QueryHandlerURL}
Content-Type: application/json

{
  "query": "¿Puedo trabajar desde casa?"
}
```

**Respuesta esperada**: Información sobre 2 días por semana de trabajo remoto

## Paso 5: Verificar en DynamoDB
1. Ir a DynamoDB → Tables
2. Buscar tabla: `rag-workshop-{tu-nombre}-vectors`
3. Verificar que hay items con chunks del documento

## Paso 6: Probar Frontend
1. Abrir `frontend/index.html` en el navegador
2. Cambiar la URL en `app.js` línea 5 por tu `QueryHandlerURL`
3. Subir un documento (simulado)
4. Hacer consultas y verificar respuestas

## Troubleshooting
- Si no hay respuestas: verificar logs de CloudWatch
- Si error de CORS: verificar headers en query_handler
- Si error de embeddings: verificar permisos de Bedrock
- Si error de DynamoDB: verificar que la tabla existe y tiene datos