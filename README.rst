########################
EC2 INSTANCES DESCRIPTOR
########################
    
^^^^^^^^^^^^^^^^^^
Installation/Usage
^^^^^^^^^^^^^^^^^^

**Project Public Repository :**  `GitHub Repository`_.
**Detailed documentation :** `EC2_Descriptor`_.

EC2 instances descriptor is a script that wraps boto (Amazon Official SDK for python) to make it easier to use on traceability processes as well as to enforce “resources state changed” policies (creations, terminations, modifications). Also, a set of classes and methods is provided to interact with Airtable API (REST) without using an SDK.

It’s written and has been tested on Python 3.9.13. To avoid environment incompatibilities a venv is provided using Poetry.

The Script can be deployed locally and toward an AWS lambda function execution environment, according to 
the specification of SAM \(Serverless Application Model\).

Clone Project Repository
************************

Use git clone; 

.. code-block:: console
    git clone: https://github.com/jesse0099/EC2_INSTANCE_DESCRIPTOR

or your favorite method
for this task. 

.. _Docker Install: https://docs.docker.com/get-docker/
.. _Poetry Docs and Install: https://python-poetry.org/docs/
.. _Python Docs and Install \(3.9\): https://www.python.org/downloads/
.. _GitHub Repository: https://github.com/jesse0099/EC2_INSTANCE_DESCRIPTOR
.. _poetry shell: https://python-poetry.org/docs/cli/#:~:text=has%20no%20option.-,shell,-The%20shell%20command
.. _EC2_Descriptor: https://ec2-instance-descriptor.readthedocs.io/en/latest/
