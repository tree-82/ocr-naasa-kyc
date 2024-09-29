# FAST API server to read the data in ID
Use Python 3.8.19

## Running the project for the first time
It is suggested to create a different environment for installing the dependencies. It can be done using conda or venv.

### Using conda:
1. Create a new conda environment: <br>`conda create -n <environment_name> python=3.8.19`

2. Switch to the conda environment: <br> `conda activate <environment_name>`

3. Install the dependencies using:<br>
`pip install -r requirements.txt`


### Using python venv
1. **Create a virtual environment:** <br> `python -m venv <venv_name>`
<br><br>

2. **Activate the virtual environemnt:** <br>
    a. For Linux Based OS or Mac-OS: <br> `source <venv_name>/bin/activate`

    b. For Windows in CMD: <br> `.\venv\Scripts\activate.bat`

    c. For Windows with PowerShell: <br> `.\venv\Scripts\activate.ps1`

    d. For Windows With Unix Like Shells (For Example Git Bash CLI).<br>
    `source venv/Scripts/activate`
<br><br>

3. **Install the dependencies using:**<br>
`pip install -r requirements.txt`


## Instruction to run the server

1. Create a .env file that contains the following variables:<br>
    ```
    HOST='localhost'
    PORT=3030
    ```

2. Run the server using the following script: <br>`python main.py`