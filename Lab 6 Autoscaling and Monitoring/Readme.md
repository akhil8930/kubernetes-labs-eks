# Lab 6: Autoscaling and Monitoring for an Application on Amazon EKS

This guide outlines the steps to implement autoscaling and monitoring for an application deployed on Amazon EKS. It includes setting up a Horizontal Pod Autoscaler (HPA), integrating monitoring tools such as Prometheus, and Grafana, and verifying the setup through load simulation.

## Prerequisites

- Application deployed on Amazon EKS.
- AWS CLI installed and configured.
- `kubectl` installed and configured.
- Helm installed (for deploying Prometheus and Grafana).

## Step 1: Implement Horizontal Pod Autoscaler (HPA)

### 1.1 Define Metrics and Thresholds for Scaling
Before setting up HPA, ensure that the metrics-server is installed in your cluster as it is required for HPA to retrieve metrics:

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

### 1.2 Set Up HPA for the Frontend Service
You can directly set up autoscaling using the `kubectl autoscale` command, which automatically scales the number of frontend service pods based on CPU utilization:

```bash
kubectl autoscale deployment <deployment-name> --cpu-percent=50 --min=1 --max=10
```

## Step 2: Set Up Monitoring

### 2.1 Install Prometheus and Grafana using Helm
Add the necessary repositories and install Prometheus and Grafana:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

helm install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace
helm install grafana grafana/grafana --namespace monitoring
```

### 2.2 Configure Grafana
1. **Access Grafana**:
   - Port-forward to access the Grafana UI:

   ```bash
   kubectl port-forward service/grafana 3000:80 --namespace monitoring
   ```

   - Visit `http://localhost:3000` in your browser.

2. **Log in to Grafana**:
   - The default username is `admin`.
   - To get the password, run the following command:

   ```bash
   kubectl get secret --namespace monitoring grafana -o jsonpath="{.data.admin-password}" | base64 --decode
   ```

3. **Add Prometheus as a Data Source**:
   - Retrieve the Cluster IP for Prometheus:

   ```bash
   kubectl get svc prometheus-kube-prometheus-prometheus -n monitoring
   ```

   - Note the Cluster IP and use it to configure Prometheus as a data source in Grafana:
     - Navigate to Configuration > Data Sources > Add data source.
     - Select Prometheus and use the URL `http://<ClusterIP>:9090`.

4. **Import Dashboards**:
   - Navigate to Dashboards, click on "Import", and enter the ID 8588 to import a pre-configured dashboard.


## Step 3: Verification

### 3.1 Simulate Load
Use any online load testing tool to generate traffic to the frontend.

### 3.2 Monitor Autoscaling
Monitor the HPA status and observe the number of pods increasing based on the load:

```bash
kubectl get hpa -w
```

### 3.3 Check Monitoring Dashboards
Access the Grafana dashboards to view metrics related to CPU utilization, response times, and other relevant data. Verify that the metrics reflect the simulated load conditions.

## Cleanup Steps

To clean up the resources created during this lab, follow these steps:

1. **Delete HPA resources**:
   ```bash
   kubectl delete hpa <hpa-name>
   ```

2. **Uninstall Prometheus and Grafana**:
   ```bash
   helm uninstall prometheus --namespace monitoring
   helm uninstall grafana --namespace monitoring
   ```
**Follow the cleanup steps from Lab 4 and 5** to delete the Kubernetes cluster and other associated resources.

By following these steps, you have successfully implemented autoscaling and monitoring for your e-commerce application on Amazon EKS. This setup helps ensure that your application can handle varying loads efficiently and provides insights into its performance and health.