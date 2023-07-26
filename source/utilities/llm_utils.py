import os
import openai

from utilities.cache import cachethis

openai.api_key = os.environ.get('OPENAI_API_KEY', 'not the token')

@cachethis
def openai_query(query, model='gpt-3.5-turbo-0613', role=None, temperature = 0.0):    
    args = {
        "model": model,
        "temperature": temperature,
        "messages": [{"role": "user", "content": query}]
    }
    if role:
        args['messages'] = [{"role": "system", "content": role}] + args['messages']
    completion = openai.ChatCompletion.create(
        model=model,
        temperature = temperature,
        messages=[
            {"role": "user", "content": query}
        ]
    )

    return completion.choices[0].message['content']
