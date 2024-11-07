# Lab 2: Deploying a Simple "Hello World" Application on Amazon EKS

## Objective
Deploy a simple "Hello World" application to ensure the Kubernetes cluster on Amazon EKS is functioning correctly.

## Prerequisites
- Ensure you have an Amazon EKS cluster set up and configured with `kubectl`.
- Make sure your `kubectl` context is set to your EKS cluster. You can verify this with the command:
  ```bash
  kubectl config current-context
  ```

## Steps

### Step 1: Create a Deployment

1. **Create a YAML file for the deployment**:
   - Name the file `hello-world-deployment.yaml`.
   - Use the `nginxdemos/hello` Docker image.
   - Define a simple deployment with 3 replicas.

   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: hello-world
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: hello-world
     template:
       metadata:
         labels:
           app: hello-world
       spec:
         containers:
         - name: hello-world
           image: nginxdemos/hello
           ports:
           - containerPort: 80
   ```

   Save this file to your working directory.

2. **Deploy to Kubernetes**:
   - Apply the deployment using `kubectl`:
     ```bash
     kubectl apply -f hello-world-deployment.yaml
     ```
   - This command will create the deployment based on the specifications in the YAML file.

### Step 2: Expose the Deployment

1. **Create a YAML file for the service**:
   - Name the file `hello-world-service.yaml`.
   - Expose the deployment using a LoadBalancer service.

   ```yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: hello-world-service
   spec:
     type: LoadBalancer
     ports:
     - port: 80
       targetPort: 80
     selector:
       app: hello-world
   ```

   Save this file to your working directory.

2. **Create the service in Kubernetes**:
   - Apply the service configuration:
     ```bash
     kubectl apply -f hello-world-service.yaml
     ```
   - This command will create a service that exposes your deployment to the internet via a LoadBalancer.

### Step 3: Access the Application

1. **Retrieve the External IP**:
   - It may take a few minutes for the LoadBalancer to be provisioned and receive an external IP address.
   - Check the service to get the external IP:
     ```bash
     kubectl get svc hello-world-service
     ```
   - Look for the `EXTERNAL-IP` in the output.

2. **Access the Application**:
   - Open a web browser and navigate to `http://<EXTERNAL-IP>`, replacing `<EXTERNAL-IP>` with the IP address you retrieved. (It can take few minutes to get all things in place)
   - You should see the "Hello World" page served by the Nginx container.

## Verification
Ensure that the "Hello World" application is accessible via the external IP and that it correctly displays the greeting. This confirms that your Kubernetes cluster and deployment are configured correctly.

## Cleanup
To clean up the resources created during this lab, run:
```bash
kubectl delete -f hello-world-deployment.yaml
kubectl delete -f hello-world-service.yaml
```
These commands will remove the deployment and service from your Kubernetes cluster, freeing up resources.

By following these detailed steps, even beginners can successfully deploy and manage a simple application on Amazon EKS, gaining confidence in using Kubernetes for more complex deployments.