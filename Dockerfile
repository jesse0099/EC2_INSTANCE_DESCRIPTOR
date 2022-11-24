FROM public.ecr.aws/lambda/python:3.9

# Copy function code
COPY ./app/ ${LAMBDA_TASK_ROOT}

# Install the function's dependencies using file requirements.txt
# from your project folder.

COPY ./app/requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "ec2_instances_descriptor.ec2_instances_desc" ]