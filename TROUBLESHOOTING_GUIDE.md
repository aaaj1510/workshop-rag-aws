# 🚨 GUÍA DE TROUBLESHOOTING - Workshop RAG

## 📋 **ERRORES ENCONTRADOS Y SOLUCIONES**

Esta guía documenta todos los errores que encontramos durante el desarrollo del workshop y cómo los solucionamos.

---

## ❌ **ERROR 1: CloudFormation - Dependencias IAM**

### **Síntomas:**
```
ROLLBACK_IN_PROGRESS
The following resource(s) failed to create: [LambdaExecutionRole]
Resource handler returned message: "Resource rag-workshop-documents-475705689198/* must be in ARN format or "*""
```

### **Causa:**
- IAM Role intentaba referenciar bucket S3 antes de que estuviera completamente creado
- Formato incorrecto de ARN en las políticas IAM

### **Solución:**
1. **Agregar dependencias explícitas**:
```yaml
LambdaExecutionRole:
  Type: AWS::IAM::Role
  DependsOn: 
    - DocumentsBucket
    - VectorTable
```

2. **Corregir formato ARN**:
```yaml
# ❌ Incorrecto
Resource: !Sub '${DocumentsBucket}/*'

# ✅ Correcto  
Resource: !Sub 'arn:aws:s3:::${DocumentsBucket}/*'
```

### **Lección aprendida:**
- CloudFormation requiere dependencias explícitas para recursos complejos
- IAM policies necesitan ARNs completos, no solo nombres de recursos

---

## ❌ **ERROR 2: Lambda - Dependencias Faltantes (PyPDF2)**

### **Síntomas:**
```
Runtime.ImportModuleError: Unable to import module 'lambda_function': No module named 'PyPDF2'
```

### **Causa:**
- Lambda no incluye PyPDF2 por defecto
- El código intentaba importar librerías no disponibles

### **Solución:**
**Opción A - Lambda Layers (Producción):**
```bash
mkdir python
pip install PyPDF2==3.0.1 -t python/
zip -r lambda-layer.zip python/
```

**Opción B - Simplificar para Workshop:**
- Cambiar de PDF a TXT processing
- Eliminar dependencia de PyPDF2
- Usar solo librerías nativas de Python

### **Código simplificado:**
```python
def extract_text_from_txt(bucket: str, key: str) -> str:
    response = s3_client.get_object(Bucket=bucket, Key=key)
    text = response['Body'].read().decode('utf-8')
    return text.strip()
```

### **Lección aprendida:**
- Para workshops, priorizar simplicidad sobre funcionalidad completa
- Lambda Layers son necesarios para dependencias externas

---

## ❌ **ERROR 3: DynamoDB - Tipos de Datos Float**

### **Síntomas:**
```
Error guardando chunks en DB: Float types are not supported. Use Decimal types instead.
```

### **Causa:**
- DynamoDB no acepta tipos `float` nativos de Python
- Los embeddings de Bedrock retornan `List[float]`

### **Solución:**
```python
from decimal import Decimal

# Convertir floats a Decimal para DynamoDB
embedding_decimal = [Decimal(str(float_val)) for float_val in embedding]

table.put_item(
    Item={
        'document_id': document_id,
        'chunk_id': chunk_id,
        'content': chunk,
        'embedding': embedding_decimal,  # ✅ Decimal
        'chunk_index': i
    }
)
```

### **Lección aprendida:**
- DynamoDB tiene restricciones específicas de tipos de datos
- Siempre convertir floats a Decimal para DynamoDB

---

## ❌ **ERROR 4: Lambda - Dependencias Faltantes (numpy)**

### **Síntomas:**
```
Runtime.ImportModuleError: Unable to import module 'lambda_function': No module named 'numpy'
```

### **Causa:**
- Query handler intentaba usar numpy para cálculos vectoriales
- numpy no está disponible por defecto en Lambda

### **Solución:**
**Implementar similitud coseno sin numpy:**
```python
import math

def cosine_similarity(vec1: List[float], vec2: List[Decimal]) -> float:
    # Convertir Decimal a float
    vec2_float = [float(d) for d in vec2]
    
    # Producto punto
    dot_product = sum(a * b for a, b in zip(vec1, vec2_float))
    
    # Normas
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2_float))
    
    if norm1 == 0 or norm2 == 0:
        return 0
    
    return dot_product / (norm1 * norm2)
```

### **Lección aprendida:**
- Implementar algoritmos básicos sin dependencias externas
- Matemáticas básicas de Python son suficientes para muchos casos

---

## ❌ **ERROR 5: Bedrock - Formulario de Caso de Uso**

### **Síntomas:**
```
ResourceNotFoundException: Model use case details have not been submitted for this account. 
Fill out the Anthropic use case details form before using the model.
```

### **Causa:**
- AWS Bedrock requiere formulario de caso de uso para modelos Anthropic
- Límites de uso temporal después de varias invocaciones

### **Solución:**
**Opción A - Completar formulario:**
1. Ir a Bedrock console → Model access
2. Completar formulario de caso de uso para Anthropic
3. Esperar aprobación (15 minutos - 24 horas)

**Opción B - Cambiar modelo:**
```python
# ❌ Requiere formulario
modelId="anthropic.claude-3-haiku-20240307-v1:0"

# ✅ Funciona inicialmente
modelId="anthropic.claude-3-sonnet-20240229-v1:0"
```

**Opción C - Fallback inteligente:**
```python
try:
    # Intentar Claude
    response = bedrock_client.invoke_model(...)
except Exception as claude_error:
    # Usar respuesta basada en contexto
    return generate_smart_response(query, context)
```

### **Lección aprendida:**
- Bedrock tiene restricciones por modelo y cuenta
- Siempre tener fallbacks para workshops en vivo

---

## ❌ **ERROR 6: Nombres de Recursos Duplicados**

### **Síntomas:**
```
BucketAlreadyExists: The requested bucket name is not available
```

### **Causa:**
- Múltiples estudiantes usando el mismo nombre de bucket S3
- Buckets S3 deben ser únicos globalmente

### **Solución:**
**Agregar parámetro StudentName:**
```yaml
Parameters:
  StudentName:
    Type: String
    Description: 'Nombre único del estudiante'
    AllowedPattern: '^[a-z0-9-]+$'

Resources:
  DocumentsBucket:
    Properties:
      BucketName: !Sub '${WorkshopName}-${StudentName}-docs-${AWS::AccountId}'
```

### **Nombres únicos generados:**
```
rag-workshop-juan-perez-docs-123456789012
rag-workshop-maria-garcia-docs-123456789012
```

### **Lección aprendida:**
- Siempre incluir identificadores únicos en workshops
- Account ID + nombre único garantiza unicidad

---

## ❌ **ERROR 7: Variables de Entorno Incorrectas**

### **Síntomas:**
```
AccessDeniedException: User is not authorized to perform: dynamodb:PutItem on resource: 
arn:aws:dynamodb:us-east-1:475705689198:table/rag-workshop-ariel-jones-vector
```

### **Causa:**
- Nombre de tabla DynamoDB incorrecto en variables de entorno
- Faltaba 's' al final: `vectors` vs `vector`

### **Solución:**
1. **Verificar nombre exacto en DynamoDB console**
2. **Actualizar variables de entorno en Lambda:**
```
VECTOR_TABLE: rag-workshop-ariel-jones-vectors  ✅
```

### **Lección aprendida:**
- Verificar nombres exactos de recursos
- Copy-paste es más seguro que escribir manualmente

---

## ❌ **ERROR 8: Frontend - Tipos de Archivo**

### **Síntomas:**
```
"Por favor selecciona un archivo PDF"
```

### **Causa:**
- Frontend configurado solo para PDFs
- Backend procesa archivos TXT
- Inconsistencia entre frontend y backend

### **Solución:**
**Actualizar validación de archivos:**
```javascript
// ❌ Solo PDF
if (file.type !== 'application/pdf') {

// ✅ PDF y TXT
if (file.type !== 'application/pdf' && 
    file.type !== 'text/plain' && 
    !file.name.endsWith('.txt')) {
```

**Actualizar HTML:**
```html
<input type="file" accept=".pdf,.txt">
```

### **Lección aprendida:**
- Mantener consistencia entre frontend y backend
- Validar en ambos lados pero con mismos criterios

---

## ❌ **ERROR 9: CloudFormation - Validación API Gateway**

### **Síntomas:**
```
Properties validation failed for resource QueryMethod with message: 
[#/MethodResponses/0: extraneous key [ResponseHeaders] is not permitted]

Properties validation failed for resource ApiDeployment with message: 
[#/StageDescription: expected type: JSONObject, found: String]
```

### **Causa:**
- `ResponseHeaders` no es válido en MethodResponses (debe ser `ResponseParameters`)
- `StageDescription` debe ser objeto, no string
- Sintaxis incorrecta en template CloudFormation

### **Solución:**
**1. Cambiar ResponseHeaders por ResponseParameters:**
```yaml
# ❌ Incorrecto
MethodResponses:
  - StatusCode: 200
    ResponseHeaders:
      Access-Control-Allow-Origin: true

# ✅ Correcto
MethodResponses:
  - StatusCode: 200
    ResponseParameters:
      method.response.header.Access-Control-Allow-Origin: false
      method.response.header.Access-Control-Allow-Headers: false
      method.response.header.Access-Control-Allow-Methods: false
```

**2. Cambiar StageDescription a formato objeto:**
```yaml
# ❌ Incorrecto
StageDescription: 'Production stage for RAG API'

# ✅ Correcto
StageDescription:
  Description: 'Production stage for RAG API'
```

### **Lección aprendida:**
- Validar sintaxis CloudFormation antes del despliegue
- API Gateway tiene sintaxis específica para CORS
- Usar cfn-lint para detectar errores temprano

---

## ❌ **ERROR 10: Lambda Permission - SourceArn Pattern**

### **Síntomas:**
```
Properties validation failed for resource LambdaApiGatewayPermission with message: 
#/SourceArn: failed validation constraint for keyword [pattern]
```

### **Causa:**
- `SourceArn` no cumple con el patrón requerido para execute-api
- Falta formato completo de ARN en Lambda Permission
- CloudFormation requiere ARN completo, no solo ID de API

### **Solución:**
```yaml
# ❌ Incorrecto - Solo ID de API
SourceArn: !Sub '${RagApi}/*/POST/query'

# ✅ Correcto - ARN completo de execute-api
SourceArn: !Sub 'arn:aws:execute-api:${AWS::Region}:${AWS::AccountId}:${RagApi}/*/POST/query'
```

**Formato correcto del ARN:**
```
arn:aws:execute-api:region:account-id:api-id/stage/method/resource-path
```

### **Lección aprendida:**
- Lambda permissions requieren ARNs completos de execute-api
- Validar patrones de ARN según el servicio AWS
- Usar variables CloudFormation para construir ARNs dinámicamente

---

## ❌ **ERROR 11: API Gateway - Missing Authentication Token**

### **Síntomas:**
```json
{"message":"Missing Authentication Token"}
```

### **Causa:**
- API Gateway Policy muy restrictiva bloquea acceso público
- CORS mal configurado
- Lambda Permission con SourceArn incorrecto
- Deployment incompleto

### **Solución Completa:**
**1. Usar template API Gateway simplificado:**
```yaml
# Eliminar Policy restrictiva del RestApi
RagApi:
  Type: AWS::ApiGateway::RestApi
  Properties:
    Name: !Sub 'rag-workshop-${StudentName}-api'
    # SIN Policy - permite acceso público

# Lambda Permission con wildcard
LambdaPermission:
  Properties:
    SourceArn: !Sub 'arn:aws:execute-api:${AWS::Region}:${AWS::AccountId}:${RagApi}/*/*'
```

**2. Verificar variables de entorno Lambda:**
```
VECTOR_TABLE=rag-workshop-{StudentName}-vectors
```

**3. Verificar permisos IAM Lambda:**
- DynamoDB: scan, query, putItem
- Bedrock: invokeModel

### **Template funcional completo:**
Usar `api-gateway-fixed.yaml` que incluye toda la configuración correcta.

### **Lección aprendida:**
- API Gateway público no necesita Policy restrictiva
- SourceArn debe usar wildcard `/*/*` para flexibilidad
- Siempre verificar deployment completo

---

## ❌ **ERROR 12: Lambda - "No module named 'lambda_function'"**

### **Síntomas:**
```
Runtime.ImportModuleError: Unable to import module 'lambda_function': No module named 'lambda_function'
```

### **Causa:**
- CloudFormation crea el archivo como `index.py` por defecto
- El Handler está configurado para `lambda_function.lambda_handler`
- Hay un desajuste entre el nombre del archivo y el handler

### **Solución:**
**Opción A - Crear archivo correcto:**
1. **Lambda Console** → **Code** tab
2. **Click derecho** en el área de archivos → **New File**
3. **Nombrar exactamente**: `lambda_function.py`
4. **Pegar el código** en el nuevo archivo
5. **Deploy**

**Opción B - Cambiar Handler:**
1. **Configuration** → **General configuration** → **Edit**
2. **Handler**: Cambiar a `index.lambda_handler`
3. **Save**

**Opción C - Verificar nombre:**
1. En el editor, verificar que el archivo se llama exactamente `lambda_function.py`
2. **NO** `index.py`, `lambda_function.py.py`, o cualquier variación

### **Lección aprendida:**
- CloudFormation no especifica el nombre del archivo, solo el código
- Lambda usa `index.py` por defecto
- El Handler debe coincidir exactamente con `archivo.función`

---

## ✅ **PRUEBAS CON POSTMAN - GUÍA RÁPIDA**

### **🚀 Setup Rápido en Postman:**

**1. Obtener URL del API:**
- CloudFormation → Outputs → `QueryEndpoint`
- Ejemplo: `https://abc123.execute-api.us-east-1.amazonaws.com/prod/query`

**2. Configurar Request:**
```
Method: POST
URL: [Tu QueryEndpoint]
Headers:
  Content-Type: application/json
Body (raw JSON):
{
  "query": "¿Cuántos días de vacaciones tengo?"
}
```

**3. Respuesta Esperada:**
```json
{
  "query": "¿Cuántos días de vacaciones tengo?",
  "response": "Según el documento, los empleados tienen derecho a 15 días hábiles de vacaciones anuales...",
  "sources": 3
}
```

### **📝 Consultas de Prueba:**
```json
{"query": "¿Puedo trabajar desde casa?"}
{"query": "¿Qué beneficios médicos hay?"}
{"query": "¿Cuál es el presupuesto para capacitación?"}
{"query": "¿Cuál es el horario de trabajo?"}
{"query": "¿Qué descuentos tengo en productos?"}
```

### **🔍 Troubleshooting API Gateway:**

**Error: "Missing Authentication Token"**
- ✅ Verificar URL completa con `/prod/query`
- ✅ Usar POST, no GET
- ✅ Verificar que el deployment esté completo

**Error: "Internal Server Error"**
- ✅ Verificar logs de Lambda en CloudWatch
- ✅ Verificar variables de entorno en Lambda
- ✅ Verificar que DynamoDB tenga datos

**Error: CORS**
- ✅ API Gateway ya tiene CORS configurado
- ✅ Si persiste, usar Postman en lugar de navegador

---

## 🛠️ **MEJORES PRÁCTICAS DERIVADAS**

### **1. Preparación de Workshop:**
- ✅ Probar todo el flujo en cuenta AWS limpia
- ✅ Tener fallbacks para servicios externos
- ✅ Documentar errores comunes y soluciones
- ✅ Crear nombres únicos automáticamente

### **2. CloudFormation:**
- ✅ Usar dependencias explícitas (`DependsOn`)
- ✅ Validar templates antes del workshop
- ✅ Incluir outputs útiles para debugging
- ✅ Usar ARNs completos en políticas IAM

### **3. Lambda:**
- ✅ Minimizar dependencias externas
- ✅ Usar librerías nativas cuando sea posible
- ✅ Implementar logging detallado
- ✅ Manejar errores gracefully

### **4. Bedrock:**
- ✅ Verificar acceso a modelos antes del workshop
- ✅ Tener modelos alternativos listos
- ✅ Implementar fallbacks inteligentes
- ✅ Monitorear quotas y límites

### **5. DynamoDB:**
- ✅ Usar tipos de datos correctos (Decimal vs Float)
- ✅ Verificar nombres de tablas exactos
- ✅ Implementar manejo de errores específicos

---

## 🎯 **CHECKLIST PRE-WORKSHOP**

### **1 Semana Antes:**
- [ ] Probar CloudFormation en cuenta limpia
- [ ] Verificar acceso a todos los modelos Bedrock
- [ ] Validar que funciones Lambda se despliegan correctamente
- [ ] Probar frontend con backend real

### **1 Día Antes:**
- [ ] Ejecutar todo el flujo end-to-end
- [ ] Verificar que no hay cambios en servicios AWS
- [ ] Preparar cuentas backup
- [ ] Tener soluciones alternativas listas

### **Durante Workshop:**
- [ ] Monitorear logs en tiempo real
- [ ] Tener troubleshooting guide a mano
- [ ] Estar preparado para pivotear a soluciones alternativas
- [ ] Documentar nuevos errores que aparezcan

---

## 📞 **RECURSOS DE AYUDA**

### **Documentación AWS:**
- [CloudFormation Troubleshooting](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/troubleshooting.html)
- [Lambda Error Handling](https://docs.aws.amazon.com/lambda/latest/dg/python-exceptions.html)
- [Bedrock Model Access](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html)
- [DynamoDB Data Types](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.NamingRulesDataTypes.html)

### **Comandos Útiles:**
```bash
# Validar CloudFormation
aws cloudformation validate-template --template-body file://template.yaml

# Ver logs Lambda en tiempo real
aws logs tail /aws/lambda/function-name --follow

# Verificar modelos Bedrock disponibles
aws bedrock list-foundation-models --region us-east-1

# Describir tabla DynamoDB
aws dynamodb describe-table --table-name table-name
```

---

**Esta guía debe actualizarse con cada nuevo error encontrado para mejorar continuamente la experiencia del workshop.** 🚀