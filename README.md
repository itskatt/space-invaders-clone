# Space Invaders

## Running the game

1) **Clone it and cd into it**

    ```sh
    git clone ...
    cd ...
    ```

2) **Setup an virtual environement (optional)**
    This allows you to safely install the game's dependencies, without interfearing with your other projects.

    ```sh
    # create it
    python -m venv env
    # activate it
    source env/bin/activate  # unix (bash)
    env\bin\activate.bat  # windows (cmd.exe)
    # see https://docs.python.org/fr/3/library/venv.html for more info
    ```

3) **Install the dependencies**

    ```sh
    python -m pip install -r requirements.txt
    ```

4) **Run the game**

    ```sh
    python run.py
    # or
    python -m ...
    ```
