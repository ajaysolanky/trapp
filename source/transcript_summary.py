from utilities.llm_utils import openai_query

class TranscriptSummary(object):
    def get_summary(self, input_text, target_language):
        prompt = f"""Generate a less than 5 word summary of the following text. Return the summary in {target_language}
TEXT: {input_text}
SUMMARY:"""
        return openai_query(prompt, model="gpt-4")
    
# print(TranscriptSummary().get_summary("Hi my name is Tom and I'm reaching out about some leaky plumbing", "Spanish"))