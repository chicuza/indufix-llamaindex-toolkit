"""Indufix LlamaIndex Toolkit - Custom tools using llama_cloud_services"""
from langchain_core.tools import tool
from llama_cloud_services import LlamaCloudIndex
import httpx
import os
from typing import List, Dict, Any

# Configuração LlamaCloud
LLAMA_CONFIG = {
    "name": "Forjador Indufix",
    "project_name": "Default",
    "organization_id": "e6e330e4-a8c4-4472-841b-096d0f307394",
    "api_key": os.getenv("LLAMA_CLOUD_API_KEY"),
}

PIPELINE_ENDPOINT = "https://api.cloud.llamaindex.ai/api/v1/pipelines/1bc5e382-d0b6-4dcf-98c5-bf4ce8f67301/retrieve"

# Lazy initialization helpers
_index = None
_retriever = None
_query_engine = None

def get_index():
    global _index
    if _index is None:
        _index = LlamaCloudIndex(**LLAMA_CONFIG)
    return _index

def get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = get_index().as_retriever()
    return _retriever

def get_query_engine():
    global _query_engine
    if _query_engine is None:
        _query_engine = get_index().as_query_engine()
    return _query_engine


@tool
async def retrieve_matching_rules(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Recupera regras de matching da base Indufix via LlamaCloud Index.
    
    Use para:
    - Buscar valores default para atributos ausentes
    - Encontrar equivalências de padrões (DIN 933 = ISO 4017)
    - Obter penalidades de confiança para valores inferidos
    - Recuperar mapeamentos Odoo
    
    Args:
        query: Consulta de busca (ex: "parafuso M10 valores default")
        top_k: Número de resultados (default: 5)
    
    Returns:
        dict com nodes contendo text, score e metadata
    """
    nodes = get_retriever().retrieve(query)
    return {
        "query": query,
        "nodes": [
            {
                "text": node.text,
                "score": node.score if hasattr(node, 'score') else 1.0,
                "metadata": node.metadata if hasattr(node, 'metadata') else {}
            }
            for node in nodes[:top_k]
        ]
    }


@tool
async def query_indufix_knowledge(query: str) -> str:
    """
    Consulta a base de conhecimento Indufix com resposta processada.
    
    Usa o query engine que processa e sintetiza a resposta baseada
    nos documentos recuperados.
    
    Args:
        query: Pergunta em linguagem natural
    
    Returns:
        str com resposta sintetizada
    """
    response = get_query_engine().query(query)
    return str(response)


@tool
async def get_default_values(product_type: str, missing_attributes: List[str]) -> Dict[str, Any]:
    """
    Busca valores default para atributos ausentes de um tipo de produto.
    
    Args:
        product_type: Tipo do produto (ex: "parafuso_sextavado", "porca")
        missing_attributes: Lista de atributos faltantes (ex: ["material", "acabamento"])
    
    Returns:
        dict com valores default e penalidades de confiança
    """
    query = f"valores default para {product_type}: {', '.join(missing_attributes)}"
    nodes = get_retriever().retrieve(query)
    
    defaults = []
    for i, attr in enumerate(missing_attributes):
        if i < len(nodes):
            node = nodes[i]
            defaults.append({
                "attribute": attr,
                "suggested_value": node.metadata.get("default_value") if hasattr(node, 'metadata') else None,
                "confidence_penalty": node.metadata.get("penalty", 0.1) if hasattr(node, 'metadata') else 0.1,
                "source": node.text[:200] if hasattr(node, 'text') else ""
            })
    
    return {
        "product_type": product_type,
        "missing_attributes": missing_attributes,
        "defaults": defaults
    }


@tool
async def get_standard_equivalences(standard: str) -> Dict[str, Any]:
    """
    Busca equivalências entre normas/padrões técnicos.
    
    Args:
        standard: Norma ou padrão (ex: "DIN 933", "ISO 4017", "ASTM A307")
    
    Returns:
        dict com normas equivalentes e especificações
    """
    query = f"equivalência norma padrão {standard} fastener"
    nodes = get_retriever().retrieve(query)
    
    equivalences = []
    for node in nodes:
        equivalences.append({
            "equivalent_standard": node.metadata.get("equivalent") if hasattr(node, 'metadata') else None,
            "description": node.text if hasattr(node, 'text') else "",
            "confidence": node.score if hasattr(node, 'score') else 1.0
        })
    
    return {
        "standard": standard,
        "equivalences": equivalences
    }


@tool
async def get_confidence_penalty(
    attribute: str,
    inferred_value: str,
    inference_method: str
) -> Dict[str, Any]:
    """
    Obtém penalidade de confiança para valor inferido.
    
    Args:
        attribute: Nome do atributo (ex: "material", "acabamento")
        inferred_value: Valor inferido (ex: "aço carbono", "zincado")
        inference_method: Método usado (ex: "default", "pattern_match", "llm")
    
    Returns:
        dict com penalidade sugerida e justificativa
    """
    query = f"penalidade confiança {attribute} {inferred_value} inferido por {inference_method}"
    nodes = get_retriever().retrieve(query)
    
    if nodes and len(nodes) > 0:
        best_match = nodes[0]
        return {
            "attribute": attribute,
            "inferred_value": inferred_value,
            "inference_method": inference_method,
            "suggested_penalty": best_match.metadata.get("penalty", 0.15) if hasattr(best_match, 'metadata') else 0.15,
            "justification": best_match.text if hasattr(best_match, 'text') else "",
            "confidence": best_match.score if hasattr(best_match, 'score') else 1.0
        }
    
    return {
        "attribute": attribute,
        "inferred_value": inferred_value,
        "inference_method": inference_method,
        "suggested_penalty": 0.2,  # default penalty
        "justification": "Nenhuma regra específica encontrada",
        "confidence": 0.0
    }


@tool
async def pipeline_retrieve_raw(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Chamada direta ao pipeline endpoint (fallback/debug).
    
    Args:
        query: Query de busca
        top_k: Número de resultados
    
    Returns:
        dict com resposta raw do pipeline
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            PIPELINE_ENDPOINT,
            json={"query": query, "top_k": top_k},
            headers={
                "Authorization": f"Bearer {LLAMA_CONFIG['api_key']}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()


# Lista de tools exportadas
TOOLS = [
    retrieve_matching_rules,
    query_indufix_knowledge,
    get_default_values,
    get_standard_equivalences,
    get_confidence_penalty,
    pipeline_retrieve_raw,
]
