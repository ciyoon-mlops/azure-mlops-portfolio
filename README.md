# Azure MLOps Portfolio

[![Azure](https://img.shields.io/badge/Azure-0078D4?style=flat&logo=microsoft-azure&logoColor=white)](https://azure.microsoft.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

> End-to-end MLOps demonstrations using Azure Machine Learning, Azure AI Search, and Retrieval-Augmented Generation (RAG) patterns.  
> Built as part of my transition from embedded/software engineering to AI Engineering.

## About Me 
I hold the following certifications:
- Microsoft Azure AI Fundamentals (AI-900)
- Microsoft Azure AI Engineer Associate (AI-102)
- KT AICE Professional

This portfolio showcases my hands-on learning journey in Azure MLOps and generative AI solutions.

## Projects Overview

| Project | Description | Key Azure Services | Status |
|---------|-------------|--------------------|--------|
| **RAG Demo** | Retrieval-Augmented Generation app using enterprise documents | Azure AI Search, Azure OpenAI, Embeddings | Planned |
| **AI Search Pipeline** | Custom vector search index with semantic ranking | Azure AI Search, Cognitive Services | Planned |
| **MLOps End-to-End** | Full ML lifecycle: data prep → training → registry → deployment → monitoring | Azure Machine Learning, GitHub Actions CI/CD | Planned |
| **Model Monitoring** | Drift detection and automated retraining demo | Azure ML Monitoring, Pipelines | Planned |

## Architecture Overview
(Planned)

```mermaid
graph TD
    A[Data Sources] --> B[Azure Data Factory / Storage]
    B --> C[Azure ML Data Ingestion]
    C --> D[Training Pipeline]
    D --> E[Model Registry]
    E --> F[Azure ML Endpoint]
    F --> G[FastAPI / Streamlit App]
    G --> H[Azure AI Search + OpenAI for RAG]