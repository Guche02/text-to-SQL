# Text-to-SQL Query Generator using ChromaDB and Mistral Model

## Overview
This project is designed to transform natural language queries into SQL queries using the Mistral language model. The generated SQL queries are then executed on a database, and the results are analyzed to provide meaningful insights.

The system follows these steps:
1. **User Query Processing**: Takes user input in natural language.
2. **Query Generation**: Uses the Mistral model to generate SQL queries based on the user query.
3. **Execution**: Runs the generated SQL query on the relevant database.
4. **Result Processing**: Retrieves the query results.
5. **Insight Generation**: Analyzes the results to provide meaningful insights.

## Technologies Used
- **Python**: Main programming language.
- **Mistral Model**: Used for natural language to SQL query transformation.
- **ChromaDB**: Vector database for efficient retrieval of schema-related information.
- **SQLite/MySQL/PostgreSQL**: Database system for query execution.
- **LangChain/OpenAI API**: May be used for better prompt engineering and LLM responses.

## Project Structure

The project is organized as follows:

```
application/
│── chroma/                  
│── configs/
│   ├── .env                 
│── tools/
│   ├── database_tools.py    
│   ├── llm_tools.py          
│   ├── retriever_tool.py     
│── utils/
│   ├── prompts.py            
│   ├── schema_vector.py      
│   ├── schema.txt            
│   ├── test_data.txt         
│── app.py                    
│── pipeline_1.py            
│── pipeline_2.py             
│── pipeline_3.py             
│── temp.py                   
│── .gitignore                
```

### Explanation of Key Files
- **app.py**: Main application script that integrates all modules and runs the text-to-SQL pipeline.
- **tools/**
  - `database_tools.py`: Handles database connections and query execution.
  - `llm_tools.py`: Uses the Mistral model to generate SQL queries from user input.
  - `retriever_tool.py`: Retrieves schema-related information from ChromaDB to aid query generation.
- **utils/**
  - `prompts.py`: Stores predefined LLM prompts to ensure high-quality SQL query generation.
  - `schema_vector.py`: Converts schema into vector embeddings and stores them in ChromaDB.
  - `schema.txt`: Stores the database schema as raw text.
  - `test_data.txt`: Sample data for testing the system.
- **pipelines**
  - `pipeline_1.py`: Prepares and cleans the user's natural language query.
  - `pipeline_2.py`: Uses the Mistral model to generate SQL queries.
  - `pipeline_3.py`: Executes the SQL query and extracts meaningful insights.
- **temp.py**: Temporary script used for testing or debugging purposes.


## Setup Instructions
1. **Clone the Repository**
```bash
git clone <repository_url>
cd text-to-sql-project
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Set Up Environment Variables**
   - Rename `.env.example` to `.env`.
   - Add required API keys and database connection details.

4. **Run the Application**
```bash
python app.py
```

## Features
- **Natural Language Query Processing**: Converts user queries into SQL automatically.
- **Schema-Aware Query Generation**: Uses ChromaDB to enhance SQL generation accuracy.
- **Efficient Query Execution**: Runs queries on a connected database.
- **Automated Insights**: Provides meaningful analysis of query results.


