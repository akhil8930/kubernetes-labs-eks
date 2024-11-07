# Lab 5: Integrating Amazon RDS with E-commerce Application on Amazon EKS

This guide details the steps to integrate Amazon RDS for managing database operations within an e-commerce application deployed on Amazon EKS. It includes creating an RDS instance, updating the application to interact with the database, and deploying these changes.

## Prerequisites

- E-commerce application set up on Amazon EKS from Lab 4.
- AWS CLI installed and configured.
- `kubectl` installed and configured.
- Docker installed.
- PostgreSQL client installed (for database interaction).

## Step 1: Create an Amazon RDS Instance

### 1.1 Create the RDS Instance with Default VPC
Create the RDS instance in the default VPC to simplify network management. Replace `yourpassword` with a secure password of your choice:

```bash
aws rds create-db-instance --db-instance-identifier ecommerce-db  --db-instance-class db.t3.micro  --engine postgres  --allocated-storage 20  --master-username mydbadmin  --master-user-password yourpassword  --backup-retention-period 0  --no-multi-az  --auto-minor-version-upgrade  --publicly-accessible  --region ap-south-1
```

### 1.2 Retrieve Database Connection Details
Retrieve the database endpoint once the instance is available (DB creation may take 5-10 minutes):

```bash
aws rds describe-db-instances --db-instance-identifier ecommerce-db --query 'DBInstances[*].Endpoint.Address' --output text --region ap-south-1
```

Record the endpoint for application configuration.

## Step 2: Initial Database Setup

### 2.1 Adjust Security Group Rules
Allow your Amazon EKS cluster to communicate with your RDS instance by updating the security group rules to permit inbound traffic on port 5432.

```bash
# Fetch the Security Group ID associated with the RDS instance
sg_id=$(aws rds describe-db-instances  --db-instance-identifier ecommerce-db  --query 'DBInstances[*].VpcSecurityGroups[*].VpcSecurityGroupId'  --output text  --region ap-south-1)
echo "Security Group ID: $sg_id"

# Authorize inbound traffic on port 5432 for the fetched Security Group ID
aws ec2 authorize-security-group-ingress --region ap-south-1  --group-id $sg_id  --protocol tcp  --port 5432  --cidr 0.0.0.0/0  # Adjust this to a more restrictive CIDR block as necessary
```

### 2.2 Create the Necessary Database Table
Connect to the database and create the `cart` table:

1. **Download and Install PostgreSQL Client**:
   - For Windows, download the installer from the [official PostgreSQL download page](https://www.postgresql.org/download/windows/) and follow the installation instructions.

2. **Connect to the Database**:
   ```bash
   psql -h your-db-endpoint -p 5432 -U mydbadmin -d postgres
   ```

3. **Create the Table**:
   ```sql
   CREATE TABLE cart (
       id SERIAL PRIMARY KEY,
       product_id VARCHAR(255) NOT NULL,
       quantity INTEGER NOT NULL
   );
   ```

4. **Verify Table Creation**:
   ```sql
   \dt
   ```

5. **Exit the Database**:
   ```sql
   \q
   ```

## Step 3: Update the Cart Service

### 3.1 Update `cart/requirements.txt`
Add `psycopg2-binary` to manage PostgreSQL database connections:

```
Flask
Flask-Cors
psycopg2-binary
```

### 3.2 Modify `cart/app.py`
Update the `app.py` file to use PostgreSQL for database operations. Ensure environment variables are correctly set to connect to the database.

```python
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )

@app.route('/cart', methods=['GET', 'POST'])
def handle_cart():
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        if request.method == 'POST':
            item = request.json
            product_id = item.get('id')  # Assuming the product object has an 'id' field
            quantity = item.get('quantity', 10.99)

            if not product_id:
                return jsonify([{'error': 'Missing required product ID'}]), 400

            cur.execute('INSERT INTO cart (product_id, quantity) VALUES (%s, %s)', (product_id, quantity))
            conn.commit()
            
            cur.execute('SELECT product_id AS name, quantity AS price FROM cart')  # Adjust these fields as necessary
            items = cur.fetchall()
            return jsonify(items), 201

        elif request.method == 'GET':
            cur.execute('SELECT product_id AS name, quantity AS price FROM cart')
            items = cur.fetchall()
            return jsonify(items)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
```

### 3.3 Update Docker Image
Build and push the updated Docker image:

```bash
cd cart/
docker build -t ecommerce-cart .
docker tag ecommerce-cart <aws_account_id>.dkr.ecr.ap-south-1.amazonaws.com/ecommerce-cart:latest
docker push <aws_account_id>.dkr.ecr.ap-south-1.amazonaws.com/ecommerce-cart:latest
```

## Step 4: Update Application Configuration

### 4.1 Modify Environment Variables in Kubernetes Deployment
Configure the deployment to use the new database settings in `cart-deployment.yaml`. Also, replace `<account_id>` in the manifest file:

```yaml
env:
  - name: DB_HOST
    value: "your-db-endpoint"
  - name: DB_PORT
    value: "5432"
  - name: DB_USER
    value: "mydbadmin"
  - name: DB_PASSWORD
    value: "yourpassword"
  - name: DB_NAME
    value: "postgres"
```

### 4.2 Apply Updated Configurations
Deploy the updated configurations:

```bash
cd ../
kubectl apply -f cart-deployment.yaml
```

## Step 5: Verify Database Integration

### 5.1 Verify Application Functionality
Ensure that the cart service interacts correctly with the RDS instance by performing operations like adding and retrieving items through the application interface.

### 5.2 Verify Database Entries Directly
Connect to the PostgreSQL database and execute SQL queries to verify the contents of the `cart` table.

1. **Connect to the Database**:
   ```bash
   psql -h your-db-endpoint -p 5432 -U mydbadmin -d postgres
   ```

2. **Check the Entry**:
   ```sql
   SELECT * FROM cart;
   ```

3. **Exit the Database**:
   ```sql
   \q
   ```

## Cleanup Steps

To clean up the resources created during this lab, follow these steps:

**Delete the RDS instance**:
   ```bash
   aws rds delete-db-instance --db-instance-identifier ecommerce-db --skip-final-snapshot --region ap-south-1
   ```

**Follow the cleanup steps from Lab 4** to delete the Kubernetes cluster and other associated resources.

By following these steps, you have successfully integrated Amazon RDS with your e-commerce application on Amazon EKS, enhancing the application's scalability and manageability.