# 🚀 PASOS DEL WORKSHOP RAG - GUÍA ESTUDIANTES

## 📋 **PREREQUISITOS**
- Cuenta AWS con acceso a Bedrock (opcional)
- Región: **us-east-1** (recomendado)
- Navegador web moderno
- Editor de código (opcional)

---

## 🎯 **PASO 1: CREAR INFRAESTRUCTURA BASE**

### **1.1 Desplegar CloudFormation**
1. **AWS Console** → Buscar "CloudFormation" → **us-east-1**
2. **Create stack** → **With new resources (standard)**
3. **Template source**: Upload a template file
4. **Choose file**: Seleccionar `infrastructure-base.yaml`
5. **Next**
6. **Stack name**: `rag-workshop-base-{tu-nombre}`
7. **StudentName**: `{tu-nombre}` (ej: juan-perez)
8. **Next** → **Next** → **Submit**
9. **Esperar** hasta ver **CREATE_COMPLETE** (5-10 minutos)

**📋 ¿Qué se crea automáticamente?**
- ✅ **S3 Bucket** para almacenar documentos
- ✅ **DynamoDB Table** para vectores y chunks
- ✅ **IAM Role** con permisos para Lambda
- ✅ **2 Lambda Functions** con código placeholder
- ✅ **CloudWatch Log Groups** para debugging
- ✅ **Variables de entorno** configuradas automáticamente

### **1.2 Explorar S3 Bucket Creado**
1. **AWS Console** → Buscar "S3"
2. **Buscar bucket**: `rag-workshop-{tu-nombre}-docs-{account-id}`
3. **Click en el bucket** → Explorar:
   - **Properties** → Ver configuración
   - **Permissions** → Ver políticas de seguridad
   - **Management** → Ver versionado habilitado
4. **Anotar el nombre exacto** del bucket

### **1.3 Explorar DynamoDB Table**
1. **AWS Console** → Buscar "DynamoDB"
2. **Tables** → Buscar `rag-workshop-{tu-nombre}-vectors`
3. **Click en la tabla** → Explorar:
   - **Overview** → Ver configuración Pay-per-request
   - **Items** → Ver que está vacía (por ahora)
   - **Overview** → Ver **Primary key**: 
     - **Partition key**: `document_id` (String)
     - **Sort key**: `chunk_id` (String)
4. **Anotar el nombre exacto** de la tabla

### **1.4 Explorar IAM Role**
1. **AWS Console** → Buscar "IAM"
2. **Roles** → Buscar `rag-workshop-{tu-nombre}-lambda-role`
3. **Click en el role** → Explorar:
   - **Trust relationships** → Ver que Lambda puede asumir este rol
   - **Permissions** → Ver políticas:
     - AWSLambdaBasicExecutionRole (CloudWatch logs)
     - WorkshopLambdaPermissions (S3, DynamoDB, Bedrock)
4. **Click en WorkshopLambdaPermissions** → **Show policy** → Ver JSON:
   ```json
   {
     "Effect": "Allow",
     "Action": ["bedrock:InvokeModel", "bedrock:ListFoundationModels"],
     "Resource": "*"
   }
   ```

---

## 🔧 **PASO 2: ACTUALIZAR FUNCIONES LAMBDA**

### **2.1 Verificar Lambda Functions Creadas**
1. **AWS Console** → Buscar "Lambda"
2. **Functions** → Verificar que existen:
   - `rag-workshop-{tu-nombre}-document-processor`
   - `rag-workshop-{tu-nombre}-query-handler`
3. **Si no existen**, fueron creadas por CloudFormation con código placeholder

### **2.2 Actualizar Document Processor**
1. **Click** en `rag-workshop-{tu-nombre}-document-processor`
2. **Explorar configuración**:
   - **Runtime**: Python 3.11
   - **Handler**: lambda_function.lambda_handler
   - **Timeout**: 5 minutos (300 segundos)
   - **Memory**: 512 MB

3. **Configuration** → **Environment variables**:
   - `VECTOR_TABLE`: `rag-workshop-{tu-nombre}-vectors` (para conectar con DynamoDB)
   - `DOCUMENTS_BUCKET`: `rag-workshop-{tu-nombre}-docs-{account-id}` (para leer archivos de S3)
   - **Save**
   
   **💡 ¿Por qué estas variables?**
   - Lambda necesita saber qué tabla DynamoDB usar para guardar vectores
   - Lambda necesita saber de qué bucket S3 descargar documentos
   - CloudFormation ya configuró los nombres únicos automáticamente

4. **Code** tab → **Reemplazar todo el código** con:
   - Abrir archivo `lambda/document_processor/lambda_function.py`
   - **Copiar todo el contenido**
   - **Pegar** en el editor de Lambda
   - **Deploy**
   
   **🚨 PROBLEMA COMÚN: Si aparece "No module named 'lambda_function'"**
   - El archivo se creó como `index.py` en lugar de `lambda_function.py`
   - **Solución**: Click derecho en el editor → **New File** → Nombrar `lambda_function.py`
   - **Pegar el código** en el nuevo archivo
   - **Deploy** nuevamente

5. **Explorar el código** - Líneas importantes:
   - **Línea 10**: `bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')`
   - **Línea 13**: `VECTOR_TABLE = os.environ['VECTOR_TABLE']`
   - **Línea 14**: `DOCUMENTS_BUCKET = os.environ['DOCUMENTS_BUCKET']`
   - **Línea 93**: Función `generate_embedding()` que llama a Bedrock
   - **Línea 99**: `modelId="amazon.titan-embed-text-v1"` (Modelo de embeddings)
   - **Línea 119**: Conversión a Decimal para DynamoDB

### **2.3 Actualizar Query Handler**
1. **Click** en `rag-workshop-{tu-nombre}-query-handler`
2. **Configuration** → **Environment variables**:
   - `VECTOR_TABLE`: `rag-workshop-{tu-nombre}-vectors` (para buscar vectores en DynamoDB)
   - **Save**
   
   **💡 ¿Por qué esta variable?**
   - Lambda necesita saber en qué tabla DynamoDB buscar los vectores guardados
   - Usa la misma tabla que el document processor para consistencia

3. **Code** tab → **Reemplazar todo el código** con:
   - Abrir archivo `lambda/query_handler/lambda_function.py`
   - **Copiar todo el contenido**
   - **Pegar** en el editor de Lambda
   - **Deploy**
   
   **🚨 PROBLEMA COMÚN: Si aparece "No module named 'lambda_function'"**
   - El archivo se creó como `index.py` en lugar de `lambda_function.py`
   - **Solución**: Click derecho en el editor → **New File** → Nombrar `lambda_function.py`
   - **Pegar el código** en el nuevo archivo
   - **Deploy** nuevamente

4. **Explorar el código** - Líneas importantes:
   - **Línea 10**: `bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')`
   - **Línea 13**: `VECTOR_TABLE = os.environ['VECTOR_TABLE']`
   - **Línea 58**: Función `generate_embedding()` para la query
   - **Línea 64**: `modelId="amazon.titan-embed-text-v1"` (Mismo modelo)
   - **Línea 77**: Función `cosine_similarity()` sin numpy
   - **Línea 129**: Función `generate_rag_response()` que llama a Claude
   - **Línea 154**: `modelId="anthropic.claude-3-sonnet-20240229-v1:0"` (Modelo de texto)

### **2.4 Verificar Permisos de Bedrock**
1. **Configuration** → **Permissions** → **Execution role**
2. **Click** en el role name
3. **Permissions** → **WorkshopLambdaPermissions** → **Show policy**
4. **Verificar líneas de Bedrock**:
   ```json
   {
     "Effect": "Allow",
     "Action": [
       "bedrock:InvokeModel",
       "bedrock:ListFoundationModels"
     ],
     "Resource": "*"
   }
   ```

---

## 🧪 **PASO 3: CONFIGURAR Y PROBAR BEDROCK**

### **3.1 Habilitar Modelos en Bedrock**
1. **AWS Console** → Buscar "Bedrock"
2. **Model access** (menú izquierdo)
3. **Manage model access** (botón naranja)
4. **Buscar y habilitar**:
   - ✅ **Amazon Titan Text Embeddings v1**
   - ✅ **Anthropic Claude 3 Sonnet**
5. **Next** → **Submit**
6. **Esperar** que el status cambie a "Access granted" (puede tomar minutos)

### **3.2 Subir Documento de Prueba a S3**
1. **S3 Console** → Tu bucket `rag-workshop-{tu-nombre}-docs-{account-id}`
2. **Upload** → **Add files**
3. **Seleccionar** `test-documents/company_policy.txt`
4. **Upload**
5. **Verificar** que el archivo aparece en el bucket

### **3.3 Probar Document Processor**
1. **Lambda Console** → `rag-workshop-{tu-nombre}-document-processor`
2. **Test** → **Create test event**
3. **Event name**: `test-s3-upload`
4. **Template**: Amazon S3 Put
5. **Modificar el JSON**:
   ```json
   {
     "Records": [
       {
         "s3": {
           "bucket": {
             "name": "rag-workshop-{tu-nombre}-docs-{account-id}"
           },
           "object": {
             "key": "company_policy.txt"
           }
         }
       }
     ]
   }
   ```
6. **Save** → **Test**
7. **Ver logs** en la respuesta:
   - ✅ "Procesando documento: company_policy.txt"
   - ✅ "Creados X chunks, generando embeddings..."
   - ✅ "Guardados X chunks para documento company_policy"

### **3.4 Verificar Datos en DynamoDB**
1. **DynamoDB Console** → Tu tabla `rag-workshop-{tu-nombre}-vectors`
2. **Explore table items**
3. **Scan** → **Run**
4. **Verificar items creados**:
   - `document_id`: "company_policy"
   - `chunk_id`: "chunk_0001", "chunk_0002", etc.
   - `content`: Texto del documento
   - `embedding`: Array de números (vectores)
   - `chunk_index`: 0, 1, 2, etc.

### **3.5 Probar Query Handler**
1. **Lambda Console** → `rag-workshop-{tu-nombre}-query-handler`
2. **Test** → **Create test event**
3. **Event name**: `test-query`
4. **Template**: API Gateway AWS Proxy
5. **Modificar el JSON**:
   ```json
   {
     "body": "{\"query\": \"¿Cuántos días de vacaciones tengo?\"}",
     "headers": {
       "Content-Type": "application/json"
     }
   }
   ```
6. **Save** → **Test**
7. **Ver respuesta**:
   ```json
   {
     "statusCode": 200,
     "headers": {
       "Content-Type": "application/json",
       "Access-Control-Allow-Origin": "*"
     },
     "body": "{\"query\":\"¿Cuántos días de vacaciones tengo?\",\"response\":\"Según el documento...\",\"sources\":3}"
   }
   ```

### **3.6 Analizar Logs de CloudWatch**
1. **Lambda Console** → **Monitor** → **View CloudWatch logs**
2. **Click** en el log stream más reciente
3. **Buscar líneas importantes**:
   - "Embedding generado para consulta, dimensión: 1536"
   - "Encontrados X chunks en la base de datos"
   - "Top 3 similitudes: [0.85, 0.72, 0.68]"
   - "Contexto construido con 3 chunks"

---

## 🌐 **PASO 4: DESPLEGAR API GATEWAY (OPCIONAL)**

### **4.1 Desplegar API Gateway**
1. **AWS Console** → CloudFormation → **Create stack**
2. **Upload template**: Seleccionar `api-gateway-only.yaml`
3. **Stack name**: `rag-workshop-api-{tu-nombre}`
4. **Parámetros**:
   - **WorkshopName**: `rag-workshop` (dejar por defecto)
   - **StudentName**: `{tu-nombre}` (MISMO que usaste antes)
   - **BaseStackName**: `rag-workshop-base-{tu-nombre}` (nombre de tu stack anterior)
5. **Deploy** y esperar **CREATE_COMPLETE** (2-3 minutos)

**💡 ¿Por qué estos parámetros?**
- **StudentName**: Debe coincidir exactamente con el stack base para encontrar tus Lambda functions
- **BaseStackName**: Para referencia (informativo)
- El template construye automáticamente los nombres de recursos existentes

### **4.2 Obtener URL del API Gateway**
1. **CloudFormation** → Tu stack → **Outputs**
2. **Copiar** el valor de `QueryEndpoint`:
   ```
   https://abc123def.execute-api.us-east-1.amazonaws.com/prod/query
   ```
3. **Anotar** esta URL para Postman

### **4.3 Probar con Postman**
1. **Abrir Postman** (o descargar desde postman.com)
2. **New Request** → **POST**
3. **URL**: Pegar tu `QueryEndpoint`
4. **Headers**:
   ```
   Content-Type: application/json
   ```
5. **Body** → **raw** → **JSON**:
   ```json
   {
     "query": "¿Cuántos días de vacaciones tengo?"
   }
   ```
6. **Send** → Ver respuesta JSON:
   ```json
   {
     "query": "¿Cuántos días de vacaciones tengo?",
     "response": "Según el documento, los empleados tienen derecho a 15 días hábiles de vacaciones anuales...",
     "sources": 2
   }
   ```

### **4.4 Probar Diferentes Consultas**
**Cambiar el body en Postman:**
```json
{"query": "¿Puedo trabajar desde casa?"}
{"query": "¿Qué beneficios médicos hay?"}
{"query": "¿Cuál es el presupuesto para capacitación?"}
{"query": "¿Cuál es el horario de trabajo?"}
```

### **4.5 Verificar Logs en CloudWatch**
1. **Lambda Console** → `query-handler` → **Monitor**
2. **View CloudWatch logs** → Ver logs en tiempo real
3. **Observar**:
   - Embedding generado para consulta
   - Chunks encontrados en DynamoDB
   - Similitudes calculadas
   - Respuesta generada por Claude

---

## 🖥️ **PASO 5: CONECTAR FRONTEND CON API REAL**

### **5.1 Obtener URL del API Gateway**
1. **CloudFormation Console** → Tu stack `rag-workshop-api-{tu-nombre}`
2. **Outputs** tab → **Copiar** el valor de `QueryEndpoint`
3. **Ejemplo**: `https://abc123def.execute-api.us-east-1.amazonaws.com/prod/query`
4. **Anotar** esta URL completa

### **5.2 Actualizar Configuración del Frontend**
1. **Abrir** `frontend/app.js` con cualquier editor de texto
2. **Buscar línea 3** que dice:
   ```javascript
   QUERY_ENDPOINT: 'https://abc123.execute-api.us-east-1.amazonaws.com/prod/query',
   ```
3. **Reemplazar** con tu URL real:
   ```javascript
   QUERY_ENDPOINT: 'https://TU-URL-COPIADA-AQUI',
   ```
4. **Guardar** el archivo (Ctrl+S)

**💡 Ejemplo completo:**
```javascript
// Antes
QUERY_ENDPOINT: 'https://abc123.execute-api.us-east-1.amazonaws.com/prod/query',

// Después (con tu URL real)
QUERY_ENDPOINT: 'https://xyz789def.execute-api.us-east-1.amazonaws.com/prod/query',
```

### **5.3 Probar Frontend con Backend Real**
1. **Abrir** `frontend/index.html` en navegador (doble click)
2. **Subir** `test-documents/company_policy.txt` (arrastrar y soltar)
3. **Esperar** mensaje: "Documento procesado exitosamente"
4. **Hacer preguntas**:
   - "¿Cuántos días de vacaciones tengo?"
   - "¿Puedo trabajar desde casa?"
   - "¿Qué beneficios médicos hay?"
   - "¿Cuál es el horario de trabajo?"
   - "¿Hay presupuesto para capacitación?"

**🚨 Si no funciona:**
- **Verificar** que guardaste `app.js` después de cambiar la URL
- **Refrescar** la página (F5)
- **Abrir Developer Tools** (F12) → Console → Ver errores
- **Probar** la URL en Postman primero para confirmar que funciona

### **5.4 Comparar Respuestas**
- **Simulación vs Real**: Notar diferencias en las respuestas
- **Contexto específico**: Las respuestas reales citan el documento exacto
- **Inteligencia**: Claude genera respuestas más naturales y precisas

### **5.5 Verificar Flujo Completo**
1. **Frontend** → Envía query al API Gateway
2. **API Gateway** → Invoca Lambda query-handler
3. **Lambda** → Busca vectores en DynamoDB
4. **Lambda** → Genera embedding con Titan
5. **Lambda** → Calcula similitud coseno
6. **Lambda** → Genera respuesta con Claude
7. **Frontend** → Muestra respuesta al usuario

---

## 🎉 **¡FELICITACIONES! SISTEMA RAG COMPLETO**

### **✅ Lo que has logrado:**
- ✅ **Infraestructura serverless** con CloudFormation
- ✅ **Procesamiento de documentos** con embeddings
- ✅ **Base de datos vectorial** en DynamoDB
- ✅ **Búsqueda semántica** con similitud coseno
- ✅ **Generación de respuestas** con Claude 3
- ✅ **API REST** con API Gateway
- ✅ **Frontend interactivo** conectado
- ✅ **Sistema RAG end-to-end** funcional

### **🚀 Próximos pasos (opcional):**
- Subir más documentos PDF/TXT
- Experimentar con diferentes tipos de preguntas
- Analizar logs de CloudWatch para entender el flujo
- Modificar parámetros como chunk_size o top_k
- Explorar otros modelos de Bedrock

### **📚 Conceptos aprendidos:**
- **RAG (Retrieval Augmented Generation)**
- **Embeddings y búsqueda vectorial**
- **Arquitecturas serverless**
- **Integración de servicios AWS**
- **APIs REST y CORS**
- **Procesamiento de lenguaje natural**os empleados tienen derecho a 15 días hábiles de vacaciones anuales...",
     "sources": 3
   }
   ```

### **4.4 Probar Diferentes Consultas**
**Cambiar el body en Postman:**
```json
{"query": "¿Puedo trabajar desde casa?"}
{"query": "¿Qué beneficios médicos hay?"}
{"query": "¿Cuál es el presupuesto para capacitación?"}
{"query": "¿Cuál es el horario de trabajo?"}
```

### **4.5 Verificar Logs en CloudWatch**
1. **Lambda Console** → `query-handler` → **Monitor**
2. **View CloudWatch logs** → Ver logs en tiempo real
3. **Observar**:
   - Embedding generado para consulta
   - Chunks encontrados en DynamoDB
   - Similitudes calculadas
   - Respuesta generada por Claude

---

bjeto `responses` con respuestas pre-programadas
4. **Línea 145**: Búsqueda por palabras clave
5. **Línea 175**: Función `realQuery()` para conexión real con Lambda
6. **Línea 190**: Función `sendQuery()` configurada para usar simulación

---

## 🎓 **PASO 5: ANÁLISIS PROFUNDO DE LA ARQUITECTURA**

### **5.1 Flujo Completo de Datos**
```
📄 Documento (S3) 
    ↓
🔄 Document Processor Lambda
    ├── Extrae texto (línea 65)
    ├── Crea chunks (línea 75)
    ├── Genera embeddings con Titan (línea 95)
    └── Guarda en DynamoDB (línea 115)
    ↓
🗄️ DynamoDB (vectores + texto)
    ↓
❓ Query del usuario
    ↓
🔍 Query Handler Lambda
    ├── Genera embedding de query (línea 65)
    ├── Busca similitud coseno (línea 78)
    ├── Selecciona top 3 chunks (línea 105)
    └── Genera respuesta con Claude (línea 155)
    ↓
💬 Respuesta contextualizada
```

### **5.2 Inspección de Embeddings**
1. **DynamoDB Console** → Tu tabla → **Items**
2. **Click** en cualquier item
3. **Ver campo `embedding`**:
   - Array de 1536 números decimales
   - Cada número representa una dimensión semántica
   - Generado por Amazon Titan Embeddings

### **5.3 Matemáticas de Similitud Coseno**
1. **Abrir** `lambda/query_handler/lambda_function.py`
2. **Línea 78-95**: Función `cosine_similarity()`
3. **Entender el cálculo**:
   ```python
   # Producto punto de vectores
   dot_product = sum(a * b for a, b in zip(vec1, vec2_float))
   
   # Normas de los vectores
   norm1 = math.sqrt(sum(a * a for a in vec1))
   norm2 = math.sqrt(sum(b * b for b in vec2_float))
   
   # Similitud coseno (0 = no similar, 1 = idéntico)
   return dot_product / (norm1 * norm2)
   ```

### **5.4 Configuración de Bedrock en el Código**
**Document Processor:**
- **Línea 8**: `bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')`
- **Línea 95**: `modelId="amazon.titan-embed-text-v1"` (Embeddings)
- **Línea 89-105**: Función completa de embeddings

**Query Handler:**
- **Línea 8**: `bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')`
- **Línea 65**: `modelId="amazon.titan-embed-text-v1"` (Query embeddings)
- **Línea 155**: `modelId="anthropic.claude-3-sonnet-20240229-v1:0"` (Generación)
- **Línea 130-175**: Función completa RAG con Claude

### **5.5 Prompt Engineering**
1. **Línea 135-150**: Prompt para Claude
2. **Elementos clave**:
   - Contexto extraído de chunks relevantes
   - Instrucciones específicas de comportamiento
   - Limitación a información del contexto
   - Formato de respuesta estructurado

### **5.6 Manejo de Errores y Tipos de Datos**
1. **DynamoDB Decimal Conversion** (línea 115):
   ```python
   embedding_decimal = [Decimal(str(float_val)) for float_val in embedding]
   ```
2. **Error Handling** en cada función
3. **CORS Headers** para frontend (línea 40-44)
4. **Logging** detallado para debugging

---

## 🔍 **VERIFICACIONES IMPORTANTES**

### **Verificaciones Detalladas:**
- [ ] **S3**: Bucket creado y documento subido
- [ ] **DynamoDB**: Tabla con items de chunks y embeddings
- [ ] **Lambda Document Processor**: Código actualizado y probado
- [ ] **Lambda Query Handler**: Código actualizado y probado
- [ ] **Bedrock**: Modelos habilitados (Titan + Claude)
- [ ] **CloudWatch**: Logs mostrando procesamiento exitoso
- [ ] **Frontend**: Demo funcionando con respuestas inteligentes
- [ ] **Arquitectura**: Flujo de datos entendido completamente

### **Si Hay Errores:**
1. **Consultar** `TROUBLESHOOTING_GUIDE.md`
2. **Verificar logs** en CloudWatch
3. **Revisar nombres** de recursos
4. **Confirmar región** us-east-1

---

## 📊 **MÉTRICAS DE ÉXITO**

Al finalizar deberías tener:
- ✅ **Infraestructura AWS**: S3, DynamoDB, Lambda, IAM configurados
- ✅ **Bedrock habilitado**: Titan Embeddings + Claude 3 Sonnet
- ✅ **Datos procesados**: Documento chunkeado con embeddings en DynamoDB
- ✅ **Lambda functions**: Código real funcionando y probado
- ✅ **Demo interactivo**: Frontend con simulación RAG inteligente
- ✅ **Conocimiento profundo**: Arquitectura, código, y conceptos RAG
- ✅ **Experiencia práctica**: Navegación completa de servicios AWS

---

## 🎓 **PRÓXIMOS PASOS**

### **Mejoras Opcionales:**
1. **Soporte PDF**: Agregar PyPDF2 via Lambda Layers
2. **Chunking inteligente**: Mejorar algoritmo de segmentación
3. **UI mejorada**: Agregar indicadores de carga
4. **Métricas**: CloudWatch dashboards
5. **Seguridad**: API Keys, autenticación

### **Producción:**
1. **Monitoreo**: CloudWatch alarms
2. **Escalabilidad**: DynamoDB on-demand
3. **Costos**: Bedrock usage monitoring
4. **Backup**: Point-in-time recovery

---

## 🚀 **SECCIÓN AVANZADA (OPCIONAL)**

### **Para Implementación Real en AWS:**

**Opción A: Function URL (Más Rápido)**
1. **Lambda Console** → `query-handler` → **Configuration** → **Function URL**
2. **Create function URL** → **Auth**: NONE → **CORS**: Enable
3. **Copiar URL** → Actualizar `app.js` → Cambiar a `realQuery()`

**Opción B: API Gateway (Completo)**
1. **Usar** `api-gateway.yaml` template
2. **Seguir** pasos originales de CloudFormation
3. **Conectar** frontend con endpoint real

### **Habilitación de Bedrock:**
1. **Bedrock Console** → **Model access**
2. **Enable** Claude 3 Sonnet y Titan Embeddings
3. **Esperar** aprobación (puede tomar minutos)

---

**¡Felicidades! Has completado el workshop RAG con AWS** 🎉

**🎯 Logros:**
- ✅ Demo RAG funcional
- ✅ Arquitectura serverless completa
- ✅ Código production-ready
- ✅ Conceptos de IA aplicados