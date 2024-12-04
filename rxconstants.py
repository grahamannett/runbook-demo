from datetime import timezone

rag_endpoint = "http://localhost:11434"
rag_api_key = "ollama"  #
app_password = "graham"


saved_runbooks_dir = "./saved/runbooks"
saved_rag_documents = "./saved/rag"

# rag_documents = "table"  # table or file, file is easier to inspect
rag_documents = "file"  # table or file, file is easier to inspect

tz = timezone.utc


MAX_QUESTIONS = 10
INPUT_BOX_ID = "input-box"

SCROLL_DOWN_ON_LOAD = False
