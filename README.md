# 🚀 Workshop RAG con AWS - Pregúntale a tus Documentos

## 📋 Descripción
Workshop práctico para implementar RAG (Retrieval Augmented Generation) usando AWS Bedrock, Lambda, DynamoDB y S3. Los participantes aprenderán a crear un sistema de IA conversacional que puede responder preguntas basándose en documentos específicos.

## 🎯 Objetivos de Aprendizaje
- Entender conceptos de RAG (Retrieval Augmented Generation)
- Implementar embeddings y búsqueda semántica
- Usar AWS Bedrock para generación de texto
- Crear arquitecturas serverless con Lambda
- Integrar múltiples servicios AWS

## 📁 Estructura del Proyecto
```
workshop-rag-aws/
├── frontend/                    # Interfaz web interactiva
│   ├── index.html              # UI principal
│   └── app.js                  # Lógica del frontend
├── lambda/                     # Funciones AWS Lambda
│   ├── document_processor/     # Procesamiento de documentos
│   └── query_handler/          # Manejo de consultas RAG
├── test-documents/             # Archivos de prueba
│   └── company_policy.txt      # Documento de ejemplo
├── infrastructure-base.yaml    # Template base (S3, DynamoDB, Lambda)
├── infrastructure-complete.yaml # Template completo (+ API Gateway)
├── WORKSHOP_STEPS.md           # Pasos detallados del workshop
└── TROUBLESHOOTING_GUIDE.md    # Guía de resolución de problemas
```

## 🚀 Inicio Rápido

### Opción 1: Demo Inmediata (Recomendado)
1. **Descargar** este repositorio (Code → Download ZIP)
2. **Extraer** archivos en tu computadora
3. **Abrir** `frontend/index.html` en tu navegador
4. **Subir** el archivo `test-documents/company_policy.txt`
5. **Hacer preguntas** como:
   - "¿Cuántos días de vacaciones tengo?"
   - "¿Puedo trabajar desde casa?"
   - "¿Qué beneficios médicos hay?"

### Opción 2: Implementación en AWS (Solo Lambda)
1. **Desplegar** `infrastructure-base.yaml` (S3, DynamoDB, Lambda)
2. **Actualizar** código de funciones Lambda
3. **Probar** directamente en Lambda console
4. **Usar** frontend en modo simulación

### Opción 3: Implementación Completa (Lambda + API Gateway)
1. **Desplegar** `infrastructure-complete.yaml` (incluye API Gateway)
2. **Actualizar** código de funciones Lambda
3. **Probar** con Postman usando endpoints reales
4. **Conectar** frontend con API real

## 🛠 Tecnologías Utilizadas
- **AWS Bedrock** - Modelos de IA (Claude 3, Titan Embeddings)
- **AWS Lambda** - Procesamiento serverless
- **Amazon DynamoDB** - Base de datos vectorial
- **Amazon S3** - Almacenamiento de documentos
- **HTML/CSS/JavaScript** - Frontend interactivo

## 📚 Conceptos Clave
- **RAG (Retrieval Augmented Generation)**: Combina búsqueda de información con generación de texto
- **Embeddings**: Representaciones vectoriales de texto para búsqueda semántica
- **Chunking**: División inteligente de documentos largos
- **Similitud Coseno**: Métrica para encontrar contenido relevante

## 🎓 Flujo del Workshop
1. **Demo** - Mostrar el sistema funcionando (10 min)
2. **Arquitectura** - Explicar componentes y flujo (15 min)
3. **Implementación** - Crear recursos AWS (25 min)
4. **Pruebas** - Validar funcionamiento (10 min)

## 🔧 Requisitos
- Cuenta AWS con acceso a Bedrock
- Navegador web moderno
- Editor de código (opcional)
- Conocimientos básicos de AWS

## 📞 Soporte
- **Troubleshooting**: Ver `TROUBLESHOOTING_GUIDE.md`
- **Pasos detallados**: Ver `WORKSHOP_STEPS.md`
- **Errores comunes**: Documentados con soluciones

## 🏆 Resultados Esperados
Al finalizar el workshop, tendrás:
- ✅ Sistema RAG funcional
- ✅ Comprensión de arquitecturas de IA
- ✅ Experiencia práctica con AWS Bedrock
- ✅ Código reutilizable para proyectos

## 📄 Licencia
Este proyecto es de uso educativo y está disponible bajo licencia MIT.

---

**¡Comienza ahora abriendo `frontend/index.html` en tu navegador!** 🎉