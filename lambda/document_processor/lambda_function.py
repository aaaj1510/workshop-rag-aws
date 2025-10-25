import json
import boto3
import os
from typing import List, Dict
from decimal import Decimal

# Clientes AWS
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')

# Variables de entorno
VECTOR_TABLE = os.environ['VECTOR_TABLE']
DOCUMENTS_BUCKET = os.environ['DOCUMENTS_BUCKET']

table = dynamodb.Table(VECTOR_TABLE)

def lambda_handler(event, context):
    """
    Procesa documentos TXT y genera embeddings para RAG
    """
    try:
        # Obtener información del documento desde S3
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
        
        print(f"Procesando documento: {key}")
        
        # Solo procesar archivos .txt
        if not key.lower().endswith('.txt'):
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': f'Archivo {key} ignorado - solo se procesan archivos .txt'
                })
            }
        
        # Descargar y extraer texto
        text_content = extract_text_from_txt(bucket, key)
        
        # Dividir en chunks
        chunks = create_chunks(text_content)
        
        # Generar embeddings y guardar en DynamoDB
        document_id = key.replace('.txt', '')
        print(f"Creados {len(chunks)} chunks, generando embeddings...")
        save_chunks_to_db(document_id, chunks)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Documento procesado exitosamente',
                'document_id': document_id,
                'chunks_created': len(chunks)
            })
        }
        
    except Exception as e:
        print(f"Error procesando documento: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def extract_text_from_txt(bucket: str, key: str) -> str:
    """Extrae texto de un archivo TXT en S3"""
    try:
        # Descargar archivo de S3
        response = s3_client.get_object(Bucket=bucket, Key=key)
        text = response['Body'].read().decode('utf-8')
        
        return text.strip()
        
    except Exception as e:
        raise Exception(f"Error extrayendo texto del archivo: {str(e)}")

def create_chunks(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Divide el texto en chunks con overlap"""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Buscar el final de una oración para evitar cortes abruptos
        if end < len(text):
            last_period = chunk.rfind('.')
            if last_period > chunk_size * 0.7:  # Si hay un punto en el último 30%
                end = start + last_period + 1
                chunk = text[start:end]
        
        chunks.append(chunk.strip())
        start = end - overlap
        
        if start >= len(text):
            break
    
    return chunks

def generate_embedding(text: str) -> List[float]:
    """Genera embedding usando Amazon Bedrock"""
    try:
        body = json.dumps({
            "inputText": text
        })
        
        response = bedrock_client.invoke_model(
            modelId="amazon.titan-embed-text-v1",
            body=body,
            contentType="application/json"
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['embedding']
        
    except Exception as e:
        print(f"Error con Bedrock: {str(e)}")
        raise Exception(f"Error generando embedding: {str(e)}")

def save_chunks_to_db(document_id: str, chunks: List[str]):
    """Guarda chunks y sus embeddings en DynamoDB"""
    try:
        for i, chunk in enumerate(chunks):
            chunk_id = f"chunk_{i:04d}"
            
            # Generar embedding
            embedding = generate_embedding(chunk)
            
            # Convertir floats a Decimal para DynamoDB
            embedding_decimal = [Decimal(str(float_val)) for float_val in embedding]
            
            # Guardar en DynamoDB
            table.put_item(
                Item={
                    'document_id': document_id,
                    'chunk_id': chunk_id,
                    'content': chunk,
                    'embedding': embedding_decimal,
                    'chunk_index': i
                }
            )
            
        print(f"Guardados {len(chunks)} chunks para documento {document_id}")
        
    except Exception as e:
        raise Exception(f"Error guardando chunks en DB: {str(e)}")