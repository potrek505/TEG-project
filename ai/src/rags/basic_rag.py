from langchain.chains import LLMChain, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import PromptTemplate

class BasicRAG:
    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever
        """
        Implement basic RAG with document stuffing
        """
        # Create a standard RAG prompt
        self.prompt = PromptTemplate.from_template(
            """
            Answer the following question based only on the provided context:
            
            Context:
            {context}
            
            Question: {input}
            
            Answer:
            """
        )
    
    # Create a document chain that combines the documents
        self.document_chain = create_stuff_documents_chain(self.llm, self.prompt)
        
        # Create a retrieval chain that uses the retriever and document chain
        self.retrieval_chain = create_retrieval_chain(self.retriever, self.document_chain)
    
    def query(self, query): 
        # Run the chain
        result = self.retrieval_chain.invoke({"input": query})
        
        # Return the answer and the source documents
        return {
            "query": query,
            "answer": result["answer"],
            "source_documents": result["context"]
        }