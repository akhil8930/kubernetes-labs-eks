# Lab 1: Setting up the Kubernetes Cluster on Amazon EKS

This lab guides you through the process of setting up a Kubernetes cluster using Amazon Elastic Kubernetes Service (EKS). By the end of this lab, you will have a fully functional EKS cluster ready to deploy applications.

## Prerequisites

- AWS Account
- AWS CLI installed and configured
- `kubectl` installed

## Step 1: Install `eksctl`

`eksctl` is a simple CLI tool for creating and managing clusters on EKS. It simplifies many of the complex tasks associated with connecting to the cluster.

```bash
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin
```

## Step 2: Launch EKS Cluster

Use `eksctl` to create an EKS cluster. This tool simplifies the process.

1. Open your terminal.
2. Run the following command to create a cluster:

```bash
eksctl create cluster --name my-ecommerce --region ap-south-1 --nodegroup-name ecommerce-nodes --node-type t3.medium --nodes 2
```

This command sets up an EKS cluster named `my-ecommerce` in the `ap-south-1` region with a node group consisting of 3 nodes of type `t3.medium`.

## Step 3: Configure kubectl

After the cluster is created, `eksctl` automatically configures `kubectl`.

1. Verify the configuration by listing the nodes:

```bash
kubectl get nodes
```

You should see the nodes you just created listed as ready.

## Verification

Ensure that your cluster is up and running:

- Run `kubectl cluster-info`. This should display cluster information and confirm that the Kubernetes master is running.
- Run `kubectl get nodes` again to ensure all nodes are in the `Ready` state.

Congratulations! You have successfully set up an Amazon EKS cluster. You are now ready to deploy applications to your cluster.

## Cleanup

To clean up the resources created during this lab, run:

```bash
eksctl delete cluster --name my-ecommerce --region ap-south-1 
```

This command will delete the EKS cluster and all associated resources, ensuring that you are not charged for resources that you are no longer using.
