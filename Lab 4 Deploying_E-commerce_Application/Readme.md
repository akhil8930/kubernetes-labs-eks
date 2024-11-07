# Lab 4: Deploying a Simple E-commerce Application on Amazon EKS

This guide provides detailed steps to deploy a simple e-commerce application using a microservices architecture on Amazon Elastic Kubernetes Service (EKS). The application consists of three main components: a frontend service, a product catalog service, and a cart service.

## Prerequisites

- AWS CLI installed and configured
- Docker installed
- `kubectl` installed and configured
- `eksctl` installed
- Helm installed

## Step 1: Set Up the EKS Cluster

Create an EKS cluster named `my-ecommerce` in the `ap-south-1` region with three `t3.medium` nodes.

```bash
eksctl create cluster --name my-ecommerce --region ap-south-1 --nodegroup-name ecommerce-nodes --node-type t3.medium --nodes 3 --nodes-min 1 --nodes-max 4 --managed
```

## Step 2: Configure `kubectl`

Update your kubeconfig to ensure `kubectl` can communicate with your new EKS cluster.

```bash
aws eks --region ap-south-1 update-kubeconfig --name my-ecommerce
```

## Step 3: Deploy NGINX Ingress Controller

### 3.1 Install NGINX Ingress Controller using Helm

Add the official NGINX Ingress controller Helm repository and update your local Helm chart repository cache:

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
```

Install the NGINX Ingress controller in the default namespace:

```bash
helm install ingress-nginx ingress-nginx/ingress-nginx --set controller.publishService.enabled=true
```

### 3.2 Deploy the Ingress Resource

Deploy the Ingress resource that defines how traffic should be routed to your services:

```bash
kubectl apply -f ingress-class.yaml
kubectl apply -f ecommerce-ingress.yaml
```

Wait for the Ingress controller to receive an external IP:

```bash
kubectl get ingress ecommerce-ingress -w
```

## Step 4: Update Frontend Configuration

**Important:** Note the external IP from the output of the previous command and update the `index.html` in the frontend application to use this IP.

### 4.1 Modify `index.html` in Frontend folder.

Locate the following script section in your `index.html` file:

```html
<script>
    const INGRESS_URL = 'http://<external-ip>'; // Replace <external-ip> with the actual IP address

    // Function to fetch products from the catalog service
    function fetchProducts() {
        fetch(`${INGRESS_URL}/api/catalog/products`)
            .then(response => response.json())
            .then(data => {
```

Replace `<external-ip>` with the actual external IP address you noted earlier.

## Step 5: Build and Push Docker Images

### 5.1 Create an ECR Repository

Create a repository in Amazon ECR for each of the microservices:

```bash
aws ecr create-repository --repository-name ecommerce-frontend --region ap-south-1
aws ecr create-repository --repository-name ecommerce-catalog --region ap-south-1
aws ecr create-repository --repository-name ecommerce-cart --region ap-south-1
```

### 5.2 Build Docker Images

Navigate to each service directory and build the Docker image:

```bash
# For the frontend service
cd frontend
docker build -t ecommerce-frontend .

# For the catalog service
cd ../catalogue
docker build -t ecommerce-catalog .

# For the cart service
cd ../cart
docker build -t ecommerce-cart .
```

### 5.3 Tag and Push to ECR

Retrieve the login command to authenticate your Docker client to your registry:

```bash
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.ap-south-1.amazonaws.com
```

Tag your images and push them to the ECR repositories:

```bash
docker tag ecommerce-frontend <aws_account_id>.dkr.ecr.ap-south-1.amazonaws.com/ecommerce-frontend:latest
docker push <aws_account_id>.dkr.ecr.ap-south-1.amazonaws.com/ecommerce-frontend:latest

docker tag ecommerce-catalog <aws_account_id>.dkr.ecr.ap-south-1.amazonaws.com/ecommerce-catalog:latest
docker push <aws_account_id>.dkr.ecr.ap-south-1.amazonaws.com/ecommerce-catalog:latest

docker tag ecommerce-cart <aws_account_id>.dkr.ecr.ap-south-1.amazonaws.com/ecommerce-cart:latest
docker push <aws_account_id>.dkr.ecr.ap-south-1.amazonaws.com/ecommerce-cart:latest
```

## Step 6: Deploy to Amazon EKS

Use `kubectl` to deploy each service to your EKS cluster:

```bash
cd ../
kubectl apply -f catalog-deployment.yaml
kubectl apply -f catalog-service.yaml
kubectl apply -f cart-deployment.yaml
kubectl apply -f cart-service.yaml
kubectl apply -f frontend-deployment.yaml
kubectl apply -f frontend-service.yaml
```

## Step 7: Verify Deployment

Ensure all services are running correctly and are accessible:

```bash
kubectl get deployments
kubectl get pods
kubectl get services
kubectl get ingress
```

Check the external IP or DNS name provided by the LoadBalancer in the ingress list to access your application.

## Cleanup Steps

To clean up the resources created during this lab, follow these steps:

1. **Delete the Kubernetes resources**:
   ```bash
   kubectl delete -f frontend-deployment.yaml
   kubectl delete -f frontend-service.yaml
   kubectl delete -f catalog-deployment.yaml
   kubectl delete -f catalog-service.yaml
   kubectl delete -f cart-deployment.yaml
   kubectl delete -f cart-service.yaml
   kubectl delete -f ecommerce-ingress.yaml
   kubectl delete -f ingress-class.yaml
   ```

2. **Delete the ECR repositories**:
   ```bash
   aws ecr delete-repository --repository-name ecommerce-frontend --region ap-south-1 --force
   aws ecr delete-repository --repository-name ecommerce-catalog --region ap-south-1 --force
   aws ecr delete-repository --repository-name ecommerce-cart --region ap-south-1 --force
   ```

3. **Delete the EKS cluster**:
   ```bash
   eksctl delete cluster --name my-ecommerce --region ap-south-1
   ```

By following these steps, you have successfully deployed and cleaned up a basic e-commerce application on Amazon EKS using a microservices architecture. This setup is scalable and ready for further expansion.