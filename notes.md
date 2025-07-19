# notes for the embrace ai initiative, get more familiar w. LLM coding

## kata 1

the task is to implement a parser using language of my choice

### questions by rinat

- "how can you be confident that the parser works"
- "what were the steps you took"
- "what were the steps"

### ideas sparked by the questions

> put in the source doc, let the LLM read it, give me its' implementation plan - "design document"
 
> generate a "definition of done" and add it to the instructions, add make file commands for format, tests
 
> add the tools and frameworks that should be used, versions; pydantic, ruff, uv, mypy
 
> think through the structure myself give it to LLM, let it summarize
 
> think about edge cases, failure modes, tests --> let the LLM write out detailed notes on how this could fail, how should it fail, assertions
 
> use cookiecutter or similar to at the same time set up a model repo
 