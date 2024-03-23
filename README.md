# Spotify Pipeline - EC2, S3 & Apache
Developed a script which extracts playlist information from the Global - Top 50 Playlist from Spotify, using spotipy. The script was then deployed on to an AWS EC2 instance, where the execution of the script was managed by an Airflow server. Running the script uploads a .csv file to an AWS S3 bucket.

## Spotify API Credentials Setup
The script makes API calls to the Spotify database, and hence authentication tokens are required. 

Authentication tokens can be retrieved from making an account on https://developer.spotify.com/dashboard/.

1. Create an account using the above URL.
2. Login to the Spotify developer dashboard.
3. Press the button "Create app".
4. Fill in the required fields (use "http://localhost/" for the redirect uri). 
5. Click the button "Settings".
6. Note down the client ID and client secret.

## AWS EC2 Setup
1. Make an account on https://aws.amazon.com.
2. Login and select the region closest to you.
3. [Create an EC2 instance.](https://docs.aws.amazon.com/efs/latest/ug/gs-step-one-create-ec2-resources.html)
    * AMI - Ubuntu.
    * Instance Type - t3.large.
    * Create a key pair login (RSA) and download the .pem file.
    * Network settings - Check "Allow HTTPS trafic from the internet".
    * Network settings - Check "Allow HTTP traffic from the internet".
4. Go to the instance summary and select the "Security Tab".
5. Select the "Security groups". 
6. "Edit inbound rules". 
7. "Add rule".
    * Type - All traffic
    * Source - Anywhere-IPv4
8. "Save rules". 
9. [Create a new IAM role.](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create.html)
    * Trusted entity type - AWS service.
    * Service or use case - EC2.
    * Permission policies:
        * AmazonEC2FullAccess
        * AmazonS3FullAccess
10. [Modify the EC2 IAM role.](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html)
11. Launch the EC2 instance.
12. Open a terminal and change to the directory containing the .pem key pair. 
13. [SSH client connect to the EC2 instance.](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/connect-linux-inst-ssh.html)
    * Before connecting, run `chmod 400 pem_file_name.pem`.
14. Run the following shell commands:
    * `sudo apt-get update`.
    * `sudo apt install python3-pip`.
    * `sudo pip install apache-airflow`.
    * `sudo pip install pandas==2.1.3`.
    * `sudo pip install spotipy==2.23.0`.
    * `sudo pip install python-decouple==3.6`.
    * `sudo pip install Flask-Session==0.5.0`.
    * `sudo pip install s3fs==2024.2.0`.
15. Initiate the airflow server: `airflow standalone`.
16. Note down the airflow username and password.
17. Close the terminal and stop the EC2 instance.

## S3 Bucket Setup
1. Login to https://aws.amazon.com.
2. Select the region closest to you.
3. Create an S3 bucket with the default settings.

## Airflow Server Setup
1. [SSH client connect to the EC2 instance.](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/connect-linux-inst-ssh.html)
2. `cd airflow`.
3. `sudo nano airflow.cfg`.
4. Edit `dags_folder = /home/ubuntu/airflow/dags` to `dags_folder = /home/ubuntu/airflow/spotify_dag`.
5. Save and exit the changes.
6. `mkdir spotify_dag`.
7. `cd spotify_dag`.
8. `sudo nano spotify_dag.py`.
9. Copy the content from the Github repository.
10. Save and exit the changes.
11. `sudo nano spotify_etl.py`.
    * Change the last line of the code to the S3 bucket URL.
12. Copy the content from the Github repository.
13. Save and exit the changes.
10. `sudo nano .env`.
14. Copy the content from the github repository, note the spotify credentials. 
15. Save and exit the changes. 

## Usage Instructions

1. [SSH client connect to the EC2 instance.](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/connect-linux-inst-ssh.html)
2. `airflow standalone`.
3. Get the EC2 instance's public IPv4 DNS address and append ":8080" to the end. 
4. Open a browser and access the Apache Airflow dashboard.
5. Login to the Apache Airflow using the credentials created from starting the Airflow server.
6. Scroll down to the spotify_dag.
7. Run the dag and check the S3 bucket for the .csv file.
8. Happy days! Terminate the S3 bucket and EC2 instances to stop recurring charges!
