# Genesis images

Repo with configuraitons and build tools for Genesis images.

# Install

To install the `gcl_images` package, follow these steps:

1. Clone the repository:
    ```sh
    git clone https://github.com/infraguys/gcl_images.git
    ```

2. Navigate to the project directory:
    ```sh
    cd gcl_images
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Install the package using pip:
    ```sh
    pip install .
    ```

# Usage

A new command `genesis-images` is available now. To build an image use a command like this:

```sh
genesis-images build /path/to/image/configs
```

For more detailed documentation:
```sh
genesis-images build --help
```