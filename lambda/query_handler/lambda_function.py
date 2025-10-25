import json
import boto3
import os
from typing import List, Dict
from decimal import Decimal
import math

# Clientes AWS
dynamodb = boto3.resource('dynamodb')
bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')

# Variables de entorno
VECTOR_TABLE = os.environ['VECTOR_TABLE']
table = dynamodb.Table(VECTOR_TABLE)

def lambda_handler(event, context):
    """
    Maneja consultas RAG: busca contexto relevante y genera respuesta
    """
    try:
        # Parsear la consulta
        body = json.loads(event.get('body', '{}'))
        query = body.get('query', '')
        
        if not query:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Query requerida'})
            }
        
        print(f"Procesando consulta: {query}")
        
        # Buscar contexto relevante
        relevant_chunks = find_relevant_chunks(query, top_k=3)
        
        # Generar respuesta con Bedrock
        response = generate_rag_response(query, relevant_chunks)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'query': query,
                'response': response,
                'sources': len(relevant_chunks)
            })
        }
        
    except Exception as e:
        print(f"Error procesando consulta: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }

def generate_embedding(text: str) -> List[float]:
    """Genera embedding para la consulta"""
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
        raise Exception(f"Error generando embedding: {str(e)}")

def cosine_similarity(vec1: List[float], vec2: List[Decimal]) -> float:
    """Calcula similitud coseno entre dos vectores sin numpy"""
    try:
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
        
    except Exception as e:
        print(f"Error calculando similitud: {str(e)}")
        return 0

def find_relevant_chunks(query: str, top_k: int = 3) -> List[Dict]:
    """Busca los chunks más relevantes para la consulta"""
    try:
        # Generar embedding de la consulta
        query_embedding = generate_embedding(query)
        print(f"Embedding generado para consulta, dimensión: {len(query_embedding)}")
        
        # Obtener todos los chunks
        response = table.scan()
        chunks = response['Items']
        print(f"Encontrados {len(chunks)} chunks en la base de datos")
        
        # Calcular similitudes
        similarities = []
        for chunk in chunks:
            if 'embedding' in chunk:
                similarity = cosine_similarity(query_embedding, chunk['embedding'])
                similarities.append({
                    'chunk': chunk,
                    'similarity': similarity
                })
        
        # Ordenar por similitud y tomar top_k
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        print(f"Top {top_k} similitudes: {[s['similarity'] for s in similarities[:top_k]]}")
        
        return [item['chunk'] for item in similarities[:top_k]]
        
    except Exception as e:
        raise Exception(f"Error buscando chunks relevantes: {str(e)}")

def generate_rag_response(query: str, relevant_chunks: List[Dict]) -> str:
    """Genera respuesta usando RAG con Claude"""
    try:
        # Construir contexto
        context = "\n\n".join([chunk['content'] for chunk in relevant_chunks])
        print(f"Contexto construido con {len(relevant_chunks)} chunks")
        
        # Prompt para Claude
        prompt = f"""Eres un asistente experto que responde preguntas basándose únicamente en el contexto proporcionado.

Contexto:
{context}

Pregunta: {query}

Instrucciones:
- Responde únicamente basándote en la información del contexto
- Si la información no está en el contexto, di "No tengo información suficiente"
- Sé preciso y conciso
- Cita las partes relevantes del contexto

Respuesta:"""

        # Llamar a Claude
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })
        
        response = bedrock_client.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=body,
            contentType="application/json"
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
        
    except Exception as e:
        raise Exception(f"Error generando respuesta: {str(e)}")