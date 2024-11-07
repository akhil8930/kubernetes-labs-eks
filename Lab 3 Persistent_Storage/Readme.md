# Lab 3: Integrating Persistent Storage with EKS Using Dynamic Provisioning

## Objective
Learn how to use dynamic persistent storage with Kubernetes on Amazon EKS by leveraging Amazon Elastic Block Store (EBS) with the help of the AWS EBS CSI driver. This lab will guide you through the process of setting up a Storage Class and a Persistent Volume Claim (PVC) to dynamically provision storage resources.

## Prerequisites
- A running EKS cluster.
- `kubectl` configured to communicate with your cluster.
- Basic understanding of Kubernetes objects like Pods, Deployments, and Services.
- AWS CLI installed and configured with appropriate permissions.

## What is a Persistent Volume?
A Persistent Volume (PV) in Kubernetes is a cluster-wide resource that you use to manage durable storage. PVs abstract the details of how storage is provided and how it's consumed. In this lab, you'll use Amazon EBS volumes as the underlying storage for PVs, which are dynamically provisioned through a Persistent Volume Claim (PVC).

## Detailed Steps

### Preliminary Step: Update IAM Role for Worker Nodes
Before installing the AWS EBS CSI driver, ensure that the IAM role associated with your EKS worker nodes has the necessary permissions to manage EBS volumes.

#### Using Bash (Linux/macOS):
```bash
role_arn=$(aws eks describe-nodegroup --cluster-name <your-eks-cluster> --nodegroup-name <your-nodegroup-name> --region <your-region> --query "nodegroup.nodeRole" --output text)
node_role=${role_arn##*/}
aws iam attach-role-policy --role-name $node_role --policy-arn arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy
```

#### Using PowerShell (Windows):
```powershell
$role_arn = aws eks describe-nodegroup --cluster-name <your-eks-cluster> --nodegroup-name <your-nodegroup-name> --region <your-region> --query "nodegroup.nodeRole" --output text
$node_role = $role_arn -replace 'arn:aws:iam::[0-9]+:role/', ''
aws iam attach-role-policy --role-name $node_role --policy-arn arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy
```

### Step 1: Install the AWS EBS CSI Driver Using EKS Add-ons
```bash
aws eks create-addon --cluster-name <your-eks-cluster> --addon-name aws-ebs-csi-driver --resolve-conflicts OVERWRITE --region <your-region>
```

### Step 2: Create a Kubernetes Storage Class
Create a file named `ebs-sc.yaml` with the following content:
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ebs-sc
provisioner: ebs.csi.aws.com
parameters:
  type: gp2
  fsType: ext4
reclaimPolicy: Retain
allowVolumeExpansion: true
```
Apply the Storage Class:
```bash
kubectl apply -f ebs-sc.yaml
```

### Step 3: Create a Persistent Volume Claim (PVC)
Create a file named `ebs-pvc.yaml` with the following content:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ebs-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: ebs-sc
  resources:
    requests:
      storage: 4Gi
```
Apply the PVC:
```bash
kubectl apply -f ebs-pvc.yaml
```

### Step 4: Verify the PVC
Check the PVC Status:
```bash
kubectl get pvc
```
The status should be "Bound", indicating that the EBS volume has been successfully provisioned and is ready for use.

### Cleanup Steps
To clean up the resources created during this lab, follow these steps:
```bash
kubectl delete pvc ebs-pvc
kubectl delete sc ebs-sc
aws eks delete-addon --cluster-name <your-eks-cluster> --addon-name aws-ebs-csi-driver --region <your-region>
```

This README provides a comprehensive guide to integrating dynamic persistent storage with Amazon EKS, focusing on the practical application of Persistent Volumes and Persistent Volume Claims.