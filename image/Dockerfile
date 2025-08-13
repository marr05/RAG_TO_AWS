# We use a base prebuilt image from AWS Lambda for python.

FROM public.ecr.aws/lambda/python:3.12

# Next we copy all the requirements into the image's environment variable, which is also the task root
# This env var is something that comes with the base python image drom aws, we do not need to create it.
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# To make SQLite3 work for chroma in lambda runtime
RUN pip install pysqlite3-binary

# Next we install the specified packages, or upgrade to the specific versions if already present.
RUN pip install -r requirements.txt --upgrade

# For local testing, we dedicate a port
EXPOSE 3000

# Set IS_USING_IMAGE_RUNTIME env var
# This flag can be used in the python script to check if we need to use the newly added version of the library, or copy the database to the /tmp folder. 
ENV IS_USING_IMAGE_RUNTIME=TRUE        

# Then we copy all the files that are in ./src
COPY src/app_api_handler.py ${LAMBDA_TASK_ROOT}

COPY src/app_work_handler.py ${LAMBDA_TASK_ROOT}

COPY src/query_model.py ${LAMBDA_TASK_ROOT}

COPY src/rag_app ${LAMBDA_TASK_ROOT}/rag_app

COPY src/data ${LAMBDA_TASK_ROOT}/data