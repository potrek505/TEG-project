from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from .basic_rag import BasicRAG

class AdaptiveRAG:
    def __init__(self, llm, retriever, vectorstore):
        """
        Implement Adaptive RAG that analyzes the query first and adjusts retrieval strategy
        """
        self.llm = llm
        self.retriever = retriever
        self.vectorstore = vectorstore

    def query(self, query):
        """
        Analyze the query complexity and determine retrieval strategy
        """
        analysis_prompt = PromptTemplate.from_template(
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

        analysis_chain = LLMChain(llm=self.llm, prompt=analysis_prompt)
        analysis_result = analysis_chain.run(question=query)

        # Parse the analysis result
        complexity = "SIMPLE"
        decomposition = []
        keywords = []

        for line in analysis_result.split("\n"):
            if line.startswith("COMPLEXITY:"):
                complexity = line.replace("COMPLEXITY:", "").strip()
            elif line.startswith("DECOMPOSITION:"):
                decomp_text = line.replace("DECOMPOSITION:", "").strip()
                if decomp_text != "NONE":
                    decomposition = [q.strip() for q in decomp_text.split(",")]
            elif line.startswith("KEYWORDS:"):
                keywords_text = line.replace("KEYWORDS:", "").strip()
                keywords = [k.strip() for k in keywords_text.split(",")]

        # Step 2: Adjust retrieval strategy based on analysis
        if complexity == "SIMPLE":
            # For simple questions, use standard retrieval
            basic_rag = BasicRAG(self.llm, self.retriever)
            result = basic_rag.query(query)
            result["strategy"] = "Standard retrieval for a simple question"
            return result

        elif decomposition and len(decomposition) > 0:
            # For complex questions that can be decomposed, retrieve for each sub-question
            sub_results = []

            for sub_q in decomposition:
                # Get documents for each sub-question
                sub_docs = self.retriever.get_relevant_documents(sub_q)
                sub_results.append({
                    "sub_question": sub_q,
                    "documents": sub_docs
                })

            # Combine all retrieved documents
            all_docs = []
            for sub_result in sub_results:
                all_docs.extend(sub_result["documents"])

            # Remove duplicates while preserving order
            seen_content = set()
            unique_docs = []
            for doc in all_docs:
                if doc.page_content not in seen_content:
                    seen_content.add(doc.page_content)
                    unique_docs.append(doc)

            # Use a more detailed prompt that acknowledges the decomposition
            prompt = PromptTemplate.from_template(
                """
                I've broken down your complex question into sub-questions and retrieved relevant information for each.
                
                Original question: {question}
                
                Sub-questions analyzed:
                {sub_questions}
                
                Please answer the original question based on this context:
                {context}
                
                Provide a comprehensive answer that addresses all aspects of the original question.
                """
            )

            document_chain = create_stuff_documents_chain(
                self.llm, 
                prompt
            )

            # Create a context string to pass to the LLM
            context = "\n\n".join([doc.page_content for doc in unique_docs[:6]])  # Limit to 6 docs
            sub_questions_text = "\n".join([f"- {sq}" for sq in decomposition])

            # Generate answer
            answer = self.llm.invoke(
                prompt.format(
                    question=query, 
                    sub_questions=sub_questions_text, 
                    context=context
                )
            ).content

            return {
                "query": query,
                "answer": answer,
                "source_documents": unique_docs,
                "strategy": f"Decomposed into {len(decomposition)} sub-questions"
            }

        else:
            # For other complex questions, use hybrid search with more documents
            enhanced_retriever = self.vectorstore.as_retriever(search_kwargs={"k": 6})

            # Create a standard RAG prompt but request a more comprehensive answer
            prompt = PromptTemplate.from_template(
                """
                Answer the following complex question based on the provided context:
                
                Context:
                {context}
                
                Question: {question}
                
                Provide a comprehensive and detailed answer.
                """
            )

            document_chain = create_stuff_documents_chain(self.llm, prompt)
            retrieval_chain = create_retrieval_chain(enhanced_retriever, document_chain)

            result = retrieval_chain.invoke({"query": query})

            return {
                "query": query,
                "answer": result["answer"],
                "source_documents": result["context"],
                "strategy": "Enhanced retrieval for a complex question"
            }