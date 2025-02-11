# 🚀 Retrieval-Augmented Generation (RAG) with PDF Processing & Vector Databases

## 📌 Project Overview
This repository implements **Retrieval-Augmented Generation (RAG)** using **pymupdf4llm** for extracting text from PDFs, and leverages **ChromaDB** & **FAISS** as vector databases for efficient retrieval. The **Ollama** LLM is used for intelligent responses based on retrieved information.

----
```sh
PDF_Question_Answering_RAG_with_pymupdf4llm 
 │── 📜 README.md # Project documentation 
 │── 📜 requirements.txt # Required dependencies 
 │── 📂 data/ # Folder containing PDF documents and text files 
 │── 📜 main.py # Main script for running the pipeline 
 │── 📜 QA_without_runnable_ollama.py # Question-answering model logic 
 │── 📜 multi_column.py # Handles multi-column text extraction from PDFs 
 │── 📜 google_search.py # Google search utility 
 │── 📜 pdf_downloader.py # Script to download PDFs from URLs 
 │── 📜 text_downloader.py # Extracts text and metadata from web pages  
 │── 📜 text_scrape.py # Web scraping logic 
 │── 📜 .gitignore # Git ignore file

```
---


---

## 🛠️ Key Features
- **📄 PDF Text Extraction**: Utilizes **pymupdf4llm** and bounding box-based OCR to extract structured text.
- **🧠 Vector Databases**: Supports **ChromaDB** & **FAISS** for storing and retrieving document embeddings.
- **🤖 Ollama Integration**: Uses **Ollama** for generating accurate and context-aware responses.
- **🔍 Optimized Search**: Hybrid search approach for high-speed, accurate retrieval.


---

## 🔧 Installation & Setup

### 1️⃣ Clone the Repository
```sh
git clone https://github.com/yourusername/RAG_Project.git
cd RAG_Project
```

### 2️⃣ Install Required Dependencies
```sh
pip install -r requirements.txt
```

### 3️⃣ Ensure Required Services are Running
- **ChromaDB**: Install and start ChromaDB if using it as a vector store.
- **FAISS**: Ensure FAISS is installed for optimized nearest neighbor searches.
- **Ollama**: Set up the Ollama LLM service for text generation.

---

## 🚀 Usage

### 📝 Extract Text from PDFs
```sh
python scripts/pdf_extraction.py --file data/sample.pdf
```

### 📊 Store Document Embeddings
```sh
python scripts/vector_store.py --db_type chromadb
```

### 🔍 Retrieve Context & Generate Responses
```sh
python scripts/retrieval.py --query "What is the document about?"
```

### 🏁 Run the Full RAG Pipeline
```sh
python main.py --file data/sample.pdf --query "Summarize the document"
```

---

## 📊 Results & Insights
- Extracted structured **text from PDFs** using bounding box-based OCR.
- Indexed and stored document embeddings in **ChromaDB/FAISS**.
- Generated relevant responses using **Ollama** LLM.
- Achieved efficient **document retrieval & question answering** using vector search.

---

## 🤝 Contributing
We welcome contributions! 🚀 If you'd like to contribute:
1. **Fork the repository**
2. **Create a new branch** (`git checkout -b feature-branch`)
3. **Commit your changes** (`git commit -m "Your Message"`)
4. **Push to the branch** (`git push origin feature-branch`)
5. **Open a Pull Request**

---

## 📜 License
This project is licensed under the **[MIT License](https://choosealicense.com/licenses/mit/)**.

🚀 **Happy Coding & Knowledge Retrieval!** 📚
