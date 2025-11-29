# Technical Proposal (Pre Project)

## Note:
> The HLD, LLD, Architecture, KPI, Specs, and other documents will be created after the project(dev) is completed.  

#### project name: BOT-GPT

#### project description: 
the project is to create a bot that can interact with the user and provide information about the user's query,

#### client requirements: (high level)
- LLM call
- using RAG flow
- can read documents
- can answer questions in a conversational manner
- API call
- a basic database design with CRUD
- 

#### my take
- since its just a prototype application, we have to make it simple and easy to use and monitor, cost should be free or negligible.

##### things we will not do
1. no complex database
    - for the prototype, a single sqlite database is enough.
2. no backend as a service BaaS (firebase, supabase, etc)
    - since its a mandatory requirement, but we can avoid this for a prototype application.
    - we can skip user authentication
    - we can skip server-side validation and secure key management (which prevent JWT (JSON Web Token) exploitation), since it will be used only by developers.

3. no advanced EDA on documents
    - EDA is used when user uploads documents to normalize the data, we can skip this step but can be added later if needed. although, we can use simple EDA to extract text from documents.

4. no complex vector database
    - we will be using simple vector database structure for demonstration that the data is getting stored and retrieved. which is ok for basic RAG architecture.

5. no AWS EC2 or similar services
    - to cut the cost, since we are keeping the application small, there is no need for EC2 or similar services, 
    - we can use google cloud run or app engine for deployment

Note: Although we the entire application runs on low cost(free till now) there are some things that we are deciding to go with a paid service: 
    - for text embedding, we will be using OpenAI's embedding API, although we can use SentenceTransformers a free open source alternative, but it requires pytorch as a requirement, which can increase the cost of deployment way high as compared to the cost of OpenAI embedding API
    - Approx cost of text-embedding-3-small: 1$/62500pages

##### things we will do
1. tech stack
    - frontend: html, css, js
    - backend: python, flask
    - LLM: gemini free tier
    - framework: langchain
    - embedding: openai
    - deployment: google cloud run
    - database: mysql, pinecone
    - container: docker, docker hub
    - version control: github