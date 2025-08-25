
# JupyterHub, MinIO, MLFlow, ~~Kserve & Keycloak~~ on Kubernetes

A complete deployment setup for running JupyterHub on Kubernetes with PostgreSQL backend, MinIO object storage, MLFlow experiment tracking, MetalLB load balancing, and NGINX ingress controller.

This configuration supports both local development with Minikube and production bare-metal deployments.

## 🏗️ Architecture

This setup includes:
- **JupyterHub**: Multi-user Jupyter notebook server
- **MinIO**: S3-compatible object storage for artifacts and data
- **MLFlow**: Machine learning experiment tracking and model registry
- **PostgreSQL**: Persistent database backend for JupyterHub and MLFlow
- **NGINX Ingress Controller**: HTTP/HTTPS routing and load balancing
- **MetalLB**: Load balancer implementation for bare-metal Kubernetes clusters

## 📁 Repository Structure

```
├── configs/
│   ├── jupyter-values.yaml         # JupyterHub Helm configuration
│   ├── minio-values.yaml          # MinIO storage configuration
│   ├── mlflow-values.yaml         # MLFlow tracking server configuration
│   └── postgresql-values.yaml     # PostgreSQL database configuration
├── jobs/
│   ├── create-mlflow-bucket.yaml  # MinIO bucket setup for MLFlow
│   └── create-mlflow-db.yaml      # Database initialization for MLFlow
├── metallb-helm-config/
│   ├── metallb-config.yaml        # MetalLB IP pool configuration
│   └── values.yaml               # MetalLB Helm values
├── sample-scripts/
│   ├── jupyter-minio-integration.ipynb
│   └── jupyter-minio-mlflow-integration.ipynb
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Kubernetes cluster (Minikube for local development)
- Helm 3.x installed
- kubectl configured to access your cluster

---

## 📦 Installation Steps

### 1. Add Required Helm Repositories

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo add jupyterhub https://jupyterhub.github.io/helm-chart/
helm repo add metallb https://metallb.github.io/metallb
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add minio https://charts.min.io/
helm repo add community-charts https://community-charts.github.io/helm-charts
helm repo add clearml https://clearml.github.io/clearml-helm-charts
helm repo update

```

### 2. Install NGINX Ingress Controller

```bash
# Install NGINX Ingress Controller
helm install ingress-nginx ingress-nginx/ingress-nginx

# Optional: Download chart for customization
helm pull ingress-nginx/ingress-nginx --untar
```

### 3. Setup MetalLB Load Balancer

```bash
# Create dedicated namespace
kubectl create namespace metallb-system

# Install MetalLB
helm install metallb metallb/metallb \
  --namespace metallb-system \
  -f metallb-helm-config/values.yaml

# Configure IP address pool
kubectl apply -f metallb-helm-config/metallb-config.yaml
```

### 4. Install PostgreSQL Database

```bash
# Install PostgreSQL with custom configuration
helm install postgresql bitnami/postgresql \
  --namespace jupyter \
  --create-namespace \
  -f configs/postgresql-values.yaml
```

### 5. Install JupyterHub

```bash
# Install JupyterHub with PostgreSQL backend
helm upgrade --install jupyter jupyterhub/jupyterhub \
  --namespace jupyter \
  --create-namespace \
  -f configs/jupyter-values.yaml

# Optional: Download chart for reference
helm pull jupyterhub/jupyterhub --untar
```

### 6. Install MinIO Object Storage

```bash
# Install MinIO with custom configuration
helm install minio minio/minio \
  --namespace minio \
  --create-namespace \
  -f configs/minio-values.yaml
```

### 7. Install MLFlow Tracking Server

```bash
# Create MLFlow bucket and database
kubectl apply -f jobs/create-mlflow-bucket.yaml
kubectl apply -f jobs/create-mlflow-db.yaml

# Install MLFlow tracking server
helm upgrade --install mlflow community-charts/mlflow \
  --namespace mlflow \
  --create-namespace \
  --values configs/mlflow-values.yaml
```

### 7. Install ClearML Server
```
helm upgrade --install clearml clearml/clearml  -n clearml --create-namespace -f clearml-values_bak.yaml 
```

### 8. Run a test
- Create a Bucket in MinIO
- Create a Key/secret pair in MinIO
- Create a key secret pair in ClearML
- Copy the credentials in the "ClearML Integreation notebook" jupyter notebook
- See results in clearML

---

## 🔧 Configuration Details

### JupyterHub Configuration
The `configs/jupyter-values.yaml` file contains:
- PostgreSQL database connection settings
- Ingress configuration for `jupyter.local`
- Security contexts optimized for Minikube
- Single-user notebook server configuration
- Resource limits and requests

### MinIO Configuration
The `configs/minio-values.yaml` includes:
- S3-compatible API configuration
- Console access settings
- Ingress routing for `minio.local` and `minio-console.local`
- Storage persistence settings

### MLFlow Configuration
The `configs/mlflow-values.yaml` contains:
- MinIO backend storage configuration
- PostgreSQL metadata store connection
- Ingress configuration for experiment tracking UI
- Authentication and authorization settings

### PostgreSQL Configuration
The `configs/postgresql-values.yaml` includes:
- Minikube-specific permission fixes
- Volume permissions configuration
- Database initialization scripts

### MetalLB Configuration
The `metallb-helm-config/` directory contains:
- IP address pool configuration for load balancer services
- LoadBalancer service type settings

---

## 🌐 Access Services

### Local Development (Minikube)

1. **Configure local DNS** - Add to your `/etc/hosts` file:
   ```
   <CLUSTER_IP> jupyter.local minio.local minio-console.local mlflow.local
   ```

2. **Service URLs**:
  |   Service       | URL                        |
  |-----------------|----------------------------|
  | JupyterHub      | http://jupyter.local       |
  | MinIO Console   | http://minio-console.local |
  | MinIO API       | http://minio.local         |
  | MLFlow UI       | http://mlflow.local        |

### Production Access

For production deployments, update the ingress configurations in the values files to use your actual domain names and configure proper TLS certificates.

---

## 🛠️ Useful Commands

### Monitoring and Debugging

```bash
# View JupyterHub logs
kubectl logs -f deployment/hub -n jupyter

# View MinIO logs
kubectl logs -f deployment/minio -n minio

# View MLFlow logs
kubectl logs -f deployment/mlflow -n mlflow

# View PostgreSQL logs
kubectl logs -f postgresql-0 -n jupyter

# Restart services
kubectl rollout restart deployment/hub -n jupyter
kubectl rollout restart deployment/minio -n minio
kubectl rollout restart deployment/mlflow -n mlflow
```

### Database Operations

```bash
# Test PostgreSQL connection
kubectl run postgresql-client --rm --tty -i --restart='Never' \
  --namespace jupyter \
  --image docker.io/bitnami/postgresql:15 \
  --env="PGPASSWORD=yourpassword" \
  --command -- psql --host postgresql --port 5432 -U postgres -d jupyterhub
```

### Service Status

```bash
# Check all deployments
kubectl get deployments --all-namespaces

# Check ingress resources
kubectl get ingress --all-namespaces

# Check services and endpoints
kubectl get svc,endpoints --all-namespaces
```

---

## 🔄 Maintenance & Upgrades

### Upgrade JupyterHub

```bash
helm repo update
helm upgrade jupyter jupyterhub/jupyterhub \
  --namespace jupyter \
  -f configs/jupyter-values.yaml
```

### Upgrade MinIO

```bash
helm repo update
helm upgrade minio minio/minio \
  --namespace minio \
  -f configs/minio-values.yaml
```

### Upgrade MLFlow

```bash
helm repo update
helm upgrade mlflow community-charts/mlflow \
  --namespace mlflow \
  --values configs/mlflow-values.yaml
```

### Upgrade PostgreSQL

```bash
helm repo update
helm upgrade postgresql bitnami/postgresql \
  --namespace jupyter \
  -f configs/postgresql-values.yaml
```

---

## 📚 References

- [JupyterHub Documentation](https://jupyterhub.readthedocs.io/)
- [JupyterHub Helm Chart](https://jupyterhub.github.io/helm-chart/)
- [MinIO Documentation](https://min.io/docs/)
- [MLFlow Documentation](https://mlflow.org/docs/latest/index.html)
- [PostgreSQL Bitnami Chart](https://github.com/bitnami/charts/tree/main/bitnami/postgresql)
- [MetalLB Documentation](https://metallb.universe.tf/)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)