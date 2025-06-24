from .basic_rag import BasicRAG
from langchain.chains import LLMChain, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import PromptTemplate
from langchain.schema import BaseRetriever
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
import json

class AdaptiveRAG:
    def __init__(self, llm, retriever, vectorstore):
        """
        Implement Adaptive RAG that analyzes the query first and adjusts retrieval strategy
        """
        # Step 1: Analyze the query complexity and determine retrieval strategy
        self.analysis_prompt = PromptTemplate.from_template(
            """
            Analyze the following question and determine the best retrieval strategy:
            
            Question: {question}
            
            1. Is this a simple factual question or a complex question requiring deep understanding?
            2. Should we decompose this question into sub-questions? If so, provide 2-3 sub-questions.
            3. What specific keywords or concepts should we focus on when retrieving documents?
            
            Respond in the following format:
            COMPLEXITY: [SIMPLE/COMPLEX]
            DECOMPOSITION: [NONE/SUB-QUESTIONS LIST]
            KEYWORDS: [List of keywords to focus on]
            """
        )
        self.llm = llm
        self.retriever = retriever
        self.vectorstore = vectorstore
        
        # Szablon do analizy pytania
        self.analysis_template = """
        Przeanalizuj następujące pytanie i określ najlepszą strategię wyszukiwania:
        
        Pytanie: {question}
        
        Odpowiedz w formacie JSON:
        {{
            "strategy": "simple|complex|multi_step",
            "search_terms": ["termin1", "termin2"],
            "complexity": "low|medium|high"
        }}
        """
        
        self.analysis_prompt = PromptTemplate(
            template=self.analysis_template,
            input_variables=["question"]
        )
        
        # Szablon do finalnej odpowiedzi
        self.answer_template = """
        Na podstawie następujących dokumentów odpowiedz na pytanie użytkownika:
        
        Pytanie: {question}
        
        Dokumenty:
        {context}
        
        Odpowiedź:
        """
        
        self.answer_prompt = PromptTemplate(
            template=self.answer_template,
            input_variables=["question", "context"]
        )
    
    def query(self, query_text: str) -> dict:
        """
        Główna metoda do zapytań RAG
        """
        try:
            print(f"[DEBUG] AdaptiveRAG: Przetwarzam pytanie: {query_text}")
            
            # Krok 1: Analiza pytania
            analysis_result = self._analyze_question(query_text)
            print(f"[DEBUG] AdaptiveRAG: Analiza: {analysis_result}")
            
            # Krok 2: Wyszukaj dokumenty
            documents = self._retrieve_documents(query_text, analysis_result)
            print(f"[DEBUG] AdaptiveRAG: Znaleziono {len(documents)} dokumentów")
            
            # Krok 3: Generuj odpowiedź
            answer = self._generate_answer(query_text, documents)
            
            return {
                "answer": answer,
                "strategy": analysis_result.get("strategy", "simple"),
                "source_documents_count": len(documents),
                "complexity": analysis_result.get("complexity", "medium")
            }
            
        except Exception as e:
            print(f"[DEBUG] AdaptiveRAG: Błąd: {e}")
            return {
                "answer": f"Wystąpił błąd podczas przetwarzania: {str(e)}",
                "strategy": "error",
                "source_documents_count": 0,
                "complexity": "error"
            }
    
    def _analyze_question(self, question: str) -> dict:
        """Analizuje pytanie i określa strategię"""
        try:
            # Użyj invoke zamiast run
            analysis_response = self.llm.invoke(
                self.analysis_prompt.format(question=question)
            )
            
            # Spróbuj sparsować JSON
            try:
                if hasattr(analysis_response, 'content'):
                    content = analysis_response.content
                else:
                    content = str(analysis_response)
                
                # Znajdź JSON w odpowiedzi
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    return {"strategy": "simple", "search_terms": [question], "complexity": "medium"}
                    
            except json.JSONDecodeError:
                return {"strategy": "simple", "search_terms": [question], "complexity": "medium"}
                
        except Exception as e:
            print(f"[DEBUG] Błąd analizy pytania: {e}")
            return {"strategy": "simple", "search_terms": [question], "complexity": "medium"}
    
    def _retrieve_documents(self, query: str, analysis: dict):
        """Pobiera dokumenty na podstawie analizy"""
        try:
            strategy = analysis.get("strategy", "simple")
            
            if strategy == "simple":
                # Proste wyszukiwanie
                docs = self.retriever.invoke(query)
                return docs[:5]  # Ogranicz do 5 dokumentów
                
            elif strategy == "complex":
                # Złożone wyszukiwanie z wieloma terminami
                search_terms = analysis.get("search_terms", [query])
                all_docs = []
                
                for term in search_terms[:3]:  # Max 3 terminy
                    docs = self.retriever.invoke(term)
                    all_docs.extend(docs[:100])  # Max 3 docs per term
                
                # Usuń duplikaty na podstawie page_content
                unique_docs = []
                seen_content = set()
                for doc in all_docs:
                    if doc.page_content not in seen_content:
                        unique_docs.append(doc)
                        seen_content.add(doc.page_content)
                
                return unique_docs[:5]
                
            else:  # multi_step
                # Multi-step reasoning
                docs = self.retriever.invoke(query)
                return docs[:7]  # Więcej dokumentów dla złożonych pytań
                
        except Exception as e:
            print(f"[DEBUG] Błąd podczas pobierania dokumentów: {e}")
            # Fallback - podstawowe wyszukiwanie
            try:
                return self.retriever.invoke(query)[:3]
            except:
                return []
    
    def _generate_answer(self, question: str, documents) -> str:
        """Generuje finalną odpowiedź"""
        try:
            # Sformatuj dokumenty
            context = "\n\n".join([
                f"Dokument {i+1}:\n{doc.page_content}" 
                for i, doc in enumerate(documents[:5])
            ])
            
            if not context.strip():
                return "Nie znalazłem odpowiednich informacji w kontekście transakcji."
            
            # Generuj odpowiedź
            response = self.llm.invoke(
                self.answer_prompt.format(question=question, context=context)
            )
            
            if hasattr(response, 'content'):
                return response.content
            else:
                return str(response)
                
        except Exception as e:
            print(f"[DEBUG] Błąd podczas generowania odpowiedzi: {e}")
            return f"Nie udało się wygenerować odpowiedzi: {str(e)}"