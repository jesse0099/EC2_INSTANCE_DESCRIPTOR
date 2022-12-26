FROM python:3.9-alpine

ENV AWS_REGION=us-east-1

# Install the function's dependencies using file requirements.txt
# from your project folder.
COPY ./app/ .
RUN  pip3 install -r requirements.txt

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "python", "./ec2_instances_descriptor.py"]
