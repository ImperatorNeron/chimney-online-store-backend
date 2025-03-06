# PostGuardAPI - Task from Starnavi

## Overview

PostGuardAPI is a RESTful API designed for managing user-generated content, including posts and comments. It incorporates artificial intelligence for automatic comment blocking and intelligent auto-replies to user inquiries. The API also provides analytical insights into comments, including metrics on created and blocked comments, authentication by jwt etc.

## Requirements
- [Docker](https://www.docker.com/get-started/)
- [Docker Compose](https://docs.docker.com/compose/install/)


## How to Use

1. Clone the repository:
```bash
git clone https://github.com/ImperatorNeron/post-guard-api.git
cd your_repository
```
2. Install all required packages in **Requirements** section.
3. Set up environment variables. Create a .env file in the root directory and specify the required configurations. You can use .env.template.
4. reate a directory named certificates within the app folder, and generate the private.pem and public.pem files for JWT token generation. You can do this using the following commands: 
    ```bash
    # Generate an RSA private key, of size 2048
    openssl genrsa -out jwt-private.pem 2048
    # Extract the public key from the key pair, which can be used in a certificate
    openssl rsa -in jwt-private.pem -outform PEM -pubout -out jwt-public.pem
    ```
5. Set up a virtual environment in the app directory and install 
   ```bash 
   pip install scons
   pip install poetry
   poetry install
   ```
6. Start the application using ```scons up``` and after that, run the database migrations ```scons migrate-up```.
7. Your project is now ready for use!

### Implemented Commands

#### Application
- ```scons up``` - up application
- ```scons logs``` - follow the logs in app container
- ```scons down``` - down application and all 
- ```scons run-tests``` - run all tests 

#### Database migrations
- ```scons auto-migrations``` - autocreate file of tables
- ```scons migrate-up``` - apply migrations to head
- ```scons migrate-down``` - down migrations t base

## License

This project is licensed under the MIT License - see the [LICENSE](https://en.wikipedia.org/wiki/MIT_License) file for details.