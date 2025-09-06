

def get_translate_prompt(target_languge: str  , text : str ) -> str:
    """Generate the system prompt for the word file creator agent."""
    return f"""
    you are a trasnlator translate from  input text to the target languge 
    {target_languge}
    Text to Tranlsate
    {text}
    """