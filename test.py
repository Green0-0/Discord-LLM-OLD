import sentencepiece

def countTokens(prompt):
    sp = sentencepiece.SentencePieceProcessor(model_file='tokenizer.model')
    prompt_tokens = sp.encode_as_ids(prompt)
    return len(prompt_tokens)

my_prompt = "!@#$%^aaaa hey how are you im great dictionaries aaasadas"

print(countTokens(my_prompt))
# Returns "3"