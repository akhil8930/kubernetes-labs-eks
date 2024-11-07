# Lab 7: CI/CD Pipeline Integration with GitHub Actions for an Application on Amazon EKS

This comprehensive guide outlines the steps to establish a CI/CD pipeline using GitHub Actions for automated deployment of an application on Amazon EKS. It includes setting up a source control repository, configuring GitHub Actions to build and push Docker images, and integrating with EKS for automated deployments.

## Prerequisites

- AWS CLI installed and configured.
- `kubectl` installed and configured.
- Access to a GitHub account.

## Step 1: Set Up a Source Control Repository

### 1.1 Create a New GitHub Repository
Create a new repository on GitHub to store the source code of your application.

1. **Log in to GitHub** and click on the "New repository" button.
2. **Name your repository** (e.g., `application`).
3. **Initialize the repository** with a README and choose the appropriate visibility.
4. **Clone the repository** to your local machine:

```bash
git clone https://github.com/<your-username>/application.git
```

5. **Navigate to the repository directory**:

```bash
cd application
```
6. **Create a simple Flask application**. Save this as `app.py`:

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Platform!"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
```

7. **Create a Dockerfile** to containerize the application. Save this as `Dockerfile`:

```Dockerfile
# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir flask

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run app.py when the container launches
CMD ["python", "app.py"]
```

## Step 2: Create an Amazon ECR Repository

Create a repository in Amazon ECR for your application:

```bash
aws ecr create-repository --repository-name application-repo --region <your-region>
```

Retrieve the ECR repository URI:

```bash
aws ecr describe-repositories --repository-names application-repo --region <your-region> --query 'repositories[0].repositoryUri' --output text
```

Note this URI as you will need it to configure your GitHub Actions workflow.

## Step 3: Configure GitHub Actions

### 3.1 Create GitHub Actions Workflow
Create a `.github/workflows` directory in your repository and add a workflow file (e.g., `ci-cd.yml`):

```bash
mkdir -p .github/workflows
```

### 3.2 Define Build, Test, and Deployment Stages
Create the `ci-cd.yml` file in workflows directory to define the CI/CD pipeline including Docker image build and push:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches:
      - main

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v1
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: <your-region>
      
      - name: Log in to Amazon ECR
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v2
        with:
          context: .
          file: ./Dockerfile
          push: true
          tags: ${{ secrets.ECR_REPOSITORY_URI }}:${{ github.sha }}

  deploy:
    runs-on: ubuntu-latest
    needs: build-and-push
    steps:
      - uses: actions/checkout@v2
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: <your-region>

      - name: Update kubeconfig
        run: |
          aws eks --region <your-region> update-kubeconfig --name my-ecommerce

      - name: Update Kubernetes deployment image
        run: |
          sed -i 's|imagename:latest|${{ secrets.ECR_REPOSITORY_URI }}:${{ github.sha }}|g' ./k8s/deployment.yml

      - name: Deploy to EKS
        run: |
          kubectl apply -f k8s/
```
Make sure to replace <your-region> with the AWS region where your EKS cluster and ECR repository are located.

### 3.3 Set Up Secrets in GitHub Repository
Configure AWS credentials and ECR repository URI as secrets in your GitHub repository:

1. Navigate to your repository on GitHub.
2. Go to Repository Settings > Secrets and Variables > Actions.
3. Click on "New repository secret" and add `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `ECR_REPOSITORY_URI` with appropriate values.

## Step 4: Integrate with EKS

### 4.1 Use Kubernetes Manifests for Deployment
Ensure your Kubernetes manifests (e.g., deployments, services) are stored in a directory `k8s/` in your repository. Here is deployment manifest (`deployment.yml`):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: application-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: application
  template:
    metadata:
      labels:
        app: application
    spec:
      containers:
      - name: application
        image: imagename:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 5000
```

### 4.2 Create a Kubernetes Service
Create a service to expose your application (`service.yml`):

```yaml
apiVersion: v1
kind: Service
metadata:
  name: application-service
spec:
  type: LoadBalancer
  selector:
    app: application
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
```
## Step 5: Push the code to Github Repository
```bash
git add .
git commit -m "Initial application code"
git push origin main
```

## Step 6: Verification

### 6.1 Application Deployment
AS soon as you push the code, this should trigger workflow and deploy the application. Check it by fetching the external ip from service in k8s.

### 6.2 Make a Code Change
Make a change in your application code message in app.py

### 6.3 Push the Change to the Repository
Push the change to your GitHub repository:

```bash
git add .
git commit -m "Update application"
git push origin main
```

### 6.4 Verify Automatic Deployment
Monitor the GitHub Actions workflow to ensure it triggers automatically and deploys the changes to your EKS cluster. Check the application to confirm the update was successful.

## Cleanup Steps

To clean up the resources created during this lab, follow these steps:

1. **Delete the GitHub repository** (if necessary):
   - Go to the repository settings on GitHub and scroll down to the "Danger Zone". Click "Delete this repository".

2. **Delete the ECR repository**:
   ```bash
   aws ecr delete-repository --repository-name application-repo --region <your-region> --force
   ```

3. **Delete the Kubernetes resources**:
   ```bash
   kubectl delete -f k8s/
   ```

4. **Delete the EKS cluster** (if created specifically for this lab):
   ```bash
   aws eks delete-cluster --name <cluster-name> --region <your-region>
   ```

By following these steps, you have successfully set up a CI/CD pipeline using GitHub Actions for your application on Amazon EKS, enabling automated builds, tests, and deployments. This setup enhances your development workflow and ensures consistent and reliable updates to your application.