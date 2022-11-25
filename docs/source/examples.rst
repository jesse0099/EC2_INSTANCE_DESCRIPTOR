########
Examples
########

******************
Installation/Usage
******************

**Project Public Repository :**  `GitHub Repository`_.

The Script is being developed assuming an AWS lambda function execution environment, according to 
the specification of SAM \(Serverless Application Model\).

.. todo:: 
    The template is not present in the public repository due to security reasons. 
    Future versions will include a secure template defining all necessary AWS resources.


Required tools
**************

    Tools installation and documentation references:
        * `Poetry Docs and Install`_.
        * `SAM cli Install`_.
        * `Docker Install`_.
        * `Python Docs and Install \(3.9\)`_.


Dependencies
************

    Presupposing all the above tools are installed and the repository has been cloned. Also, a suitable
    ``template.yaml`` file is available at the repository root directory. The next step is to activate or
    create the virtual environment.

Poetry venv activation/creation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    At the root of the repository, the following files are available:

    * ``poetry.toml``: Local poetry configuration file.
    * ``pyproject.toml``: Dependencies configuration file.
    * ``poetry.lock``: Dependencies lock file.

    The ``poetry.toml`` file contains the followings **Poetry Virtualenvs** options:

        * **create** = *true* 
            If no other venv is active, It'll create one. Otherwise, nothing is done.

        * **in-project** = *true*
            If set to true, the virtual environment will be created in the project root directory
            under *.venv/*.

    Poetry will try to create the virtual environment on calls to the command ``poetry``. But this can
    be done manually by executing `poetry shell`_.

    Once the virtual environment is created, activating it is as easy as executing the
    followings  One-Liners:

    * ``source $(poetry env info --path)/bin/activate``
    * ``&((poetry env info --path) + "\Scripts\activate.ps1")``

Poetry venv deactivation/exit
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    Once the virtual environment is active and a shell to it is present, deactivation/exit can be
    achieved by the followings commands:

    * ``deactivate``
    * ``exit``

    In depth information can be found in: 

Poetry, dependencies installation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*Inside the virtual environment*

|   The following command will install all the not optional dependencies defined in the ``pyproject.toml``:
    
        ``poetry install``: The install command reads the ``pyproject.toml`` file from the current project, 
        resolves the dependencies, and installs them.

|   However, optional dependencies wont be, so we have to this manually:

        ``poetry install -E {extra_name}``: Install the specified extra group.

|    Optional dependencies installation:

       * ``poetry install -E all_extras``      
            **Install all extras**

       * ``poetry install -E build_and_debug``
            **Install boto3 and debugpy**

       * ``poetry install -E docs``            
            **Install sphinx and sphinx-rtd-theme**

Execution 
*********

Build
^^^^^
| ``sam build``

.. note::
    Execute at repository root level. In depth information can be found in: 

Local Invoke
^^^^^^^^^^^^
| ``sam local invoke``

.. note::
    Execute at repository root level. In depth information can be found in: 

Debug 
***** 

VS Code AWS Toolkit
^^^^^^^^^^^^^^^^^^^

Debugpy
^^^^^^^

Deploy
******
| ``sam deploy --s3-bucket {My S3 Bucket}``
|       ``--s3-prefix {My S3 Bucket Prefix}`` 
|       ``--image-repository {AWS ECR URI}``
|       ``--region {AWS Region name}``
|       ``--stack-name {AWS Stack Name}`` 
|       ``--capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM``

.. note::
    Execute at repository root level. In depth information can be found in: 



.. todo::
    Installation/Usage documentation is not as detailed as I would like. 
    Fix it when the time comes.
.. todo::
    Explain the reason to create optional dependencies.
.. todo::
    Populate in depth information where required. When the time comes.

.. _SAM cli Install: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html
.. _Docker Install: https://docs.docker.com/get-docker/
.. _Poetry Docs and Install: https://python-poetry.org/docs/
.. _Python Docs and Install \(3.9\): https://www.python.org/downloads/
.. _GitHub Repository: https://github.com/jesse0099/EC2_INSTANCE_DESCRIPTOR
.. _poetry shell: https://python-poetry.org/docs/cli/#:~:text=has%20no%20option.-,shell,-The%20shell%20command