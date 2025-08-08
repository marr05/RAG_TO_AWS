# RAG_TO_AWS

A Python RAG App using FLASK. To deploy on AWS. Using AWS Bedrock for LLM access. Amazon_Titan_Text for embeddings, and Llama 3 : 70b Instruct for inference.

## Deployment HACKS

## Challenges

    # Pysqlite3 that comes with the base image is outdated -> it is required by Chroma_DB -> RUN pip install pysqlite3-binary -> its a built in lib,
    # so just installing the binary isnt enough. We also need to add this snippet in our code:
        __import__("pysqlite3")
        sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
        -> to replace the pysqlite instance in our runtime on aws.

    # Can only write to /tmp directory -> Chroma needs to be in a path that has read and write capacity. In AWS we only get this capacity in the temp directory.
        To resolve this, we can copy all of our database into the /tmp directory when we're running it in AWS lambda. 
        - Lambda containers stay warm and are active for upto 15min, we can do this only once and then check to see if the files exist. 

    # The location of instructions in the dockerfile is important, since it runs from top to bottom, and caches the layer of the image at each instruction.

    # For instructions that I want to run once, and are rarely needed to be changed, we can add them to the top of the docker file, like installing requirements, can be on the top, whereas, copying files (which can change frequently, can be at the bottom). 
