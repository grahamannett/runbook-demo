from datetime import timezone

rag_endpoint = "http://localhost:11434"
rag_api_key = "ollama"  #
app_password = "graham"


saved_runbooks_dir = "./saved/runbooks"

rag_docs_file_dir = "./saved/rag"
# # table or file, file is easier to inspect
rag_docs_storage_type = "table"  # StorageType.TABLE


tz = timezone.utc


MAX_QUESTIONS = 10
INPUT_BOX_ID = "input-box"

SCROLL_DOWN_ON_LOAD = True  # this is helpful if i want to look at bottom of page while dev
