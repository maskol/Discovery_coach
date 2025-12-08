import os

from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

# Map API key from .env file
if api_key := os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = api_key


def load_prompt_file(filename: str) -> str:
    """Load a prompt file from the prompt_help folder."""
    filepath = os.path.join(os.path.dirname(__file__), "prompt_help", filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: Could not find {filename} in prompt_help folder")
        return ""


def build_or_load_vectorstore(
    knowledge_dir: str = "./knowledge_base", persist_dir: str = "./rag_db"
) -> Chroma:
    """
    Builds (the first time) or loads (if it already exists) a Chroma vector store
    containing your own documents about Epics/Features/SAFe.

    knowledge_dir: folder with .txt/.md documents
    persist_dir: folder where Chroma stores the index
    """

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Om index redan finns → bara ladda
    if os.path.exists(persist_dir) and os.listdir(persist_dir):
        vectorstore = Chroma(
            embedding_function=embeddings, persist_directory=persist_dir
        )
        return vectorstore

    # Annars bygga nytt
    # Här använder vi DirectoryLoader; justera glob_pattern vid behov
    loader = DirectoryLoader(
        knowledge_dir,
        glob="**/*.txt",  # ändra till t.ex. "**/*.md" eller kombinera om du vill
        loader_cls=TextLoader,
        show_progress=True,
    )

    docs = loader.load()

    # Dela upp dokument i chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    split_docs = splitter.split_documents(docs)

    # Skapa Chroma index
    vectorstore = Chroma.from_documents(
        documents=split_docs, embedding=embeddings, persist_directory=persist_dir
    )

    # Spara till disk
    vectorstore.persist()

    return vectorstore


def build_epic_pm_coach_with_rag(
    knowledge_dir: str = "./knowledge_base", persist_dir: str = "./rag_db"
) -> tuple[object, object]:
    """
    Creates an Epic/PM coach with RAG.
    Returns (chain, retriever).
    """

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
    )

    # Load system prompt from external file
    system_prompt = load_prompt_file("system_prompt.txt")

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("system", "Content from internal documents:\n{context}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{user_input}"),
        ]
    )

    # Create a runnable chain using the modern LangChain API
    chain = prompt | llm

    # Bygg / ladda vectorstore & retriever
    vectorstore = build_or_load_vectorstore(
        knowledge_dir=knowledge_dir, persist_dir=persist_dir
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 6})

    return chain, retriever


def display_help():
    """Display help information about available commands and questionnaires."""
    help_text = load_prompt_file("help.txt")
    print(help_text)


def display_epic_outline():
    """Display the current Epic content from conversation."""
    if (
        hasattr(display_epic_outline, "current_epic")
        and display_epic_outline.current_epic
    ):
        print("\n" + "=" * 80)
        print("CURRENT EPIC OUTLINE")
        print("=" * 80 + "\n")
        print(display_epic_outline.current_epic)
        print("\n" + "=" * 80 + "\n")
    else:
        print(
            "\nNo Epic content available. Start by providing epic details in conversation.\n"
        )


def display_feature_outline():
    """Display the current Feature content from conversation."""
    if (
        hasattr(display_feature_outline, "current_feature")
        and display_feature_outline.current_feature
    ):
        print("\n" + "=" * 80)
        print("CURRENT FEATURE OUTLINE")
        print("=" * 80 + "\n")
        print(display_feature_outline.current_feature)
        print("\n" + "=" * 80 + "\n")
    else:
        print(
            "\nNo Feature content available. Start by providing feature details in conversation.\n"
        )


def display_pi_objectives_outline():
    """Display the current PI Objectives content from conversation."""
    if (
        hasattr(display_pi_objectives_outline, "current_pi")
        and display_pi_objectives_outline.current_pi
    ):
        print("\n" + "=" * 80)
        print("CURRENT PI OBJECTIVES OUTLINE")
        print("=" * 80 + "\n")
        print(display_pi_objectives_outline.current_pi)
        print("\n" + "=" * 80 + "\n")
    else:
        print(
            "\nNo PI Objectives content available. Start by providing PI Objectives details in conversation.\n"
        )


def format_docs(docs) -> str:
    """Combine document chunks into a text string for context."""
    parts = []
    for d in docs:
        source = d.metadata.get("source", "unknown-source")
        parts.append(f"[Source: {source}]\n{d.page_content}\n")
    return "\n---\n".join(parts)


def load_epic_file(filepath: str) -> str:
    """Load an existing Epic from a file for evaluation."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ Error: File not found at '{filepath}'")
        print(f"   Current directory: {os.getcwd()}")
        print(f"   Try using an absolute path or check the file exists.")
        return ""
    except Exception as e:
        print(f"❌ Error reading file '{filepath}': {str(e)}")
        return ""


def evaluate_epic_command(epic_content: str, chain, retriever) -> None:
    """
    Evaluate an existing Epic against templates and best practices.
    Provides structured feedback without requiring conversation history.
    """
    if not epic_content:
        print("No epic content to evaluate.")
        return

    # Create evaluation prompt with explicit format requirement
    evaluation_prompt = """Please evaluate the following Epic against the SAFe Epic Hypothesis Statement template and best practices. 

IMPORTANT: The Epic Hypothesis Statement should follow this EXACT format:

For <customers>
who <do something>
the <solution>
is a <something – the 'how'>
that <provides this value>
unlike <competitor, current solution or non-existing solution>
our solution <does something better — the 'why'>

Provide structured feedback on:
1. Whether all 8 required elements are present (Epic Name, Problem/Opportunity, Target Customers, Business Outcome, Leading Indicators, NFRs, Hypothesis Statement, Constraints/Risks)
2. If the Business Outcome is measurable (with specific metrics, percentages, and timeframes)
3. If Leading Indicators are clearly defined and predictive of the outcome
4. If Non-Functional Requirements are specific and testable
5. If the Hypothesis Statement follows the required format (see above)
6. Specific recommendations for improvement, including a corrected Hypothesis Statement if needed in the exact format specified above

Here is the Epic to evaluate:

---
{}
---

Please provide detailed, actionable feedback. Use the exact hypothesis format when providing recommendations.""".format(
        epic_content
    )

    # Retrieve relevant context from knowledge base
    docs = retriever.invoke(evaluation_prompt)
    context = format_docs(docs) if docs else "No relevant context found."

    # Create simple conversation history for this evaluation
    eval_history = []

    # Invoke chain for evaluation
    response = chain.invoke(
        {
            "user_input": evaluation_prompt,
            "context": context,
            "chat_history": eval_history,
        }
    )

    response_text = response.content if hasattr(response, "content") else str(response)

    print("\n" + "=" * 80)
    print("EPIC EVALUATION RESULTS")
    print("=" * 80 + "\n")
    print(response_text)
    print("\n" + "=" * 80 + "\n")

    # Store the epic content for outline display
    display_epic_outline.current_epic = epic_content


if __name__ == "__main__":
    knowledge_dir = "./knowledge_base"
    persist_dir = "./rag_db"

    chain, retriever = build_epic_pm_coach_with_rag(
        knowledge_dir=knowledge_dir, persist_dir=persist_dir
    )

    print("Starting Epic/Feature coach with RAG.")
    print(f"Knowledge base: {knowledge_dir}")
    print("Type 'help' for commands or 'quit' to exit.\n")

    # Initialize conversation history
    chat_history = []

    while True:
        user_input = input("You: ").strip()

        # Handle help commands
        if user_input.lower() == "help":
            display_help()
            continue
        elif user_input.lower() == "outline epic":
            display_epic_outline()
            continue
        elif user_input.lower() == "outline feature":
            display_feature_outline()
            continue
        elif user_input.lower() == "outline pi objectives":
            display_pi_objectives_outline()
            continue
        elif user_input.lower() == "activate epic":
            if (
                hasattr(display_epic_outline, "current_epic")
                and display_epic_outline.current_epic
            ):
                # Send the current epic to the agent for coaching
                epic_to_activate = display_epic_outline.current_epic
                print("\n[ACTIVATING EPIC FOR COACHING]")
                docs = retriever.invoke(epic_to_activate)
                context = format_docs(docs) if docs else "No relevant context found."
                response = chain.invoke(
                    {
                        "user_input": f"Please provide targeted coaching and feedback on this epic:\n\n{epic_to_activate}",
                        "context": context,
                        "chat_history": chat_history,
                    }
                )
                response_text = (
                    response.content if hasattr(response, "content") else str(response)
                )
                print("\nAgent:")
                print(response_text)
                print()
                # Add to history
                chat_history.append(HumanMessage(content=epic_to_activate))
                chat_history.append(AIMessage(content=response_text))
            else:
                print(
                    "\nNo Epic content available. Use 'outline epic' first or 'evaluate epic <file>' to load an epic.\n"
                )
            continue
        elif user_input.lower() == "activate feature":
            if (
                hasattr(display_feature_outline, "current_feature")
                and display_feature_outline.current_feature
            ):
                # Send the current feature to the agent for coaching
                feature_to_activate = display_feature_outline.current_feature
                print("\n[ACTIVATING FEATURE FOR COACHING]")
                docs = retriever.invoke(feature_to_activate)
                context = format_docs(docs) if docs else "No relevant context found."
                response = chain.invoke(
                    {
                        "user_input": f"Please provide targeted coaching and feedback on this feature:\n\n{feature_to_activate}",
                        "context": context,
                        "chat_history": chat_history,
                    }
                )
                response_text = (
                    response.content if hasattr(response, "content") else str(response)
                )
                print("\nAgent:")
                print(response_text)
                print()
                # Add to history
                chat_history.append(HumanMessage(content=feature_to_activate))
                chat_history.append(AIMessage(content=response_text))
            else:
                print(
                    "\nNo Feature content available. Use 'outline feature' first or 'evaluate feature <file>' to load a feature.\n"
                )
            continue
        elif user_input.lower() == "activate pi objectives":
            if (
                hasattr(display_pi_objectives_outline, "current_pi")
                and display_pi_objectives_outline.current_pi
            ):
                # Send the current PI objectives to the agent for coaching
                pi_to_activate = display_pi_objectives_outline.current_pi
                print("\n[ACTIVATING PI OBJECTIVES FOR COACHING]")
                docs = retriever.invoke(pi_to_activate)
                context = format_docs(docs) if docs else "No relevant context found."
                response = chain.invoke(
                    {
                        "user_input": f"Please provide targeted coaching and feedback on these PI Objectives:\n\n{pi_to_activate}",
                        "context": context,
                        "chat_history": chat_history,
                    }
                )
                response_text = (
                    response.content if hasattr(response, "content") else str(response)
                )
                print("\nAgent:")
                print(response_text)
                print()
                # Add to history
                chat_history.append(HumanMessage(content=pi_to_activate))
                chat_history.append(AIMessage(content=response_text))
            else:
                print(
                    "\nNo PI Objectives content available. Start by providing PI Objectives details in conversation or use 'evaluate'.\n"
                )
            continue
        elif user_input.lower() == "new epic":
            display_epic_outline.current_epic = None
            print("\n[NEW EPIC SESSION] Previous epic cleared. Ready for new epic.\n")
            continue
        elif user_input.lower() == "new feature":
            display_feature_outline.current_feature = None
            print(
                "\n[NEW FEATURE SESSION] Previous feature cleared. Ready for new feature.\n"
            )
            continue
        elif user_input.lower() == "new pi objectives":
            display_pi_objectives_outline.current_pi = None
            print(
                "\n[NEW PI OBJECTIVES SESSION] Previous PI objectives cleared. Ready for new objectives.\n"
            )
            continue
        elif user_input.lower() in ["quit", "exit", "q"]:
            print("Exiting. Thank you for today!")
            break
        elif user_input.lower().startswith("evaluate epic "):
            # Extract filename: "evaluate epic path/to/epic.txt"
            filepath = user_input[13:].strip()
            if not filepath:
                print(
                    "Please provide a file path. Usage: evaluate epic ./path/to/epic.txt"
                )
                continue
            epic_content = load_epic_file(filepath)
            if epic_content:
                evaluate_epic_command(epic_content, chain, retriever)
            continue
        elif user_input.lower().startswith("evaluate feature "):
            # Extract filename: "evaluate feature path/to/feature.txt"
            filepath = user_input[16:].strip()
            if not filepath:
                print(
                    "Please provide a file path. Usage: evaluate feature ./path/to/feature.txt"
                )
                continue
            feature_content = load_epic_file(filepath)
            if feature_content:
                # Use similar evaluation for features
                eval_prompt = f"""Please evaluate the following Feature against SAFe best practices and the template:

{feature_content}

Provide feedback on: 1) Feature name clarity, 2) Description completeness, 3) Benefit hypothesis clarity, 4) Acceptance criteria (should be in Gherkin format with Given-When-Then), and 5) Recommendations for improvement."""
                docs = retriever.invoke(eval_prompt)
                context = format_docs(docs) if docs else "No relevant context found."
                response = chain.invoke(
                    {"user_input": eval_prompt, "context": context, "chat_history": []}
                )
                response_text = (
                    response.content if hasattr(response, "content") else str(response)
                )
                print("\n" + "=" * 80)
                print("FEATURE EVALUATION RESULTS")
                print("=" * 80 + "\n")
                print(response_text)
                print("\n" + "=" * 80 + "\n")

                # Store the feature content for outline display
                display_feature_outline.current_feature = feature_content
            continue

        if not user_input:  # Skip empty inputs
            continue

        # Build context-aware user input (include active epic/feature/pi if available)
        context_prefix = ""
        if (
            hasattr(display_epic_outline, "current_epic")
            and display_epic_outline.current_epic
        ):
            context_prefix += (
                f"\n[ACTIVE EPIC CONTEXT]\n{display_epic_outline.current_epic}\n"
            )
        if (
            hasattr(display_feature_outline, "current_feature")
            and display_feature_outline.current_feature
        ):
            context_prefix += f"\n[ACTIVE FEATURE CONTEXT]\n{display_feature_outline.current_feature}\n"
        if (
            hasattr(display_pi_objectives_outline, "current_pi")
            and display_pi_objectives_outline.current_pi
        ):
            context_prefix += f"\n[ACTIVE PI OBJECTIVES CONTEXT]\n{display_pi_objectives_outline.current_pi}\n"

        # Combine active context with user input
        full_user_input = context_prefix + user_input if context_prefix else user_input

        # 1) Fetch relevant documents
        docs = retriever.invoke(full_user_input)
        context = (
            format_docs(docs)
            if docs
            else "No relevant context found in knowledge base."
        )

        # Debug: Show what context was found
        if docs:
            print(f"\n[DEBUG] Found {len(docs)} relevant document(s)")

        # 2) Run the chain with context + user_input + history
        response = chain.invoke(
            {
                "user_input": full_user_input,
                "context": context,
                "chat_history": chat_history,
            }
        )

        # Extract response text
        response_text = (
            response.content if hasattr(response, "content") else str(response)
        )

        print("\nAgent:")
        print(response_text)
        print()

        # Track Epic and Feature content from conversation
        if "epic" in user_input.lower():
            display_epic_outline.current_epic = user_input
        if "feature" in user_input.lower():
            display_feature_outline.current_feature = user_input
        if "pi objectives" in user_input.lower():
            display_pi_objectives_outline.current_pi = user_input

        # 3) Add to conversation history for next iteration
        chat_history.append(HumanMessage(content=user_input))
        chat_history.append(AIMessage(content=response_text))


# ============================================================================
# API Module Interface - For use with FastAPI server (app.py)
# ============================================================================

# Global context for API use
active_context = {
    "epic": None,
    "feature": None,
    "pi_objectives": None,
    "chat_history": [],
}

# Global chain and retriever (initialized on first call)
_chain = None
_retriever = None


def initialize_vector_store(
    knowledge_dir: str = "./knowledge_base", persist_dir: str = "./rag_db"
):
    """Initialize the vector store and return the chain and retriever."""
    global _chain, _retriever
    if _chain is None or _retriever is None:
        _chain, _retriever = build_epic_pm_coach_with_rag(knowledge_dir, persist_dir)
    return _chain, _retriever


def get_retrieval_chain():
    """Get the initialized retrieval chain. Initializes if not already done."""
    global _chain, _retriever
    if _chain is None:
        initialize_vector_store()
    return _chain
